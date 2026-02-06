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
	port       = flag.String("port", "8000", "Port to listen on")
	bufferSize = flag.Int("buffer", 200, "Frame buffer size")
	debug      = flag.Bool("debug", false, "Enable debug logging")
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
		Msg("Starting GTA Analytics WebSocket Gateway")

	// Criar handler WebSocket
	wsHandler := NewWebSocketHandler(*bufferSize)

	// Iniciar gerenciador de conexões
	go wsHandler.Run()

	// Configurar rotas
	http.HandleFunc("/ws", wsHandler.HandleWebSocket)
	http.HandleFunc("/health", healthHandler)
	http.HandleFunc("/stats", statsHandler(wsHandler))
	http.HandleFunc("/frames", framesHandler(wsHandler))

	// Iniciar servidor
	addr := ":" + *port
	log.Info().Str("addr", addr).Msg("Server started")

	if err := http.ListenAndServe(addr, nil); err != nil {
		log.Fatal().Err(err).Msg("Server failed")
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
