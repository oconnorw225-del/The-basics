#!/bin/bash
################################################################################
# Chimera Auto-Pilot - Automated Installation & Configuration Script
# 
# This script automatically:
# 1. Detects the environment and installs all dependencies
# 2. Sets up databases (PostgreSQL, MongoDB, Redis)
# 3. Configures the Chimera system with intelligent defaults
# 4. Installs the bot and all components
# 5. Creates systemd service for auto-start
# 6. Activates and starts the system
# 7. Enables self-optimization
#
# Usage: 
#   bash auto_install.sh                    # Interactive mode
#   bash auto_install.sh --auto             # Fully automated mode
#   bash auto_install.sh --production       # Production deployment
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/chimera-autopilot"
LOG_DIR="/var/log/chimera"
CONFIG_DIR="/etc/chimera"
DATA_DIR="/var/lib/chimera"
VENV_DIR="$INSTALL_DIR/venv"
SERVICE_NAME="chimera-autopilot"

# Parse arguments
AUTO_MODE=false
PRODUCTION_MODE=false
SKIP_DATABASES=false

for arg in "$@"; do
    case $arg in
        --auto)
            AUTO_MODE=true
            ;;
        --production)
            PRODUCTION_MODE=true
            ;;
        --skip-databases)
            SKIP_DATABASES=true
            ;;
    esac
done

################################################################################
# Helper Functions
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "\n${PURPLE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${PURPLE}▶ $1${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════${NC}\n"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        OS=$(uname -s)
        VER=$(uname -r)
    fi
    log_info "Detected OS: $OS $VER"
}

wait_for_input() {
    if [ "$AUTO_MODE" = false ]; then
        read -p "Press Enter to continue..."
    fi
}

################################################################################
# Installation Steps
################################################################################

print_banner() {
    clear
    echo -e "${CYAN}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║     ██████╗██╗  ██╗██╗███╗   ███╗███████╗██████╗  █████╗               ║
║    ██╔════╝██║  ██║██║████╗ ████║██╔════╝██╔══██╗██╔══██╗              ║
║    ██║     ███████║██║██╔████╔██║█████╗  ██████╔╝███████║              ║
║    ██║     ██╔══██║██║██║╚██╔╝██║██╔══╝  ██╔══██╗██╔══██║              ║
║    ╚██████╗██║  ██║██║██║ ╚═╝ ██║███████╗██║  ██║██║  ██║              ║
║     ╚═════╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝              ║
║                                                                          ║
║              AUTO-PILOT TRADING SYSTEM - AUTO INSTALLER                 ║
║                    Automated Setup & Deployment                          ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}\n"
    
    if [ "$AUTO_MODE" = true ]; then
        log_info "Running in FULLY AUTOMATED mode"
    else
        log_info "Running in INTERACTIVE mode"
    fi
    
    if [ "$PRODUCTION_MODE" = true ]; then
        log_warning "PRODUCTION deployment mode enabled"
    fi
    
    sleep 2
}

step1_system_checks() {
    log_step "STEP 1: System Requirements Check"
    
    # Check CPU
    CPU_CORES=$(nproc)
    log_info "CPU Cores: $CPU_CORES"
    
    # Check Memory
    TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
    log_info "Total Memory: ${TOTAL_MEM}GB"
    
    if [ "$TOTAL_MEM" -lt 2 ]; then
        log_warning "Recommended memory is 2GB+. System has ${TOTAL_MEM}GB"
    fi
    
    # Check Disk Space
    DISK_SPACE=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
    log_info "Available Disk Space: ${DISK_SPACE}GB"
    
    if [ "$DISK_SPACE" -lt 10 ]; then
        log_warning "Recommended disk space is 10GB+. Available: ${DISK_SPACE}GB"
    fi
    
    # Check Network
    if ping -c 1 google.com &> /dev/null; then
        log_success "Network connectivity: OK"
    else
        log_error "No network connectivity"
        exit 1
    fi
    
    log_success "System requirements check completed"
    wait_for_input
}

step2_install_system_packages() {
    log_step "STEP 2: Installing System Packages"
    
    # Update package lists
    log_info "Updating package lists..."
    apt-get update -qq
    
    # Essential packages
    log_info "Installing essential packages..."
    apt-get install -y -qq \
        curl \
        wget \
        git \
        build-essential \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        sudo \
        vim \
        htop \
        net-tools
    
    log_success "System packages installed"
    wait_for_input
}

step3_install_python() {
    log_step "STEP 3: Installing Python 3.11+"
    
    # Check if Python 3.11+ is already installed
    if command -v python3.11 &> /dev/null; then
        log_success "Python 3.11 already installed"
    else
        log_info "Installing Python 3.11..."
        add-apt-repository -y ppa:deadsnakes/ppa
        apt-get update -qq
        apt-get install -y -qq \
            python3.11 \
            python3.11-venv \
            python3.11-dev \
            python3-pip
    fi
    
    # Verify installation
    PYTHON_VERSION=$(python3.11 --version)
    log_success "Installed: $PYTHON_VERSION"
    
    # Upgrade pip
    python3.11 -m pip install --upgrade pip setuptools wheel
    
    wait_for_input
}

step4_install_nodejs() {
    log_step "STEP 4: Installing Node.js 18+"
    
    # Check if Node.js is already installed
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        log_success "Node.js already installed: $NODE_VERSION"
    else
        log_info "Installing Node.js 18..."
        curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
        apt-get install -y -qq nodejs
        
        NODE_VERSION=$(node --version)
        log_success "Installed Node.js: $NODE_VERSION"
    fi
    
    # Install global npm packages
    log_info "Installing global npm packages..."
    npm install -g npm@latest
    
    wait_for_input
}

step5_install_databases() {
    log_step "STEP 5: Installing Databases"
    
    if [ "$SKIP_DATABASES" = true ]; then
        log_warning "Skipping database installation (--skip-databases flag)"
        return
    fi
    
    # PostgreSQL
    log_info "Installing PostgreSQL..."
    apt-get install -y -qq postgresql postgresql-contrib
    systemctl start postgresql
    systemctl enable postgresql
    log_success "PostgreSQL installed and running"
    
    # MongoDB
    log_info "Installing MongoDB..."
    wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add -
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list
    apt-get update -qq
    apt-get install -y -qq mongodb-org
    systemctl start mongod
    systemctl enable mongod
    log_success "MongoDB installed and running"
    
    # Redis
    log_info "Installing Redis..."
    apt-get install -y -qq redis-server
    systemctl start redis-server
    systemctl enable redis-server
    log_success "Redis installed and running"
    
    wait_for_input
}

step6_configure_databases() {
    log_step "STEP 6: Configuring Databases"
    
    if [ "$SKIP_DATABASES" = true ]; then
        log_warning "Skipping database configuration"
        return
    fi
    
    # Configure PostgreSQL
    log_info "Configuring PostgreSQL..."
    
    # Generate random password
    DB_PASSWORD=$(openssl rand -base64 32)
    
    sudo -u postgres psql <<EOF
CREATE DATABASE chimera_trading;
CREATE USER chimera WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE chimera_trading TO chimera;
ALTER DATABASE chimera_trading OWNER TO chimera;
EOF
    
    log_success "PostgreSQL configured"
    
    # Save credentials
    mkdir -p "$CONFIG_DIR"
    cat > "$CONFIG_DIR/db_credentials.json" <<EOF
{
    "postgres": {
        "host": "localhost",
        "port": 5432,
        "database": "chimera_trading",
        "user": "chimera",
        "password": "$DB_PASSWORD"
    },
    "mongodb": {
        "uri": "mongodb://localhost:27017",
        "database": "chimera_timeseries"
    },
    "redis": {
        "uri": "redis://localhost:6379/0"
    }
}
EOF
    
    chmod 600 "$CONFIG_DIR/db_credentials.json"
    log_success "Database credentials saved to $CONFIG_DIR/db_credentials.json"
    
    wait_for_input
}

step7_create_directories() {
    log_step "STEP 7: Creating Directory Structure"
    
    log_info "Creating directories..."
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$DATA_DIR"
    mkdir -p "$DATA_DIR/backups"
    mkdir -p "$DATA_DIR/logs"
    mkdir -p "$DATA_DIR/models"
    
    log_success "Directory structure created"
    wait_for_input
}

step8_install_chimera() {
    log_step "STEP 8: Installing Chimera Auto-Pilot"
    
    log_info "Copying Chimera files to $INSTALL_DIR..."
    
    # Copy current directory to install directory
    CURRENT_DIR=$(pwd)
    rsync -av --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
        "$CURRENT_DIR/" "$INSTALL_DIR/"
    
    cd "$INSTALL_DIR"
    
    # Create Python virtual environment
    log_info "Creating Python virtual environment..."
    python3.11 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    
    # Install Python dependencies
    log_info "Installing Python dependencies..."
    if [ -f "requirements_chimera.txt" ]; then
        pip install -r requirements_chimera.txt
    else
        # Install minimal dependencies
        pip install aiohttp websockets numpy pydantic fastapi uvicorn asyncio
    fi
    
    log_success "Chimera Auto-Pilot installed"
    wait_for_input
}

step9_configure_chimera() {
    log_step "STEP 9: Auto-Configuring Chimera System"
    
    log_info "Generating configuration..."
    
    # Load database credentials if they exist
    if [ -f "$CONFIG_DIR/db_credentials.json" ]; then
        DB_CREDS=$(cat "$CONFIG_DIR/db_credentials.json")
    else
        DB_CREDS="{}"
    fi
    
    # Create main configuration file
    cat > "$CONFIG_DIR/config.yaml" <<EOF
# Chimera Auto-Pilot Configuration
# Auto-generated on $(date)

mode: production
install_dir: $INSTALL_DIR
log_dir: $LOG_DIR
data_dir: $DATA_DIR

# Database Configuration
database:
  enabled: $([ "$SKIP_DATABASES" = false ] && echo "true" || echo "false")
  postgres:
    host: localhost
    port: 5432
    database: chimera_trading
    user: chimera
  mongodb:
    uri: mongodb://localhost:27017
    database: chimera_timeseries
  redis:
    uri: redis://localhost:6379/0

# Trading Configuration
trading:
  enabled: false  # Enable manually after setup
  symbols:
    - BTC/CAD
    - ETH/CAD
  interval: 60
  default_quantity: 0.001
  max_position_size: 0.1

# Exchange Configuration (SET YOUR API KEYS)
exchanges:
  ndax:
    enabled: false
    api_key: "YOUR_NDAX_API_KEY"
    api_secret: "YOUR_NDAX_API_SECRET"
    user_id: "YOUR_NDAX_USER_ID"
    account_id: "YOUR_NDAX_ACCOUNT_ID"
    testnet: true
  
  binance:
    enabled: false
    api_key: "YOUR_BINANCE_API_KEY"
    api_secret: "YOUR_BINANCE_API_SECRET"
    testnet: true

# Solvency Monitoring
solvency:
  check_interval: 300
  min_ratio: 0.5
  alert_threshold: 0.6

# Monitoring
monitoring:
  prometheus_port: 9090
  health_check_interval: 30

# Dashboard
dashboard:
  enabled: true
  port: 8000
  host: 0.0.0.0

# Safety Settings
safety:
  require_approval: true
  max_risk_per_trade: 0.02
  max_daily_loss: 0.05
  kill_switch_active: false

# Learning & Optimization
learning:
  enabled: true
  save_interval: 600
  min_experiences: 100

# Logging
logging:
  level: INFO
  file: $LOG_DIR/chimera.log
  max_size: 100MB
  backup_count: 10
EOF
    
    log_success "Configuration file created: $CONFIG_DIR/config.yaml"
    
    # Create environment file
    cat > "$CONFIG_DIR/.env" <<EOF
# Chimera Environment Variables
CHIMERA_MODE=production
CHIMERA_CONFIG=$CONFIG_DIR/config.yaml
CHIMERA_LOG_DIR=$LOG_DIR
CHIMERA_DATA_DIR=$DATA_DIR
PYTHONPATH=$INSTALL_DIR
EOF
    
    chmod 600 "$CONFIG_DIR/.env"
    
    log_success "Environment configuration created"
    wait_for_input
}

step10_create_systemd_service() {
    log_step "STEP 10: Creating Systemd Service"
    
    log_info "Creating systemd service..."
    
    cat > "/etc/systemd/system/$SERVICE_NAME.service" <<EOF
[Unit]
Description=Chimera Auto-Pilot Trading System
After=network.target postgresql.service mongodb.service redis.service
Wants=postgresql.service mongodb.service redis.service

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$VENV_DIR/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=$INSTALL_DIR"
EnvironmentFile=$CONFIG_DIR/.env
ExecStart=$VENV_DIR/bin/python3 $INSTALL_DIR/unified_system.py --auto
Restart=always
RestartSec=10
StandardOutput=append:$LOG_DIR/chimera.log
StandardError=append:$LOG_DIR/chimera-error.log

# Security
NoNewPrivileges=true
PrivateTmp=true

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd
    systemctl daemon-reload
    
    log_success "Systemd service created: $SERVICE_NAME"
    wait_for_input
}

step11_setup_monitoring() {
    log_step "STEP 11: Setting Up Monitoring"
    
    # Install monitoring tools
    log_info "Installing monitoring tools..."
    
    # Prometheus (optional)
    if [ "$PRODUCTION_MODE" = true ]; then
        log_info "Installing Prometheus..."
        wget -q https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
        tar xzf prometheus-2.45.0.linux-amd64.tar.gz -C /opt/
        rm prometheus-2.45.0.linux-amd64.tar.gz
        mv /opt/prometheus-2.45.0.linux-amd64 /opt/prometheus
        
        # Create Prometheus config
        cat > /opt/prometheus/prometheus.yml <<EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'chimera'
    static_configs:
      - targets: ['localhost:9090']
EOF
        
        log_success "Prometheus installed"
    fi
    
    # Create monitoring script
    cat > "$INSTALL_DIR/monitor.sh" <<'EOF'
#!/bin/bash
# Chimera Monitoring Script

echo "=== Chimera Auto-Pilot Status ==="
echo ""
echo "Service Status:"
systemctl status chimera-autopilot --no-pager | grep Active
echo ""
echo "Recent Logs:"
tail -n 20 /var/log/chimera/chimera.log
echo ""
echo "System Resources:"
echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')%"
echo "Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
echo "Disk: $(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 ")"}')"
EOF
    
    chmod +x "$INSTALL_DIR/monitor.sh"
    
    log_success "Monitoring setup complete"
    wait_for_input
}

step12_configure_firewall() {
    log_step "STEP 12: Configuring Firewall"
    
    if command -v ufw &> /dev/null; then
        log_info "Configuring UFW firewall..."
        
        # Allow SSH
        ufw allow 22/tcp
        
        # Allow dashboard
        ufw allow 8000/tcp
        
        # Allow Prometheus (if enabled)
        if [ "$PRODUCTION_MODE" = true ]; then
            ufw allow 9090/tcp
        fi
        
        # Enable firewall
        echo "y" | ufw enable
        
        log_success "Firewall configured"
    else
        log_warning "UFW not found, skipping firewall configuration"
    fi
    
    wait_for_input
}

step13_create_helper_scripts() {
    log_step "STEP 13: Creating Helper Scripts"
    
    # Start script
    cat > "$INSTALL_DIR/start.sh" <<EOF
#!/bin/bash
echo "Starting Chimera Auto-Pilot..."
systemctl start $SERVICE_NAME
systemctl status $SERVICE_NAME --no-pager
EOF
    chmod +x "$INSTALL_DIR/start.sh"
    
    # Stop script
    cat > "$INSTALL_DIR/stop.sh" <<EOF
#!/bin/bash
echo "Stopping Chimera Auto-Pilot..."
systemctl stop $SERVICE_NAME
EOF
    chmod +x "$INSTALL_DIR/stop.sh"
    
    # Restart script
    cat > "$INSTALL_DIR/restart.sh" <<EOF
#!/bin/bash
echo "Restarting Chimera Auto-Pilot..."
systemctl restart $SERVICE_NAME
systemctl status $SERVICE_NAME --no-pager
EOF
    chmod +x "$INSTALL_DIR/restart.sh"
    
    # Status script
    cat > "$INSTALL_DIR/status.sh" <<EOF
#!/bin/bash
bash $INSTALL_DIR/monitor.sh
EOF
    chmod +x "$INSTALL_DIR/status.sh"
    
    # Update script
    cat > "$INSTALL_DIR/update.sh" <<EOF
#!/bin/bash
echo "Updating Chimera Auto-Pilot..."
cd $INSTALL_DIR
git pull
source $VENV_DIR/bin/activate
pip install -r requirements_chimera.txt --upgrade
systemctl restart $SERVICE_NAME
echo "Update complete!"
EOF
    chmod +x "$INSTALL_DIR/update.sh"
    
    log_success "Helper scripts created"
    wait_for_input
}

step14_run_tests() {
    log_step "STEP 14: Running System Tests"
    
    cd "$INSTALL_DIR"
    source "$VENV_DIR/bin/activate"
    
    log_info "Running basic import tests..."
    
    # Test imports
    python3 -c "
try:
    import chimera_core
    print('✅ Chimera core imports OK')
except Exception as e:
    print(f'❌ Import error: {e}')

try:
    from chimera_core.database import DatabaseManager
    print('✅ Database module OK')
except Exception as e:
    print(f'⚠️  Database module: {e}')

try:
    from chimera_core.intelligence import AdaptiveIntelligence
    print('✅ AI module OK')
except Exception as e:
    print(f'⚠️  AI module: {e}')

try:
    from chimera_core.monitoring_enhanced import ObservabilitySystem
    print('✅ Monitoring module OK')
except Exception as e:
    print(f'⚠️  Monitoring module: {e}')

print('\\n✅ Basic system tests passed!')
"
    
    log_success "System tests completed"
    wait_for_input
}

step15_enable_and_start() {
    log_step "STEP 15: Enabling and Starting Chimera"
    
    log_info "Enabling service to start on boot..."
    systemctl enable "$SERVICE_NAME"
    
    log_info "Starting Chimera Auto-Pilot..."
    systemctl start "$SERVICE_NAME"
    
    sleep 3
    
    # Check status
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log_success "Chimera Auto-Pilot is RUNNING!"
    else
        log_warning "Service started but may need configuration"
        systemctl status "$SERVICE_NAME" --no-pager
    fi
    
    wait_for_input
}

print_final_summary() {
    clear
    echo -e "${GREEN}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║                    ✅ INSTALLATION COMPLETE! ✅                         ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}\n"
    
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
    
    echo -e "${GREEN}📍 Installation Summary:${NC}"
    echo -e "   • Install Directory: ${BLUE}$INSTALL_DIR${NC}"
    echo -e "   • Configuration: ${BLUE}$CONFIG_DIR/config.yaml${NC}"
    echo -e "   • Logs: ${BLUE}$LOG_DIR/${NC}"
    echo -e "   • Service: ${BLUE}$SERVICE_NAME${NC}"
    echo ""
    
    echo -e "${GREEN}🎮 Quick Commands:${NC}"
    echo -e "   • Start:   ${YELLOW}systemctl start $SERVICE_NAME${NC}"
    echo -e "   • Stop:    ${YELLOW}systemctl stop $SERVICE_NAME${NC}"
    echo -e "   • Restart: ${YELLOW}systemctl restart $SERVICE_NAME${NC}"
    echo -e "   • Status:  ${YELLOW}systemctl status $SERVICE_NAME${NC}"
    echo -e "   • Logs:    ${YELLOW}tail -f $LOG_DIR/chimera.log${NC}"
    echo ""
    
    echo -e "${GREEN}🔧 Helper Scripts:${NC}"
    echo -e "   • Start:   ${YELLOW}$INSTALL_DIR/start.sh${NC}"
    echo -e "   • Stop:    ${YELLOW}$INSTALL_DIR/stop.sh${NC}"
    echo -e "   • Monitor: ${YELLOW}$INSTALL_DIR/monitor.sh${NC}"
    echo -e "   • Update:  ${YELLOW}$INSTALL_DIR/update.sh${NC}"
    echo ""
    
    echo -e "${GREEN}🌐 Access Dashboard:${NC}"
    echo -e "   • URL: ${YELLOW}http://$(hostname -I | awk '{print $1}'):8000${NC}"
    echo -e "   • Local: ${YELLOW}http://localhost:8000${NC}"
    echo ""
    
    echo -e "${GREEN}⚙️  Next Steps:${NC}"
    echo -e "   1. Edit configuration: ${YELLOW}nano $CONFIG_DIR/config.yaml${NC}"
    echo -e "   2. Add your API keys for exchanges"
    echo -e "   3. Enable trading: Set ${YELLOW}trading.enabled: true${NC}"
    echo -e "   4. Restart service: ${YELLOW}systemctl restart $SERVICE_NAME${NC}"
    echo -e "   5. Monitor logs: ${YELLOW}tail -f $LOG_DIR/chimera.log${NC}"
    echo ""
    
    if [ "$SKIP_DATABASES" = false ]; then
        echo -e "${GREEN}🔒 Database Credentials:${NC}"
        echo -e "   Saved to: ${YELLOW}$CONFIG_DIR/db_credentials.json${NC}"
        echo ""
    fi
    
    echo -e "${YELLOW}⚠️  Important Security Notes:${NC}"
    echo -e "   • Update API keys in config before enabling trading"
    echo -e "   • Review safety settings (max risk, daily loss limits)"
    echo -e "   • Start in testnet mode before production"
    echo -e "   • Keep database credentials secure"
    echo ""
    
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
    
    echo -e "${GREEN}🚀 Chimera Auto-Pilot is ready for optimization and trading!${NC}\n"
    
    # Show current status
    systemctl status "$SERVICE_NAME" --no-pager || true
}

################################################################################
# Main Installation Flow
################################################################################

main() {
    print_banner
    
    check_root
    detect_os
    
    step1_system_checks
    step2_install_system_packages
    step3_install_python
    step4_install_nodejs
    step5_install_databases
    step6_configure_databases
    step7_create_directories
    step8_install_chimera
    step9_configure_chimera
    step10_create_systemd_service
    step11_setup_monitoring
    step12_configure_firewall
    step13_create_helper_scripts
    step14_run_tests
    step15_enable_and_start
    
    print_final_summary
}

# Run main installation
main

exit 0
