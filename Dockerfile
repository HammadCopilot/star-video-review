# Multi-stage build for STAR Video Review App
# Stage 1: Build React Frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy frontend source
COPY frontend/ ./

# Build React app for production
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=${REACT_APP_API_URL:-/api}
RUN npm run build

# Stage 2: Python Backend with Frontend
FROM python:3.10-slim-bookworm

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    python3-dev \
    build-essential \
    libpq-dev \
    postgresql-client \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Upgrade pip first
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements file
COPY backend/requirements.txt .

# Configure pip with much longer timeout for large downloads (PyTorch is ~900MB)
RUN pip config set global.timeout 600 && \
    pip config set global.index-url https://pypi.org/simple/

# Install dependencies in stages for better caching and reliability
# Stage 1: Lightweight dependencies first
RUN pip install --no-cache-dir --timeout 600 \
    gunicorn==21.2.0 \
    Flask==3.1.2 \
    Flask-SQLAlchemy==3.0.5 \
    Flask-JWT-Extended==4.6.0 \
    Flask-CORS==4.0.0 \
    python-dotenv==1.0.0 \
    bcrypt==4.1.2 \
    "Werkzeug>=3.1.0" \
    requests==2.31.0 \
    urllib3==2.1.0 \
    python-dateutil==2.8.2 \
    psycopg2-binary==2.9.9

# Stage 2: Image processing libraries
RUN pip install --no-cache-dir --timeout 600 \
    Pillow==10.2.0 \
    "numpy>=1.24.0,<2.0.0" \
    opencv-python==4.8.1.78

# Stage 3: Video processing (requires ffmpeg)
RUN pip install --no-cache-dir --timeout 600 \
    moviepy==2.0.0.dev2 \
    ffmpeg-python==0.2.0

# Stage 4: OpenAI client (lightweight)
RUN pip install --no-cache-dir --timeout 600 \
    openai==1.59.6

# Stage 5: PyTorch and Whisper (heavy downloads - install with retry)
# PyTorch is ~900MB, so we install it separately with more time
RUN pip install --no-cache-dir --timeout 1200 torch || \
    (sleep 10 && pip install --no-cache-dir --timeout 1200 torch) || \
    (sleep 10 && pip install --no-cache-dir --timeout 1200 torch)

# Stage 6: Whisper (depends on torch)
RUN pip install --no-cache-dir --timeout 600 \
    openai-whisper==20240930

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

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8081", "--workers", "2", "--timeout", "300", "--log-level", "info", "--pythonpath", "/app/backend", "app:create_app('production')"]