package main

import (
	"encoding/json"
	"net/http"
	"sync/atomic"
	"time"

	"github.com/gorilla/websocket"
	"github.com/rs/zerolog/log"
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024 * 64,  // 64KB read buffer
	WriteBufferSize: 1024 * 64,  // 64KB write buffer
	CheckOrigin: func(r *http.Request) bool {
		return true // Permitir todas as origens (ajustar em produção)
	},
}

// WebSocketHandler gerencia conexões WebSocket
type WebSocketHandler struct {
	buffer       *RingBuffer
	connections  map[*websocket.Conn]bool
	register     chan *websocket.Conn
	unregister   chan *websocket.Conn
	frameCounter int64
	stats        *Stats
}

// Stats guarda estatísticas do sistema
type Stats struct {
	FramesReceived    int64     `json:"frames_received"`
	FramesProcessed   int64     `json:"frames_processed"`
	FramesDropped     int64     `json:"frames_dropped"`
	ActiveConnections int32     `json:"active_connections"`
	BufferUsage       float64   `json:"buffer_usage"`
	StartTime         time.Time `json:"start_time"`
}

// NewWebSocketHandler cria um novo handler WebSocket
func NewWebSocketHandler(bufferSize int) *WebSocketHandler {
	return &WebSocketHandler{
		buffer:      NewRingBuffer(bufferSize),
		connections: make(map[*websocket.Conn]bool),
		register:    make(chan *websocket.Conn),
		unregister:  make(chan *websocket.Conn),
		stats: &Stats{
			StartTime: time.Now(),
		},
	}
}

// Run inicia o gerenciador de conexões
func (h *WebSocketHandler) Run() {
	for {
		select {
		case conn := <-h.register:
			h.connections[conn] = true
			atomic.AddInt32(&h.stats.ActiveConnections, 1)
			log.Info().
				Int("active_connections", int(h.stats.ActiveConnections)).
				Msg("Client connected")

		case conn := <-h.unregister:
			if _, ok := h.connections[conn]; ok {
				delete(h.connections, conn)
				conn.Close()
				atomic.AddInt32(&h.stats.ActiveConnections, -1)
				log.Info().
					Int("active_connections", int(h.stats.ActiveConnections)).
					Msg("Client disconnected")
			}
		}
	}
}

// HandleWebSocket lida com conexões WebSocket individuais
func (h *WebSocketHandler) HandleWebSocket(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Error().Err(err).Msg("Failed to upgrade connection")
		return
	}

	h.register <- conn

	defer func() {
		h.unregister <- conn
	}()

	// Configurar timeouts
	conn.SetReadDeadline(time.Now().Add(60 * time.Second))
	conn.SetPongHandler(func(string) error {
		conn.SetReadDeadline(time.Now().Add(60 * time.Second))
		return nil
	})

	// Iniciar goroutine para enviar pings
	go h.pingClient(conn)

	// Loop de leitura de mensagens
	for {
		messageType, message, err := conn.ReadMessage()
		if err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
				log.Error().Err(err).Msg("WebSocket error")
			}
			break
		}

		// Processar mensagem
		if err := h.handleMessage(conn, messageType, message); err != nil {
			log.Error().Err(err).Msg("Failed to handle message")
		}
	}
}

// handleMessage processa uma mensagem recebida
func (h *WebSocketHandler) handleMessage(conn *websocket.Conn, messageType int, message []byte) error {
	// Parsear mensagem JSON
	var msg map[string]interface{}
	if err := json.Unmarshal(message, &msg); err != nil {
		return err
	}

	msgType, ok := msg["type"].(string)
	if !ok {
		return nil
	}

	switch msgType {
	case "frame":
		return h.handleFrame(msg)
	case "start_capture":
		log.Info().Msg("Capture started")
		h.sendAck(conn, "capture_started")
	case "stop_capture":
		log.Info().Msg("Capture stopped")
		h.sendAck(conn, "capture_stopped")
	default:
		log.Warn().Str("type", msgType).Msg("Unknown message type")
	}

	return nil
}

// handleFrame processa um frame recebido
func (h *WebSocketHandler) handleFrame(msg map[string]interface{}) error {
	// Extrair dados do frame
	frameData, ok := msg["data"].(string)
	if !ok {
		return nil
	}

	timestamp, _ := msg["timestamp"].(float64)

	// Criar frame
	frameNumber := atomic.AddInt64(&h.frameCounter, 1)
	frame := Frame{
		Data:       []byte(frameData),
		Timestamp:  int64(timestamp),
		Number:     int(frameNumber),
		ReceivedAt: time.Now(),
	}

	// Adicionar ao buffer
	wasFull := h.buffer.IsFull()
	success := h.buffer.Push(frame)

	atomic.AddInt64(&h.stats.FramesReceived, 1)

	if success {
		if wasFull {
			atomic.AddInt64(&h.stats.FramesDropped, 1)
			log.Warn().
				Int("frame", int(frameNumber)).
				Int("buffer_size", h.buffer.Len()).
				Msg("Frame dropped (buffer full)")
		} else {
			log.Debug().
				Int("frame", int(frameNumber)).
				Int("buffer_size", h.buffer.Len()).
				Msg("Frame received")
		}
	}

	// Atualizar stats de buffer
	bufferStats := h.buffer.Stats()
	h.stats.BufferUsage = bufferStats["usage_percent"].(float64)

	return nil
}

// sendAck envia uma mensagem de acknowledgment
func (h *WebSocketHandler) sendAck(conn *websocket.Conn, message string) error {
	response := map[string]string{
		"type":    "ack",
		"message": message,
	}
	return conn.WriteJSON(response)
}

// pingClient envia pings periódicos para manter a conexão viva
func (h *WebSocketHandler) pingClient(conn *websocket.Conn) {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for range ticker.C {
		if err := conn.WriteMessage(websocket.PingMessage, nil); err != nil {
			return
		}
	}
}

// GetStats retorna estatísticas atuais
func (h *WebSocketHandler) GetStats() *Stats {
	stats := *h.stats
	stats.BufferUsage = h.buffer.Stats()["usage_percent"].(float64)
	return &stats
}

// GetBuffer retorna o buffer de frames
func (h *WebSocketHandler) GetBuffer() *RingBuffer {
	return h.buffer
}
