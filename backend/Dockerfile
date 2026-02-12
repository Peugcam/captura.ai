# ========================================
# Stage 1: Builder
# ========================================
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# ========================================
# Stage 2: Runtime
# ========================================
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-por \
    libtesseract-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r backend && useradd -r -g backend backend

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/backend/.local

# Copy application code
COPY . .

# Create exports directory
RUN mkdir -p exports && \
    chown -R backend:backend /app

# Switch to non-root user
USER backend

# Add .local/bin to PATH
ENV PATH=/home/backend/.local/bin:$PATH

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# Default command
CMD ["python", "main_websocket.py"]
