//go:build !windows
// +build !windows

package main

import (
	"net"
	"net/http"
	"os"

	"github.com/rs/zerolog/log"
)

// IPCServer handles Unix Domain Socket / Named Pipe connections
type IPCServer struct {
	socketPath string
	listener   net.Listener
}

// NewIPCServer creates a new IPC server using Unix Domain Sockets
func NewIPCServer() (*IPCServer, error) {
	socketPath := "/tmp/gta-gateway.sock"

	// Remove existing socket file if it exists
	os.Remove(socketPath)

	listener, err := net.Listen("unix", socketPath)
	if err != nil {
		return nil, err
	}
	log.Info().Str("socket", socketPath).Msg("Unix Domain Socket listener created (Linux/Mac)")

	return &IPCServer{
		socketPath: socketPath,
		listener:   listener,
	}, nil
}

// Serve starts the IPC server with the given HTTP handler
func (s *IPCServer) Serve(handler http.Handler) error {
	log.Info().Str("path", s.socketPath).Msg("Starting IPC server")
	return http.Serve(s.listener, handler)
}

// Close closes the IPC server
func (s *IPCServer) Close() error {
	log.Info().Msg("Closing IPC server")
	if s.listener != nil {
		return s.listener.Close()
	}
	return nil
}

// GetPath returns the socket/pipe path
func (s *IPCServer) GetPath() string {
	return s.socketPath
}
