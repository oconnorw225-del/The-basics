# Multi-stage Dockerfile for Chimera Unified System
FROM node:20-alpine AS frontend-builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (use npm install if no lock file exists)
RUN npm install || npm ci

# Copy source files
COPY . .

# Build frontend
RUN npm run build || echo "Frontend build skipped"

# Python backend stage
FROM python:3.11-slim AS backend

WORKDIR /app

# Install system dependencies including curl for health checks
RUN apt-get update && apt-get install -y \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY backend/ ./backend/
COPY unified_system.py .
COPY bot.js .
COPY server.js .

# Create dist directory and copy built frontend if available
RUN mkdir -p ./dist
COPY --from=frontend-builder /app/dist ./dist/ || true
COPY --from=frontend-builder /app/package*.json ./

# Install Node production dependencies
RUN npm install --only=production || true

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port 8080 (default for container)
EXPOSE 8080

# Set environment variables
ENV PORT=8080
ENV NODE_ENV=production
ENV PYTHON_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:${PORT}/ || exit 1

# Start command - run unified system
CMD ["python3", "unified_system.py"]

