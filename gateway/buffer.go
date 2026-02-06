package main

import (
	"sync"
	"time"
)

// Frame representa um frame capturado
type Frame struct {
	Data      []byte    `json:"data"`
	Timestamp int64     `json:"timestamp"`
	Number    int       `json:"number"`
	ReceivedAt time.Time `json:"received_at"`
}

// RingBuffer é um buffer circular lock-free para frames
type RingBuffer struct {
	buffer   []Frame
	size     int
	head     int
	tail     int
	count    int
	mu       sync.RWMutex
	notEmpty *sync.Cond
	notFull  *sync.Cond
}

// NewRingBuffer cria um novo buffer circular
func NewRingBuffer(size int) *RingBuffer {
	rb := &RingBuffer{
		buffer: make([]Frame, size),
		size:   size,
	}
	rb.notEmpty = sync.NewCond(&rb.mu)
	rb.notFull = sync.NewCond(&rb.mu)
	return rb
}

// Push adiciona um frame ao buffer (bloqueia se cheio)
func (rb *RingBuffer) Push(frame Frame) bool {
	rb.mu.Lock()
	defer rb.mu.Unlock()

	// Se buffer está cheio, descarta o frame mais antigo (política drop-oldest)
	if rb.count == rb.size {
		// Avança tail para descartar frame antigo
		rb.tail = (rb.tail + 1) % rb.size
		rb.count--
	}

	rb.buffer[rb.head] = frame
	rb.head = (rb.head + 1) % rb.size
	rb.count++

	rb.notEmpty.Signal()
	return true
}

// Pop remove e retorna o frame mais antigo do buffer
func (rb *RingBuffer) Pop() (Frame, bool) {
	rb.mu.Lock()
	defer rb.mu.Unlock()

	if rb.count == 0 {
		return Frame{}, false
	}

	frame := rb.buffer[rb.tail]
	rb.tail = (rb.tail + 1) % rb.size
	rb.count--

	rb.notFull.Signal()
	return frame, true
}

// PopBatch retorna até maxFrames frames do buffer
func (rb *RingBuffer) PopBatch(maxFrames int) []Frame {
	rb.mu.Lock()
	defer rb.mu.Unlock()

	if rb.count == 0 {
		return nil
	}

	batchSize := maxFrames
	if batchSize > rb.count {
		batchSize = rb.count
	}

	frames := make([]Frame, batchSize)
	for i := 0; i < batchSize; i++ {
		frames[i] = rb.buffer[rb.tail]
		rb.tail = (rb.tail + 1) % rb.size
		rb.count--
	}

	rb.notFull.Signal()
	return frames
}

// Len retorna o número de frames no buffer
func (rb *RingBuffer) Len() int {
	rb.mu.RLock()
	defer rb.mu.RUnlock()
	return rb.count
}

// IsFull verifica se o buffer está cheio
func (rb *RingBuffer) IsFull() bool {
	rb.mu.RLock()
	defer rb.mu.RUnlock()
	return rb.count == rb.size
}

// IsEmpty verifica se o buffer está vazio
func (rb *RingBuffer) IsEmpty() bool {
	rb.mu.RLock()
	defer rb.mu.RUnlock()
	return rb.count == 0
}

// Clear limpa todos os frames do buffer
func (rb *RingBuffer) Clear() {
	rb.mu.Lock()
	defer rb.mu.Unlock()
	rb.head = 0
	rb.tail = 0
	rb.count = 0
}

// Stats retorna estatísticas do buffer
func (rb *RingBuffer) Stats() map[string]interface{} {
	rb.mu.RLock()
	defer rb.mu.RUnlock()

	return map[string]interface{}{
		"size":         rb.size,
		"count":        rb.count,
		"usage_percent": float64(rb.count) / float64(rb.size) * 100,
	}
}
