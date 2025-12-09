# Multi-stage Dockerfile for NDAX Quantum Engine
FROM node:18-alpine AS frontend-builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source files
COPY . .

# Build frontend
RUN npm run build

# Python backend stage
FROM python:3.11-slim AS backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY backend/ ./backend/
COPY unified_system.py .

# Node.js runtime stage
FROM node:18-alpine AS runtime

WORKDIR /app

# Copy built frontend from builder
COPY --from=frontend-builder /app/dist ./dist
COPY --from=frontend-builder /app/package*.json ./

# Install production dependencies only
RUN npm ci --only=production

# Copy server files
COPY server.js .
COPY bot.js .

# Copy Python backend from backend stage
COPY --from=backend /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend /app/backend ./backend
COPY --from=backend /app/unified_system.py .

# Expose ports
EXPOSE 3000 8000 9000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# Start command
CMD ["node", "server.js"]
