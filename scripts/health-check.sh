#!/bin/bash
###############################################################################
# health-check.sh - System Health Monitoring for The-basics System
#
# This script checks all services, verifies API connectivity, tests database
# connections, and monitors resource usage.
#
# Usage:
#   ./scripts/health-check.sh [--verbose] [--json]
#
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PID_DIR="$PROJECT_ROOT/.unified-system/pids"

# Flags
VERBOSE=false
JSON_OUTPUT=false

# Health status
HEALTH_SCORE=0
MAX_SCORE=0
ISSUES=()

###############################################################################
# Utility Functions
###############################################################################

log() {
    if ! $JSON_OUTPUT; then
        echo -e "${GREEN}[✓]${NC} $1"
    fi
}

log_error() {
    if ! $JSON_OUTPUT; then
        echo -e "${RED}[✗]${NC} $1"
    fi
    ISSUES+=("$1")
}

log_warn() {
    if ! $JSON_OUTPUT; then
        echo -e "${YELLOW}[!]${NC} $1"
    fi
    ISSUES+=("WARNING: $1")
}

log_info() {
    if $VERBOSE && ! $JSON_OUTPUT; then
        echo -e "${BLUE}[i]${NC} $1"
    fi
}

check_pass() {
    HEALTH_SCORE=$((HEALTH_SCORE + 1))
    MAX_SCORE=$((MAX_SCORE + 1))
    log "$1"
}

check_fail() {
    MAX_SCORE=$((MAX_SCORE + 1))
    log_error "$1"
}

check_warn() {
    HEALTH_SCORE=$((HEALTH_SCORE + 0.5))
    MAX_SCORE=$((MAX_SCORE + 1))
    log_warn "$1"
}

###############################################################################
# Service Checks
###############################################################################

check_service() {
    local service_name=$1
    local pid_file="$PID_DIR/${service_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            check_pass "Service $service_name is running (PID: $pid)"
            return 0
        else
            check_fail "Service $service_name has stale PID file"
            return 1
        fi
    else
        check_fail "Service $service_name is not running"
        return 1
    fi
}

check_all_services() {
    if ! $JSON_OUTPUT; then
        echo ""
        echo "========================================="
        echo "Service Status Checks"
        echo "========================================="
    fi
    
    check_service "backend"
    check_service "dashboard"
    
    # Optional services
    if [ -f "$PID_DIR/ai-orchestrator.pid" ]; then
        check_service "ai-orchestrator"
    fi
    
    if [ -f "$PID_DIR/trading-engine.pid" ]; then
        check_service "trading-engine"
    fi
}

###############################################################################
# API Endpoint Checks
###############################################################################

check_endpoint() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}
    
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$response_code" == "$expected_code" ]; then
        check_pass "API endpoint $name is responsive ($url)"
        return 0
    else
        check_fail "API endpoint $name failed (expected $expected_code, got $response_code)"
        return 1
    fi
}

check_api_endpoints() {
    if ! $JSON_OUTPUT; then
        echo ""
        echo "========================================="
        echo "API Endpoint Checks"
        echo "========================================="
    fi
    
    # Load environment
    if [ -f "$PROJECT_ROOT/.env" ]; then
        export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs 2>/dev/null || true)
    fi
    
    # Check backend
    local backend_port=${PYTHON_PORT:-8000}
    if curl -s -f "http://localhost:$backend_port" > /dev/null 2>&1; then
        check_pass "Backend API is responsive (port $backend_port)"
    else
        check_fail "Backend API is not responsive (port $backend_port)"
    fi
    
    # Check dashboard
    local dashboard_port=${PORT:-3000}
    if curl -s -f "http://localhost:$dashboard_port" > /dev/null 2>&1; then
        check_pass "Dashboard is responsive (port $dashboard_port)"
    else
        check_fail "Dashboard is not responsive (port $dashboard_port)"
    fi
    
    # Check bot if running
    local bot_port=${BOT_PORT:-9000}
    if [ -f "$PID_DIR/trading-engine.pid" ]; then
        if curl -s -f "http://localhost:$bot_port" > /dev/null 2>&1; then
            check_pass "Trading bot is responsive (port $bot_port)"
        else
            check_warn "Trading bot is not responsive (port $bot_port)"
        fi
    fi
}

###############################################################################
# Database Checks
###############################################################################

check_databases() {
    if ! $JSON_OUTPUT; then
        echo ""
        echo "========================================="
        echo "Database Connection Checks"
        echo "========================================="
    fi
    
    # Load environment
    if [ -f "$PROJECT_ROOT/.env" ]; then
        export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs 2>/dev/null || true)
    fi
    
    # Check Redis
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping > /dev/null 2>&1; then
            check_pass "Redis is connected and responsive"
        else
            check_warn "Redis is not responsive"
        fi
    else
        log_info "Redis not installed, skipping check"
    fi
    
    # Check PostgreSQL
    if [ -n "$DATABASE_URL" ] || [ -n "$POSTGRES_HOST" ]; then
        if command -v psql &> /dev/null; then
            if psql "$DATABASE_URL" -c "SELECT 1" > /dev/null 2>&1; then
                check_pass "PostgreSQL is connected and responsive"
            else
                check_warn "PostgreSQL connection failed"
            fi
        else
            log_info "psql not installed, skipping PostgreSQL check"
        fi
    fi
    
    # Check MongoDB
    if [ -n "$MONGODB_URI" ]; then
        if command -v mongo &> /dev/null || command -v mongosh &> /dev/null; then
            local mongo_cmd=$(command -v mongosh &> /dev/null && echo "mongosh" || echo "mongo")
            if $mongo_cmd "$MONGODB_URI" --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
                check_pass "MongoDB is connected and responsive"
            else
                check_warn "MongoDB connection failed"
            fi
        else
            log_info "mongo/mongosh not installed, skipping MongoDB check"
        fi
    fi
    
    # Check SQLite database files
    if [ -f "$PROJECT_ROOT/.unified-system/db/system.db" ]; then
        check_pass "SQLite system database exists"
    else
        check_warn "SQLite system database not found"
    fi
    
    if [ -f "$PROJECT_ROOT/.unified-system/checkpoints/state.db" ]; then
        check_pass "Recovery checkpoint database exists"
    else
        log_info "Recovery checkpoint database not initialized yet"
    fi
}

###############################################################################
# Resource Monitoring
###############################################################################

check_resources() {
    if ! $JSON_OUTPUT; then
        echo ""
        echo "========================================="
        echo "Resource Usage"
        echo "========================================="
    fi
    
    # CPU usage
    if command -v top &> /dev/null; then
        local cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
        if (( $(echo "$cpu_usage < 80" | bc -l) )); then
            check_pass "CPU usage is normal (${cpu_usage}%)"
        else
            check_warn "CPU usage is high (${cpu_usage}%)"
        fi
    fi
    
    # Memory usage
    if command -v free &> /dev/null; then
        local mem_usage=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')
        if (( $(echo "$mem_usage < 80" | bc -l) )); then
            check_pass "Memory usage is normal (${mem_usage}%)"
        else
            check_warn "Memory usage is high (${mem_usage}%)"
        fi
    elif command -v vm_stat &> /dev/null; then
        # macOS
        log_info "Memory monitoring on macOS"
    fi
    
    # Disk usage
    local disk_usage=$(df -h "$PROJECT_ROOT" | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$disk_usage" -lt 80 ]; then
        check_pass "Disk usage is normal (${disk_usage}%)"
    else
        check_warn "Disk usage is high (${disk_usage}%)"
    fi
    
    # Check log directory size
    if [ -d "$PROJECT_ROOT/.unified-system/logs" ]; then
        local log_size=$(du -sh "$PROJECT_ROOT/.unified-system/logs" 2>/dev/null | cut -f1)
        log_info "Log directory size: $log_size"
    fi
}

###############################################################################
# Credential Validation
###############################################################################

check_credentials() {
    if ! $JSON_OUTPUT; then
        echo ""
        echo "========================================="
        echo "Credential Validation"
        echo "========================================="
    fi
    
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        check_fail ".env file not found"
        return 1
    fi
    
    check_pass ".env file exists"
    
    # Load environment
    export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs 2>/dev/null || true)
    
    # Check critical credentials
    if [ -n "$JWT_SECRET" ]; then
        check_pass "JWT_SECRET is configured"
    else
        check_warn "JWT_SECRET is not configured"
    fi
    
    if [ -n "$ENCRYPTION_KEY" ]; then
        check_pass "ENCRYPTION_KEY is configured"
    else
        check_warn "ENCRYPTION_KEY is not configured"
    fi
    
    # Check trading credentials (if trading enabled)
    if [ "$FEATURE_TRADING_ENABLED" == "true" ]; then
        if [ -n "$NDAX_API_KEY" ] && [ -n "$NDAX_API_SECRET" ]; then
            check_pass "Trading credentials are configured"
        else
            check_fail "Trading enabled but credentials missing"
        fi
    fi
}

###############################################################################
# File and Path Validation
###############################################################################

check_files() {
    if ! $JSON_OUTPUT; then
        echo ""
        echo "========================================="
        echo "File and Path Validation"
        echo "========================================="
    fi
    
    # Check critical files
    local critical_files=(
        "package.json"
        "server.js"
        "unified_system.py"
        "config/features.yaml"
        "src/core/error-handler.js"
        "src/core/recovery-system.py"
        "src/core/freeze-detector.js"
        "src/security/credential-manager.js"
    )
    
    for file in "${critical_files[@]}"; do
        if [ -f "$PROJECT_ROOT/$file" ]; then
            log_info "✓ $file exists"
        else
            check_warn "Missing file: $file"
        fi
    done
    
    # Check critical directories
    local critical_dirs=(
        "src"
        "scripts"
        "config"
        ".unified-system/logs"
    )
    
    for dir in "${critical_dirs[@]}"; do
        if [ -d "$PROJECT_ROOT/$dir" ]; then
            log_info "✓ $dir exists"
        else
            check_fail "Missing directory: $dir"
        fi
    done
}

###############################################################################
# JSON Output
###############################################################################

output_json() {
    local health_percent=$(echo "scale=2; ($HEALTH_SCORE / $MAX_SCORE) * 100" | bc)
    
    cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "health_score": $HEALTH_SCORE,
  "max_score": $MAX_SCORE,
  "health_percent": $health_percent,
  "status": "$([ $HEALTH_SCORE == $MAX_SCORE ] && echo "healthy" || echo "degraded")",
  "issues": [
$(printf '    "%s"' "${ISSUES[0]}"
for issue in "${ISSUES[@]:1}"; do
    printf ',\n    "%s"' "$issue"
done
printf '\n')
  ]
}
EOF
}

###############################################################################
# Main
###############################################################################

main() {
    # Parse arguments
    for arg in "$@"; do
        case $arg in
            --verbose|-v)
                VERBOSE=true
                ;;
            --json|-j)
                JSON_OUTPUT=true
                ;;
        esac
    done
    
    if ! $JSON_OUTPUT; then
        echo "========================================="
        echo "The-basics System Health Check"
        echo "========================================="
    fi
    
    # Run all checks
    check_all_services
    check_api_endpoints
    check_databases
    check_resources
    check_credentials
    check_files
    
    # Output results
    if $JSON_OUTPUT; then
        output_json
    else
        echo ""
        echo "========================================="
        echo "Health Summary"
        echo "========================================="
        
        local health_percent=$(echo "scale=2; ($HEALTH_SCORE / $MAX_SCORE) * 100" | bc)
        echo -e "Score: $HEALTH_SCORE / $MAX_SCORE (${health_percent}%)"
        
        if [ $HEALTH_SCORE == $MAX_SCORE ]; then
            echo -e "${GREEN}Status: All systems healthy ✓${NC}"
            exit 0
        elif (( $(echo "$health_percent >= 70" | bc -l) )); then
            echo -e "${YELLOW}Status: System operational with warnings${NC}"
            exit 0
        else
            echo -e "${RED}Status: System has critical issues${NC}"
            exit 1
        fi
    fi
}

main "$@"
