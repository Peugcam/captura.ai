package main

import (
	b64 "encoding/base64"
	"encoding/json"
	"io"
	"net/http"
	"time"

	"github.com/rs/zerolog/log"
)

// uploadHandler aceita uploads HTTP de frames (para OBS Browser Source)
func uploadHandler(wsHandler *WebSocketHandler) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")

		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusOK)
			return
		}

		if r.Method != http.MethodPost {
			w.WriteHeader(http.StatusMethodNotAllowed)
			return
		}

		// Parse multipart form
		err := r.ParseMultipartForm(10 << 20) // 10 MB max
		if err != nil {
			log.Error().Err(err).Msg("Failed to parse multipart form")
			http.Error(w, "Failed to parse form", http.StatusBadRequest)
			return
		}

		file, _, err := r.FormFile("file")
		if err != nil {
			log.Error().Err(err).Msg("Failed to get file from form")
			http.Error(w, "Failed to get file", http.StatusBadRequest)
			return
		}
		defer file.Close()

		// Read file data
		fileBytes, err := io.ReadAll(file)
		if err != nil {
			log.Error().Err(err).Msg("Failed to read file")
			http.Error(w, "Failed to read file", http.StatusInternalServerError)
			return
		}

		// Convert to base64
		base64Data := b64.StdEncoding.EncodeToString(fileBytes)

		// Add to buffer
		frame := Frame{
			Data:       []byte(base64Data),
			Timestamp:  time.Now().UnixMilli(),
			ReceivedAt: time.Now(),
		}

		if wsHandler.GetBuffer().Push(frame) {
			log.Info().Int("size_kb", len(fileBytes)/1024).Msg("Frame uploaded via HTTP")
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(map[string]interface{}{
				"success": true,
				"message": "Frame uploaded successfully",
			})
		} else {
			log.Warn().Msg("Buffer full, frame dropped")
			w.WriteHeader(http.StatusServiceUnavailable)
			json.NewEncoder(w).Encode(map[string]interface{}{
				"success": false,
				"message": "Buffer full",
			})
		}
	}
}

// uploadHandlerWebRTC aceita uploads HTTP de frames para buffer WebRTC
func uploadHandlerWebRTC(webrtcHandler *WebRTCHandler) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")

		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusOK)
			return
		}

		if r.Method != http.MethodPost {
			w.WriteHeader(http.StatusMethodNotAllowed)
			return
		}

		// Parse multipart form
		err := r.ParseMultipartForm(10 << 20) // 10 MB max
		if err != nil {
			log.Error().Err(err).Msg("Failed to parse multipart form")
			http.Error(w, "Failed to parse form", http.StatusBadRequest)
			return
		}

		file, _, err := r.FormFile("file")
		if err != nil {
			log.Error().Err(err).Msg("Failed to get file from form")
			http.Error(w, "Failed to get file", http.StatusBadRequest)
			return
		}
		defer file.Close()

		// Read file data
		fileBytes, err := io.ReadAll(file)
		if err != nil {
			log.Error().Err(err).Msg("Failed to read file")
			http.Error(w, "Failed to read file", http.StatusInternalServerError)
			return
		}

		// Convert to base64
		base64Data := b64.StdEncoding.EncodeToString(fileBytes)

		// Add to buffer
		frame := Frame{
			Data:       []byte(base64Data),
			Timestamp:  time.Now().UnixMilli(),
			ReceivedAt: time.Now(),
		}

		if webrtcHandler.GetBuffer().Push(frame) {
			log.Info().Int("size_kb", len(fileBytes)/1024).Msg("Frame uploaded via HTTP (WebRTC buffer)")
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(map[string]interface{}{
				"success": true,
				"message": "Frame uploaded successfully",
			})
		} else {
			log.Warn().Msg("Buffer full, frame dropped")
			w.WriteHeader(http.StatusServiceUnavailable)
			json.NewEncoder(w).Encode(map[string]interface{}{
				"success": false,
				"message": "Buffer full",
			})
		}
	}
}
