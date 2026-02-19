package main

import (
	"encoding/json"
	"flag"
	"net/http"
	"os"
	"time"

	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
)

var (
	port            = flag.String("port", "8000", "Port to listen on")
	bufferSize      = flag.Int("buffer", 200, "Frame buffer size")
	debug           = flag.Bool("debug", false, "Enable debug logging")
	enableWebRTC    = flag.Bool("webrtc", true, "Enable WebRTC support (default: true)")
	enableWebSocket = flag.Bool("websocket", true, "Enable WebSocket support (default: true)")
	enableIPC       = flag.Bool("ipc", true, "Enable IPC (Unix Socket/Named Pipe) (default: true)")
)

func main() {
	flag.Parse()

	// Configurar logger
	zerolog.TimeFieldFormat = zerolog.TimeFormatUnix
	if *debug {
		zerolog.SetGlobalLevel(zerolog.DebugLevel)
	} else {
		zerolog.SetGlobalLevel(zerolog.InfoLevel)
	}
	log.Logger = log.Output(zerolog.ConsoleWriter{Out: os.Stderr, TimeFormat: time.RFC3339})

	log.Info().
		Str("port", *port).
		Int("buffer_size", *bufferSize).
		Bool("debug", *debug).
		Bool("webrtc_enabled", *enableWebRTC).
		Bool("websocket_enabled", *enableWebSocket).
		Bool("ipc_enabled", *enableIPC).
		Msg("Starting GTA Analytics Gateway (WebSocket + WebRTC + IPC)")

	// Criar handlers
	var wsHandler *WebSocketHandler
	var webrtcHandler *WebRTCHandler

	if *enableWebSocket {
		wsHandler = NewWebSocketHandler(*bufferSize)
		go wsHandler.Run()
		log.Info().Msg("WebSocket support enabled")
	}

	if *enableWebRTC {
		webrtcHandler = NewWebRTCHandler(*bufferSize)
		log.Info().Msg("WebRTC support enabled")
	}

	// Use shared buffer between transports
	// Priority: WebSocket > WebRTC (if both enabled, WebSocket buffer is primary)
	var primaryHandler interface{}
	if *enableWebSocket {
		primaryHandler = wsHandler
	} else if *enableWebRTC {
		primaryHandler = webrtcHandler
	}

	// Create HTTP router
	mux := http.NewServeMux()

	// Configurar rotas
	if *enableWebSocket {
		mux.HandleFunc("/ws", wsHandler.HandleWebSocket)
		mux.HandleFunc("/stats", statsHandler(wsHandler))
		mux.HandleFunc("/frames", framesHandler(wsHandler))
	}

	if *enableWebRTC {
		mux.HandleFunc("/offer", webrtcHandler.HandleOffer)
		if !*enableWebSocket {
			// Se WebSocket desabilitado, usar buffer do WebRTC para /frames e /stats
			mux.HandleFunc("/stats", statsHandlerWebRTC(webrtcHandler))
			mux.HandleFunc("/frames", framesHandlerWebRTC(webrtcHandler))
		}
	}

	mux.HandleFunc("/health", healthHandler)

	// HTTP upload endpoint for OBS Browser Source
	if *enableWebSocket {
		mux.HandleFunc("/upload", uploadHandler(wsHandler))
	} else if *enableWebRTC {
		mux.HandleFunc("/upload", uploadHandlerWebRTC(webrtcHandler))
	}

	// Start IPC server (Unix Socket / Named Pipe)
	if *enableIPC && primaryHandler != nil {
		ipcServer, err := NewIPCServer()
		if err != nil {
			log.Error().Err(err).Msg("Failed to create IPC server, continuing without it")
		} else {
			go func() {
				log.Info().Str("path", ipcServer.GetPath()).Msg("IPC server started")
				if err := ipcServer.Serve(mux); err != nil {
					log.Error().Err(err).Msg("IPC server error")
				}
			}()
		}
	}

	// Start HTTP server
	addr := ":" + *port
	log.Info().Str("addr", addr).Msg("HTTP server started")

	if err := http.ListenAndServe(addr, mux); err != nil {
		log.Fatal().Err(err).Msg("HTTP server failed")
	}
}

// healthHandler responde com status de saúde do servidor
func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":    "healthy",
		"timestamp": time.Now().Unix(),
	})
}

// statsHandler retorna estatísticas do sistema
func statsHandler(wsHandler *WebSocketHandler) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("Access-Control-Allow-Origin", "*")

		stats := wsHandler.GetStats()
		uptime := time.Since(stats.StartTime).Seconds()

		response := map[string]interface{}{
			"frames_received":     stats.FramesReceived,
			"frames_processed":    stats.FramesProcessed,
			"frames_dropped":      stats.FramesDropped,
			"active_connections":  stats.ActiveConnections,
			"buffer_usage":        stats.BufferUsage,
			"uptime_seconds":      uptime,
			"frames_per_second":   float64(stats.FramesReceived) / uptime,
			"drop_rate":           float64(stats.FramesDropped) / float64(stats.FramesReceived) * 100,
		}

		json.NewEncoder(w).Encode(response)
	}
}

// framesHandler retorna frames do buffer (para Python backend)
func framesHandler(wsHandler *WebSocketHandler) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("Access-Control-Allow-Origin", "*")

		if r.Method != http.MethodGet {
			w.WriteHeader(http.StatusMethodNotAllowed)
			return
		}

		// Pegar batch de frames (máximo 10 por vez)
		frames := wsHandler.GetBuffer().PopBatch(10)

		if len(frames) == 0 {
			w.WriteHeader(http.StatusNoContent)
			return
		}

		// Converter frames para JSON
		frameList := make([]map[string]interface{}, len(frames))
		for i, frame := range frames {
			frameList[i] = map[string]interface{}{
				"data":        string(frame.Data),
				"timestamp":   frame.Timestamp,
				"number":      frame.Number,
				"received_at": frame.ReceivedAt.Unix(),
			}
		}

		response := map[string]interface{}{
			"frames": frameList,
			"count":  len(frames),
		}

		json.NewEncoder(w).Encode(response)
	}
}

// framesHandlerWebRTC retorna frames do buffer WebRTC (para Python backend)
func framesHandlerWebRTC(webrtcHandler *WebRTCHandler) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("Access-Control-Allow-Origin", "*")

		if r.Method != http.MethodGet {
			w.WriteHeader(http.StatusMethodNotAllowed)
			return
		}

		// Pegar batch de frames (máximo 10 por vez)
		frames := webrtcHandler.GetBuffer().PopBatch(10)

		if len(frames) == 0 {
			w.WriteHeader(http.StatusNoContent)
			return
		}

		// Converter frames para JSON
		frameList := make([]map[string]interface{}, len(frames))
		for i, frame := range frames {
			frameList[i] = map[string]interface{}{
				"data":        string(frame.Data),
				"timestamp":   frame.Timestamp,
				"number":      frame.Number,
				"received_at": frame.ReceivedAt.Unix(),
			}
		}

		response := map[string]interface{}{
			"frames": frameList,
			"count":  len(frames),
		}

		json.NewEncoder(w).Encode(response)
	}
}

// statsHandlerWebRTC retorna estatísticas do sistema WebRTC
func statsHandlerWebRTC(webrtcHandler *WebRTCHandler) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("Access-Control-Allow-Origin", "*")

		stats := webrtcHandler.GetStats()
		uptime := time.Since(stats.StartTime).Seconds()

		response := map[string]interface{}{
			"frames_received":     stats.FramesReceived,
			"frames_processed":    stats.FramesProcessed,
			"frames_dropped":      stats.FramesDropped,
			"active_connections":  stats.ActiveConnections,
			"buffer_usage":        stats.BufferUsage,
			"uptime_seconds":      uptime,
			"frames_per_second":   float64(stats.FramesReceived) / uptime,
			"drop_rate":           float64(stats.FramesDropped) / float64(stats.FramesReceived) * 100,
			"transport":           "webrtc",
		}

		json.NewEncoder(w).Encode(response)
	}
}
