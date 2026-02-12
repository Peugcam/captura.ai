package main

import (
	"encoding/base64"
	"encoding/json"
	"io"
	"net/http"
	"sync/atomic"
	"time"

	"github.com/pion/webrtc/v3"
	"github.com/rs/zerolog/log"
)

// WebRTCHandler gerencia conexões WebRTC
type WebRTCHandler struct {
	buffer       *RingBuffer
	frameCounter int64
	stats        *Stats
	config       webrtc.Configuration
}

// NewWebRTCHandler cria um novo handler WebRTC
func NewWebRTCHandler(bufferSize int) *WebRTCHandler {
	// Configuração WebRTC com STUN servers públicos
	config := webrtc.Configuration{
		ICEServers: []webrtc.ICEServer{
			{
				URLs: []string{
					"stun:stun.l.google.com:19302",
					"stun:stun1.l.google.com:19302",
				},
			},
		},
	}

	return &WebRTCHandler{
		buffer: NewRingBuffer(bufferSize),
		stats: &Stats{
			StartTime: time.Now(),
		},
		config: config,
	}
}

// SDPRequest representa uma requisição de SDP offer
type SDPRequest struct {
	SDP  string `json:"sdp"`
	Type string `json:"type"`
}

// SDPResponse representa uma resposta com SDP answer
type SDPResponse struct {
	SDP  string `json:"sdp"`
	Type string `json:"type"`
}

// HandleOffer lida com SDP offers e retorna SDP answer
func (h *WebRTCHandler) HandleOffer(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type")

	// Handle CORS preflight
	if r.Method == http.MethodOptions {
		w.WriteHeader(http.StatusOK)
		return
	}

	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Parse SDP offer
	body, err := io.ReadAll(r.Body)
	if err != nil {
		log.Error().Err(err).Msg("Failed to read request body")
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	var sdpReq SDPRequest
	if err := json.Unmarshal(body, &sdpReq); err != nil {
		log.Error().Err(err).Msg("Failed to parse SDP offer")
		http.Error(w, "Invalid SDP offer", http.StatusBadRequest)
		return
	}

	// Create new PeerConnection
	peerConnection, err := webrtc.NewPeerConnection(h.config)
	if err != nil {
		log.Error().Err(err).Msg("Failed to create PeerConnection")
		http.Error(w, "Internal error", http.StatusInternalServerError)
		return
	}

	// Handle ICE connection state changes
	peerConnection.OnICEConnectionStateChange(func(connectionState webrtc.ICEConnectionState) {
		log.Info().
			Str("state", connectionState.String()).
			Msg("ICE Connection State changed")

		if connectionState == webrtc.ICEConnectionStateDisconnected ||
			connectionState == webrtc.ICEConnectionStateFailed ||
			connectionState == webrtc.ICEConnectionStateClosed {
			if err := peerConnection.Close(); err != nil {
				log.Error().Err(err).Msg("Failed to close PeerConnection")
			}
			atomic.AddInt32(&h.stats.ActiveConnections, -1)
		}
	})

	// Setup DataChannel handler
	peerConnection.OnDataChannel(func(d *webrtc.DataChannel) {
		log.Info().
			Str("label", d.Label()).
			Msg("DataChannel opened")

		atomic.AddInt32(&h.stats.ActiveConnections, 1)

		// Handle DataChannel messages (binary frames)
		d.OnMessage(func(msg webrtc.DataChannelMessage) {
			h.handleDataChannelMessage(msg)
		})

		d.OnClose(func() {
			log.Info().
				Str("label", d.Label()).
				Msg("DataChannel closed")
		})
	})

	// Set remote description (offer)
	offer := webrtc.SessionDescription{
		Type: webrtc.SDPTypeOffer,
		SDP:  sdpReq.SDP,
	}

	if err := peerConnection.SetRemoteDescription(offer); err != nil {
		log.Error().Err(err).Msg("Failed to set remote description")
		http.Error(w, "Invalid offer", http.StatusBadRequest)
		return
	}

	// Create answer
	answer, err := peerConnection.CreateAnswer(nil)
	if err != nil {
		log.Error().Err(err).Msg("Failed to create answer")
		http.Error(w, "Failed to create answer", http.StatusInternalServerError)
		return
	}

	// Set local description (answer)
	if err := peerConnection.SetLocalDescription(answer); err != nil {
		log.Error().Err(err).Msg("Failed to set local description")
		http.Error(w, "Failed to set local description", http.StatusInternalServerError)
		return
	}

	// Send answer back to client
	sdpResp := SDPResponse{
		SDP:  answer.SDP,
		Type: answer.Type.String(),
	}

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(sdpResp)

	log.Info().Msg("WebRTC negotiation completed successfully")
}

// handleDataChannelMessage processa mensagens do DataChannel
func (h *WebRTCHandler) handleDataChannelMessage(msg webrtc.DataChannelMessage) {
	if msg.IsString {
		// String message (JSON control messages)
		h.handleJSONMessage(msg.Data)
	} else {
		// Binary message (raw JPEG frame)
		h.handleBinaryFrame(msg.Data)
	}
}

// handleJSONMessage processa mensagens JSON de controle
func (h *WebRTCHandler) handleJSONMessage(data []byte) {
	var msg map[string]interface{}
	if err := json.Unmarshal(data, &msg); err != nil {
		log.Error().Err(err).Msg("Failed to parse JSON message")
		return
	}

	msgType, ok := msg["type"].(string)
	if !ok {
		return
	}

	switch msgType {
	case "start_capture":
		log.Info().Msg("WebRTC: Capture started")
	case "stop_capture":
		log.Info().Msg("WebRTC: Capture stopped")
	case "frame_base64":
		// Legacy: base64-encoded frame in JSON
		frameData, ok := msg["data"].(string)
		if !ok {
			return
		}
		decoded, err := base64.StdEncoding.DecodeString(frameData)
		if err != nil {
			log.Error().Err(err).Msg("Failed to decode base64 frame")
			return
		}
		h.handleBinaryFrame(decoded)
	default:
		log.Warn().Str("type", msgType).Msg("Unknown WebRTC message type")
	}
}

// handleBinaryFrame processa um frame binário (raw JPEG)
func (h *WebRTCHandler) handleBinaryFrame(data []byte) {
	// Criar frame
	frameNumber := atomic.AddInt64(&h.frameCounter, 1)
	frame := Frame{
		Data:       data, // Raw JPEG bytes (no base64 encoding!)
		Timestamp:  time.Now().UnixMilli(),
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
				Int("frame_size_kb", len(data)/1024).
				Msg("Frame dropped (buffer full)")
		} else {
			log.Debug().
				Int("frame", int(frameNumber)).
				Int("buffer_size", h.buffer.Len()).
				Int("frame_size_kb", len(data)/1024).
				Msg("WebRTC frame received")
		}
	}

	// Atualizar stats de buffer
	bufferStats := h.buffer.Stats()
	h.stats.BufferUsage = bufferStats["usage_percent"].(float64)
}

// GetStats retorna estatísticas atuais
func (h *WebRTCHandler) GetStats() *Stats {
	stats := *h.stats
	stats.BufferUsage = h.buffer.Stats()["usage_percent"].(float64)
	return &stats
}

// GetBuffer retorna o buffer de frames
func (h *WebRTCHandler) GetBuffer() *RingBuffer {
	return h.buffer
}
