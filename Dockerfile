# Multi-stage build for STAR Video Review App
# Stage 1: Build React Frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build React app for production
RUN npm run build

# Stage 2: Python Backend with Frontend
FROM python:3.10-slim-bookworm

WORKDIR /app

# Install system dependencies for opencv, ffmpeg, and other packages
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY backend/requirements.txt .

# Configure pip
RUN pip config set global.timeout 100 && \
    pip config set global.index-url https://pypi.org/simple/

# Install Python dependencies (handle numpy/opencv conflicts)
RUN pip uninstall -y numpy opencv-python || true && \
    pip install --no-cache-dir --upgrade \
    gunicorn==21.2.0 \
    -r requirements.txt

# Copy backend application code
COPY backend/ ./backend/

# Copy built React frontend from builder stage
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Create required directories
RUN mkdir -p backend/uploads backend/models backend/instance && \
    chmod -R 755 backend/uploads backend/models backend/instance

# Set working directory to backend
WORKDIR /app/backend

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PORT=8081

# Expose port
EXPOSE 8081

# Create entrypoint script to serve static files
RUN echo '#!/bin/bash\n\
from flask import Flask, send_from_directory\n\
import os\n\
\n\
app = None\n\
\n\
def setup_static_serving(flask_app):\n\
    """Setup Flask to serve React static files"""\n\
    frontend_build = "/app/frontend/build"\n\
    \n\
    @flask_app.route("/", defaults={"path": ""})\n\
    @flask_app.route("/<path:path>")\n\
    def serve(path):\n\
        if path.startswith("api/") or path == "health":\n\
            # Let Flask handle API routes\n\
            pass\n\
        elif path != "" and os.path.exists(os.path.join(frontend_build, path)):\n\
            return send_from_directory(frontend_build, path)\n\
        else:\n\
            return send_from_directory(frontend_build, "index.html")\n\
    \n\
    return flask_app\n\
' > /app/setup_static.py

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8081", "--workers", "2", "--timeout", "300", "--log-level", "info", "app:create_app()"]