#!/bin/bash
set -e

APP_NAME="ov-panel"
INSTALL_DIR="/opt/$APP_NAME"
REPO_URL="https://github.com/primeZdev/ov-panel"
PYTHON="/usr/bin/python3"

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
BLUE="\033[0;34m"
RED="\033[0;31m"
BOLD="\033[1m"
NC="\033[0m"

get_server_ip() {
    local ip=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "Unable to detect")
    echo "$ip"
}

get_version() {
    if [ -f "backend/version.py" ]; then
        local version=$(grep -o '"[^"]*"' "backend/version.py" | head -1 | tr -d '"')
        echo "v$version"
    fi
}

show_welcome_banner() {
    clear
    echo -e "${CYAN}${BOLD}"
    echo "  ██████╗ ██╗   ██╗██████╗  █████╗ ███╗   ██╗███████╗██╗     "
    echo " ██╔═══██╗██║   ██║██╔══██╗██╔══██╗████╗  ██║██╔════╝██║     "
    echo " ██║   ██║██║   ██║██████╔╝███████║██╔██╗ ██║█████╗  ██║     "
    echo " ██║   ██║╚██╗ ██╔╝██╔═══╝ ██╔══██║██║╚██╗██║██╔══╝  ██║     "
    echo " ╚██████╔╝ ╚████╔╝ ██║     ██║  ██║██║ ╚████║███████╗███████╗"
    echo "  ╚═════╝   ╚═══╝  ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝"
    echo -e "${NC}"
    echo
    
    local box_width=50
    local title="OVPANEL Installation Setup"
    local padding=$(( (box_width - ${#title}) / 2 ))
    
    echo -e "${YELLOW}${BOLD}"
    printf "╔"
    printf "═%.0s" $(seq 1 $box_width)
    printf "╗\n"
    
    printf "║"
    printf " %.0s" $(seq 1 $padding)
    printf "%s" "$title"
    printf " %.0s" $(seq 1 $(( box_width - padding - ${#title} )))
    printf "║\n"
    
    printf "╚"
    printf "═%.0s" $(seq 1 $box_width)
    printf "╝\n"
    echo -e "${NC}"
    echo
    
    local server_ip=$(get_server_ip)
    local version=$(get_version)
    
    echo -e "${GREEN}• ${BOLD}Version:${NC} ${BLUE}$version${NC}"
    echo -e "${GREEN}• ${BOLD}Server IP:${NC} ${BLUE}$server_ip${NC}"
    echo -e "${GREEN}• ${BOLD}Telegram Channel:${NC} ${BLUE}@OVPanel${NC}"
    echo
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
}

show_welcome_banner

echo -e "${YELLOW}Updating system packages...${NC}"
apt update -y
apt install -y python3 python3-pip python3-venv wget curl git

if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Cloning repository from $REPO_URL...${NC}"
    git clone "$REPO_URL" "$INSTALL_DIR"
else
    echo -e "${YELLOW}Directory exists, pulling latest changes...${NC}"
    cd "$INSTALL_DIR"
    git pull
fi

cd "$INSTALL_DIR"

echo -e "${YELLOW}Creating Python virtual environment...${NC}"
$PYTHON -m venv venv

echo -e "${YELLOW}Installing installer dependencies...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install colorama pexpect requests

echo -e "${GREEN}Starting OV-Panel installer...${NC}"
venv/bin/python installer.py
