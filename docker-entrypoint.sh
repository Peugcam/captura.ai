#!/bin/bash
set -e

echo "==================================="
echo "GTA Analytics V2 - Starting..."
echo "==================================="

# Start Gateway in background
echo "Starting Gateway on port ${GATEWAY_PORT}..."
cd /app/gateway
./gateway -port=${GATEWAY_PORT} -buffer=200 -webrtc=true -websocket=true -ipc=true &
GATEWAY_PID=$!
echo "Gateway started (PID: ${GATEWAY_PID})"

# Wait for Gateway to be ready
sleep 3

# Start Backend
echo "Starting Backend on port ${BACKEND_PORT}..."
cd /app/backend
python main_websocket.py &
BACKEND_PID=$!
echo "Backend started (PID: ${BACKEND_PID})"

# Start Nginx reverse proxy
echo "Starting Nginx reverse proxy on port ${PORT}..."
cat > /etc/nginx/nginx.conf <<EOF
events {
    worker_connections 1024;
}

http {
    upstream gateway {
        server localhost:${GATEWAY_PORT};
    }

    upstream backend {
        server localhost:${BACKEND_PORT};
    }

    server {
        listen ${PORT};

        location / {
            root /app;
            index dashboard-obs.html;
            try_files \$uri \$uri/ =404;
        }

        location /gateway/ {
            proxy_pass http://gateway/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host \$host;
            proxy_cache_bypass \$http_upgrade;
        }

        location /api/ {
            proxy_pass http://backend/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host \$host;
            proxy_cache_bypass \$http_upgrade;
        }

        location /events {
            proxy_pass http://backend/events;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host \$host;
            proxy_cache_bypass \$http_upgrade;
        }

        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF

nginx -g "daemon off;" &
NGINX_PID=$!
echo "Nginx started (PID: ${NGINX_PID})"

echo "==================================="
echo "All services started successfully!"
echo "Gateway: http://localhost:${GATEWAY_PORT}"
echo "Backend: http://localhost:${BACKEND_PORT}"
echo "Frontend: http://localhost:${PORT}"
echo "==================================="

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
