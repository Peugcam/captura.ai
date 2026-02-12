# ========================================
# Stage 1: Build
# ========================================
FROM golang:1.21-alpine AS builder

# Install build dependencies
RUN apk add --no-cache git ca-certificates

WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY *.go ./

# Build binary (statically linked for alpine)
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -ldflags='-w -s -extldflags "-static"' \
    -o gateway \
    main.go websocket.go buffer.go

# ========================================
# Stage 2: Runtime
# ========================================
FROM alpine:latest

# Install runtime dependencies
RUN apk --no-cache add ca-certificates tzdata

# Create non-root user
RUN addgroup -g 1000 gateway && \
    adduser -D -u 1000 -G gateway gateway

WORKDIR /app

# Copy binary from builder
COPY --from=builder /app/gateway .

# Change ownership
RUN chown -R gateway:gateway /app

# Switch to non-root user
USER gateway

# Expose ports
# 8000: HTTP/WebSocket
# 50000-50100: WebRTC UDP (reserved for future use)
EXPOSE 8000
EXPOSE 50000-50100/udp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1

# Default command
CMD ["./gateway", "-port=8000", "-buffer=200"]
