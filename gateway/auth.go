package main

import (
	"crypto/subtle"
	"net/http"
	"os"

	"github.com/rs/zerolog/log"
)

// internalToken é lido do ambiente. Compartilhado com o backend (INTERNAL_API_TOKEN).
// Vazio => autenticação desabilitada (apenas para desenvolvimento local).
var internalToken = os.Getenv("INTERNAL_API_TOKEN")

func init() {
	if internalToken == "" {
		log.Warn().Msg("INTERNAL_API_TOKEN não definido — auth do gateway DESABILITADA. Defina em produção (mesmo token do backend).")
	}
}

// requireAuth envolve um handler exigindo o header X-API-Key válido.
// O preflight OPTIONS passa direto (o handler responde o CORS).
func requireAuth(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodOptions || internalToken == "" {
			next(w, r)
			return
		}

		provided := r.Header.Get("X-API-Key")
		if subtle.ConstantTimeCompare([]byte(provided), []byte(internalToken)) != 1 {
			log.Warn().Str("path", r.URL.Path).Msg("🔒 Requisição rejeitada: X-API-Key inválida ou ausente")
			w.Header().Set("Access-Control-Allow-Origin", "*")
			http.Error(w, "Unauthorized: invalid or missing X-API-Key", http.StatusUnauthorized)
			return
		}

		next(w, r)
	}
}
