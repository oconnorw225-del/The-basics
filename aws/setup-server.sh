#!/bin/bash

################################################################################
# AWS Server Setup Script for Chimera System
# 
# This script sets up a fresh AWS EC2 instance with all required dependencies
# and configures the Chimera autonomous system for production deployment.
#
# Usage:
#   bash setup-server.sh                  # Interactive setup
#   bash setup-server.sh --auto           # Automated setup with defaults
#   bash setup-server.sh --minimal        # Minimal install (no databases)
#
# Requirements:
#   - Ubuntu 20.04 LTS or newer
#   - Minimum 2GB RAM, 4GB recommended
#   - 20GB free disk space
################################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuration
INSTALL_DIR="/opt/chimera"
LOG_DIR="/var/log/chimera"
SERVICE_USER="chimera"
PYTHON_VERSION="3.11"

# Parse arguments
AUTO_MODE=false
MINIMAL_MODE=false

for arg in "$@"; do
    case $arg in
        --auto)
            AUTO_MODE=true
            ;;
        --minimal)
            MINIMAL_MODE=true
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
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_step() {
    echo -e "\n${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${PURPLE}▶ $1${NC}"
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root. Use: sudo bash setup-server.sh"
        exit 1
    fi
}

################################################################################
# Installation Steps
################################################################################

print_banner() {
    echo -e "${PURPLE}"
    cat << "EOF"
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║        ██████╗██╗  ██╗██╗███╗   ███╗███████╗██████╗  ██╗     ║
    ║       ██╔════╝██║  ██║██║████╗ ████║██╔════╝██╔══██╗███║     ║
    ║       ██║     ███████║██║██╔████╔██║█████╗  ██████╔╝╚██║     ║
    ║       ██║     ██╔══██║██║██║╚██╔╝██║██╔══╝  ██╔══██╗ ██║     ║
    ║       ╚██████╗██║  ██║██║██║ ╚═╝ ██║███████╗██║  ██║ ██║     ║
    ║        ╚═════╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═╝     ║
    ║                                                               ║
    ║              AWS Server Setup - Production Ready             ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

update_system() {
    log_step "Updating system packages"
    apt-get update -qq
    apt-get upgrade -y -qq
    log_success "System updated"
}

install_dependencies() {
    log_step "Installing system dependencies"
    
    apt-get install -y -qq \
        software-properties-common \
        build-essential \
        curl \
        wget \
        git \
        vim \
        htop \
        net-tools \
        ufw \
        fail2ban \
        certbot \
        python3-certbot-nginx \
        nginx \
        supervisor \
        redis-server \
        postgresql \
        postgresql-contrib \
        libpq-dev \
        python3-pip \
        python3-venv \
        python3-dev \
        nodejs \
        npm
    
    log_success "System dependencies installed"
}

setup_python() {
    log_step "Setting up Python $PYTHON_VERSION"
    
    # Add deadsnakes PPA for latest Python
    add-apt-repository -y ppa:deadsnakes/ppa
    apt-get update -qq
    
    # Install Python and venv
    apt-get install -y -qq \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-venv \
        python${PYTHON_VERSION}-dev
    
    # Set as default
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1
    
    # Upgrade pip
    python3 -m pip install --upgrade pip setuptools wheel
    
    log_success "Python $PYTHON_VERSION installed and configured"
}

setup_nodejs() {
    log_step "Setting up Node.js"
    
    # Install latest LTS version
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
    
    # Update npm
    npm install -g npm@latest
    
    log_success "Node.js $(node --version) and npm $(npm --version) installed"
}

create_service_user() {
    log_step "Creating service user"
    
    if ! id -u "$SERVICE_USER" > /dev/null 2>&1; then
        useradd -r -m -s /bin/bash "$SERVICE_USER"
        log_success "User '$SERVICE_USER' created"
    else
        log_info "User '$SERVICE_USER' already exists"
    fi
}

setup_directories() {
    log_step "Setting up directories"
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p /etc/chimera
    
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
    chown -R "$SERVICE_USER:$SERVICE_USER" "$LOG_DIR"
    
    log_success "Directories created and configured"
}

setup_firewall() {
    log_step "Configuring firewall"
    
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow http
    ufw allow https
    ufw allow 8000/tcp  # API
    ufw --force enable
    
    log_success "Firewall configured"
}

setup_postgresql() {
    if [ "$MINIMAL_MODE" = true ]; then
        log_info "Skipping PostgreSQL setup (minimal mode)"
        return
    fi
    
    log_step "Configuring PostgreSQL"
    
    # Generate secure random password
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
    
    sudo -u postgres psql -c "CREATE USER chimera WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || true
    sudo -u postgres psql -c "CREATE DATABASE chimera OWNER chimera;" 2>/dev/null || true
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE chimera TO chimera;" 2>/dev/null || true
    
    # Save password to secure file
    echo "DB_PASSWORD=$DB_PASSWORD" >> /etc/chimera/secrets.env
    chmod 600 /etc/chimera/secrets.env
    
    # Enable and start PostgreSQL
    systemctl enable postgresql
    systemctl start postgresql
    
    log_success "PostgreSQL configured (password saved to /etc/chimera/secrets.env)"
}

setup_redis() {
    if [ "$MINIMAL_MODE" = true ]; then
        log_info "Skipping Redis setup (minimal mode)"
        return
    fi
    
    log_step "Configuring Redis"
    
    # Generate secure random password
    REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
    
    # Configure Redis for production
    sed -i 's/^bind 127.0.0.1/bind 127.0.0.1/' /etc/redis/redis.conf
    sed -i "s/^# requirepass.*/requirepass $REDIS_PASSWORD/" /etc/redis/redis.conf
    
    # Save password to secure file
    echo "REDIS_PASSWORD=$REDIS_PASSWORD" >> /etc/chimera/secrets.env
    chmod 600 /etc/chimera/secrets.env
    
    # Enable and start Redis
    systemctl enable redis-server
    systemctl start redis-server
    
    log_success "Redis configured (password saved to /etc/chimera/secrets.env)"
}

setup_nginx() {
    log_step "Configuring Nginx"
    
    cat > /etc/nginx/sites-available/chimera << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
    
    # Enable site
    ln -sf /etc/nginx/sites-available/chimera /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Test and reload
    nginx -t
    systemctl enable nginx
    systemctl restart nginx
    
    log_success "Nginx configured"
}

setup_supervisor() {
    log_step "Configuring Supervisor"
    
    cat > /etc/supervisor/conf.d/chimera.conf << EOF
[program:chimera]
command=/opt/chimera/venv/bin/python3 /opt/chimera/unified_system.py --auto
directory=/opt/chimera
user=$SERVICE_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$LOG_DIR/chimera.log
environment=PATH="/opt/chimera/venv/bin"
EOF
    
    systemctl enable supervisor
    systemctl restart supervisor
    
    log_success "Supervisor configured"
}

clone_repository() {
    log_step "Cloning Chimera repository"
    
    cd /tmp
    if [ -d "The-basics" ]; then
        rm -rf The-basics
    fi
    
    git clone https://github.com/oconnorw225-del/The-basics.git
    
    # Copy to install directory
    cp -r The-basics/* "$INSTALL_DIR/"
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
    
    log_success "Repository cloned"
}

install_python_dependencies() {
    log_step "Installing Python dependencies"
    
    cd "$INSTALL_DIR"
    
    # Create virtual environment
    sudo -u "$SERVICE_USER" python3 -m venv venv
    
    # Install requirements
    if [ -f requirements.txt ]; then
        sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install -r requirements.txt
    fi
    
    log_success "Python dependencies installed"
}

install_node_dependencies() {
    log_step "Installing Node.js dependencies"
    
    cd "$INSTALL_DIR"
    
    if [ -f package.json ]; then
        sudo -u "$SERVICE_USER" npm install
    fi
    
    log_success "Node.js dependencies installed"
}

configure_environment() {
    log_step "Configuring environment"
    
    # Generate secure secrets
    SECRET_KEY=$(openssl rand -base64 32)
    JWT_SECRET=$(openssl rand -base64 32)
    
    # Load database passwords if they were generated
    if [ -f /etc/chimera/secrets.env ]; then
        source /etc/chimera/secrets.env
    else
        # Fallback if running in minimal mode
        DB_PASSWORD="CHANGE_THIS_IN_PRODUCTION"
        REDIS_PASSWORD="CHANGE_THIS_IN_PRODUCTION"
    fi
    
    cat > "$INSTALL_DIR/.env" << EOF
# Chimera Production Configuration
NODE_ENV=production
PYTHON_ENV=production

# Database
DATABASE_URL=postgresql://chimera:${DB_PASSWORD}@localhost/chimera
REDIS_URL=redis://:${REDIS_PASSWORD}@localhost:6379

# API
API_PORT=8000
API_HOST=0.0.0.0

# Security
SECRET_KEY=${SECRET_KEY}
JWT_SECRET=${JWT_SECRET}

# AWS (if using)
AWS_REGION=us-east-1
EOF
    
    chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR/.env"
    chmod 600 "$INSTALL_DIR/.env"
    
    log_success "Environment configured with secure credentials"
}

setup_systemd_service() {
    log_step "Setting up systemd service"
    
    cat > /etc/systemd/system/chimera.service << EOF
[Unit]
Description=Chimera Autonomous System
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
ExecStart=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/unified_system.py --auto
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable chimera
    
    log_success "Systemd service configured"
}

start_services() {
    log_step "Starting services"
    
    # Start via supervisor
    supervisorctl reread
    supervisorctl update
    supervisorctl start chimera
    
    log_success "Services started"
}

print_summary() {
    log_step "Installation Summary"
    
    echo -e "${GREEN}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
    echo -e "${GREEN}┃  ✓ Chimera AWS Server Setup Complete!           ┃${NC}"
    echo -e "${GREEN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
    echo ""
    echo -e "${BLUE}Installation Directory:${NC} $INSTALL_DIR"
    echo -e "${BLUE}Log Directory:${NC} $LOG_DIR"
    echo -e "${BLUE}Service User:${NC} $SERVICE_USER"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Update .env file with your API keys and secrets"
    echo "2. Configure SSL with: certbot --nginx"
    echo "3. Check service status: supervisorctl status chimera"
    echo "4. View logs: tail -f $LOG_DIR/chimera.log"
    echo ""
    echo -e "${BLUE}Useful Commands:${NC}"
    echo "  Start:   supervisorctl start chimera"
    echo "  Stop:    supervisorctl stop chimera"
    echo "  Restart: supervisorctl restart chimera"
    echo "  Status:  supervisorctl status chimera"
    echo ""
}

################################################################################
# Main Installation Flow
################################################################################

main() {
    check_root
    print_banner
    
    update_system
    install_dependencies
    setup_python
    setup_nodejs
    create_service_user
    setup_directories
    setup_firewall
    setup_postgresql
    setup_redis
    setup_nginx
    setup_supervisor
    clone_repository
    install_python_dependencies
    install_node_dependencies
    configure_environment
    setup_systemd_service
    start_services
    
    print_summary
}

# Run main installation
main "$@"
