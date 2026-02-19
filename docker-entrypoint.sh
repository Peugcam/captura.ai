#!/bin/bash
set -e

echo "==================================="
echo "GTA Analytics V2 - Starting..."
echo "==================================="

# Change backend port to 8080 (Fly.io expects this port)
export BACKEND_PORT=8080
export BACKEND_HOST=0.0.0.0

# Start Backend on port 8080
echo "Starting Backend on port ${BACKEND_PORT}..."
cd /app/backend
exec python main_websocket.py
