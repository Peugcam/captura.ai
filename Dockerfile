# Multi-stage Dockerfile for GTA Analytics V2
# Stage 1: Build Gateway (Go)
FROM golang:1.21-alpine AS gateway-builder

WORKDIR /build

# Copy Gateway source
COPY gateway/ ./

# Build Gateway
RUN go build -o gateway .

# Stage 2: Python Backend + Frontend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    tesseract-ocr \
    tesseract-ocr-por \
    tesseract-ocr-eng \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Gateway binary from builder
COPY --from=gateway-builder /build/gateway /app/gateway/gateway

# Copy Python requirements
COPY backend/requirements.txt /app/backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy application code
COPY backend/ /app/backend/

# Copy all dashboard HTML files
COPY dashboard-obs.html /app/
COPY dashboard-v2.html /app/
COPY capture-obs.html /app/
COPY dashboard-player.html /app/backend/
COPY dashboard-viewer.html /app/backend/
COPY dashboard-strategist.html /app/backend/
COPY dashboard-strategist-v2.html /app/backend/
COPY dashboard-monitor.html /app/backend/
COPY dashboard-tournament.html /app/backend/

# Create data directory for exports
RUN mkdir -p /data/exports

# Expose ports
EXPOSE 8080 8000 3000

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV GATEWAY_PORT=8000
ENV BACKEND_PORT=3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Start script
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
