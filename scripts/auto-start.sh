#!/bin/bash
###############################################################################
# auto-start.sh - Service Startup Orchestration for The-basics System
#
# This script starts all system components in the correct order with
# dependency checking and health verification.
#
# Usage:
#   ./scripts/auto-start.sh [--dev|--prod]
#
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/.unified-system/logs"
LOG_FILE="$LOG_DIR/startup.log"
PID_DIR="$PROJECT_ROOT/.unified-system/pids"

# Create necessary directories
mkdir -p "$LOG_DIR" "$PID_DIR"

# Default mode
MODE="dev"

###############################################################################
# Utility Functions
###############################################################################

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

###############################################################################
# Pre-flight Checks
###############################################################################

preflight_checks() {
    log "Running pre-flight checks..."
    
    local failed=0
    
    # Check if .env exists
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        log_error ".env file not found. Run auto-setup.sh first."
        failed=1
    fi
    
    # Check if node_modules exists
    if [ ! -d "$PROJECT_ROOT/node_modules" ]; then
        log_warn "node_modules not found. Installing dependencies..."
        cd "$PROJECT_ROOT" && npm install || failed=1
    fi
    
    # Check if Python venv exists
    if [ ! -d "$PROJECT_ROOT/venv" ]; then
        log_warn "Python venv not found. Creating..."
        python3 -m venv "$PROJECT_ROOT/venv" || failed=1
    fi
    
    # Load environment variables
    if [ -f "$PROJECT_ROOT/.env" ]; then
        export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs)
        log "✓ Environment variables loaded"
    fi
    
    if [ $failed -eq 1 ]; then
        log_error "Pre-flight checks failed"
        return 1
    fi
    
    log "✓ Pre-flight checks passed"
    return 0
}

###############################################################################
# Service Management
###############################################################################

start_service() {
    local service_name=$1
    local command=$2
    local port=$3
    local log_file="$LOG_DIR/${service_name}.log"
    local pid_file="$PID_DIR/${service_name}.pid"
    
    log_info "Starting $service_name..."
    
    # Check if already running
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            log_warn "$service_name already running (PID: $pid)"
            return 0
        else
            rm -f "$pid_file"
        fi
    fi
    
    # Start the service
    cd "$PROJECT_ROOT"
    nohup bash -c "$command" > "$log_file" 2>&1 &
    local pid=$!
    echo $pid > "$pid_file"
    
    log "✓ $service_name started (PID: $pid)"
    
    # Wait a moment for startup
    sleep 2
    
    # Verify it's still running
    if kill -0 "$pid" 2>/dev/null; then
        log "✓ $service_name is running"
        
        # Check port if specified
        if [ -n "$port" ]; then
            verify_service_health "$service_name" "$port" 30
        fi
        
        return 0
    else
        log_error "$service_name failed to start"
        return 1
    fi
}

stop_service() {
    local service_name=$1
    local pid_file="$PID_DIR/${service_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            log_info "Stopping $service_name (PID: $pid)..."
            kill "$pid" || kill -9 "$pid"
            rm -f "$pid_file"
            log "✓ $service_name stopped"
        else
            rm -f "$pid_file"
        fi
    else
        log_info "$service_name is not running"
    fi
}

verify_service_health() {
    local service_name=$1
    local port=$2
    local timeout=$3
    local elapsed=0
    
    log_info "Verifying $service_name health on port $port..."
    
    while [ $elapsed -lt $timeout ]; do
        if curl -s -f "http://localhost:$port" > /dev/null 2>&1 || \
           nc -z localhost "$port" > /dev/null 2>&1; then
            log "✓ $service_name health check passed"
            return 0
        fi
        sleep 1
        elapsed=$((elapsed + 1))
    done
    
    log_warn "$service_name health check failed (timeout after ${timeout}s)"
    return 1
}

###############################################################################
# Database Services
###############################################################################

start_databases() {
    log "Starting database services..."
    
    # Redis (if available and in dev mode)
    if command -v redis-server &> /dev/null && [ "$MODE" == "dev" ]; then
        if ! pgrep -x redis-server > /dev/null; then
            log_info "Starting Redis..."
            redis-server --daemonize yes || log_warn "Failed to start Redis"
        else
            log "✓ Redis already running"
        fi
    fi
    
    # PostgreSQL (if configured)
    if [ -n "$POSTGRES_HOST" ] && [ "$POSTGRES_HOST" == "localhost" ] && [ "$MODE" == "dev" ]; then
        if command -v pg_ctl &> /dev/null; then
            log_info "Starting PostgreSQL..."
            pg_ctl start -D "$HOME/postgres" || log_warn "Failed to start PostgreSQL"
        fi
    fi
    
    # MongoDB (if configured)
    if [ -n "$MONGODB_URI" ] && [[ "$MONGODB_URI" == *"localhost"* ]] && [ "$MODE" == "dev" ]; then
        if command -v mongod &> /dev/null; then
            if ! pgrep -x mongod > /dev/null; then
                log_info "Starting MongoDB..."
                mongod --fork --logpath "$LOG_DIR/mongodb.log" --dbpath "$PROJECT_ROOT/.unified-system/mongodb" || log_warn "Failed to start MongoDB"
            else
                log "✓ MongoDB already running"
            fi
        fi
    fi
    
    log "✓ Database services ready"
}

###############################################################################
# Application Services
###############################################################################

start_backend() {
    log "Starting backend API..."
    
    local port=${PYTHON_PORT:-8000}
    
    # Activate Python venv and start backend
    local cmd="source $PROJECT_ROOT/venv/bin/activate && cd $PROJECT_ROOT && python3 unified_system.py"
    
    start_service "backend" "$cmd" "$port"
}

start_ai_orchestrator() {
    log "Starting AI orchestrator..."
    
    # Check if feature is enabled
    if [ "$FEATURE_AI_PLATFORMS_ENABLED" != "true" ]; then
        log_info "AI platforms disabled, skipping orchestrator"
        return 0
    fi
    
    local cmd="cd $PROJECT_ROOT/freelance_engine && python3 orchestrator.py"
    
    start_service "ai-orchestrator" "$cmd" ""
}

start_trading_engine() {
    log "Starting trading engine..."
    
    # Check if trading is enabled
    if [ "$FEATURE_TRADING_ENABLED" != "true" ]; then
        log_info "Trading disabled, skipping engine"
        return 0
    fi
    
    local cmd="cd $PROJECT_ROOT && node bot.js"
    
    start_service "trading-engine" "$cmd" "${BOT_PORT:-9000}"
}

start_dashboard() {
    log "Starting dashboard..."
    
    local port=${PORT:-3000}
    
    if [ "$MODE" == "dev" ]; then
        # Development mode with Vite
        local cmd="cd $PROJECT_ROOT && npm run dev"
    else
        # Production mode
        local cmd="cd $PROJECT_ROOT && npm run start"
    fi
    
    start_service "dashboard" "$cmd" "$port"
}

start_monitoring() {
    log "Starting monitoring services..."
    
    # Prometheus (if configured)
    if [ "$PROMETHEUS_ENABLED" == "true" ] && command -v prometheus &> /dev/null; then
        log_info "Starting Prometheus..."
        # Prometheus config would go here
    fi
    
    log "✓ Monitoring services ready"
}

###############################################################################
# Stop All Services
###############################################################################

stop_all_services() {
    log "Stopping all services..."
    
    stop_service "dashboard"
    stop_service "trading-engine"
    stop_service "ai-orchestrator"
    stop_service "backend"
    
    # Stop databases if in dev mode
    if [ "$MODE" == "dev" ]; then
        if pgrep -x redis-server > /dev/null; then
            log_info "Stopping Redis..."
            redis-cli shutdown || true
        fi
        
        if pgrep -x mongod > /dev/null; then
            log_info "Stopping MongoDB..."
            mongod --shutdown || true
        fi
    fi
    
    log "✓ All services stopped"
}

###############################################################################
# Status Check
###############################################################################

check_status() {
    log "Checking service status..."
    
    local all_running=true
    
    for service in backend ai-orchestrator trading-engine dashboard; do
        local pid_file="$PID_DIR/${service}.pid"
        
        if [ -f "$pid_file" ]; then
            local pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                log "✓ $service: Running (PID: $pid)"
            else
                log_error "$service: Not running (stale PID file)"
                all_running=false
                rm -f "$pid_file"
            fi
        else
            log_warn "$service: Not started"
            all_running=false
        fi
    done
    
    if $all_running; then
        log "✓ All services are running"
        return 0
    else
        log_warn "Some services are not running"
        return 1
    fi
}

###############################################################################
# Main Startup Flow
###############################################################################

main() {
    log "========================================="
    log "The-basics System Auto-Start"
    log "========================================="
    
    # Parse arguments
    if [ "$1" == "--prod" ]; then
        MODE="prod"
        export NODE_ENV=production
    elif [ "$1" == "--dev" ]; then
        MODE="dev"
        export NODE_ENV=development
    elif [ "$1" == "--stop" ]; then
        stop_all_services
        exit 0
    elif [ "$1" == "--status" ]; then
        check_status
        exit $?
    fi
    
    log_info "Mode: $MODE"
    
    # Run pre-flight checks
    preflight_checks || exit 1
    
    # Start services in order
    log "Starting services..."
    
    start_databases || log_warn "Database startup had issues"
    sleep 2
    
    start_backend || log_error "Backend failed to start"
    sleep 3
    
    start_ai_orchestrator || log_warn "AI orchestrator startup had issues"
    sleep 2
    
    start_trading_engine || log_warn "Trading engine startup had issues"
    sleep 2
    
    start_dashboard || log_warn "Dashboard startup had issues"
    sleep 3
    
    start_monitoring || log_warn "Monitoring startup had issues"
    
    # Final health check
    log "========================================="
    log "Startup sequence complete!"
    log "========================================="
    
    check_status
    
    log_info ""
    log_info "Services:"
    log_info "  Dashboard:  http://localhost:${PORT:-3000}"
    log_info "  Backend:    http://localhost:${PYTHON_PORT:-8000}"
    log_info "  Bot:        http://localhost:${BOT_PORT:-9000}"
    log_info ""
    log_info "Logs: $LOG_DIR"
    log_info "PIDs: $PID_DIR"
    log_info ""
    log_info "To stop all services: $0 --stop"
    log_info "To check status: $0 --status"
}

# Handle SIGTERM and SIGINT
trap 'stop_all_services; exit 0' SIGTERM SIGINT

# Run main function
main "$@"
