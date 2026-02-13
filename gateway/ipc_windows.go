//go:build windows
// +build windows

package main

import (
	"net"
	"net/http"

	"github.com/Microsoft/go-winio"
	"github.com/rs/zerolog/log"
)

// IPCServer handles Unix Domain Socket / Named Pipe connections
type IPCServer struct {
	socketPath string
	listener   net.Listener
}

// NewIPCServer creates a new IPC server using Windows Named Pipes
func NewIPCServer() (*IPCServer, error) {
	socketPath := `\\.\pipe\gta-gateway`
	listener, err := winio.ListenPipe(socketPath, nil)
	if err != nil {
		return nil, err
	}
	log.Info().Str("pipe", socketPath).Msg("Named Pipe listener created (Windows)")

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
