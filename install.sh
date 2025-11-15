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

apt update -y
apt install -y python3 python3-pip python3-venv wget curl git -y

curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs build-essential

python3 -m pip install colorama pexpect requests uuid uv alembic --break-system-packages


if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Downloading latest release...${NC}"

    LATEST_URL=$(curl -s https://api.github.com/repos/primeZdev/ov-panel/releases/latest \
        | grep "tarball_url" \
        | cut -d '"' -f 4)

    mkdir -p "$INSTALL_DIR"
    cd /tmp

    wget -O latest.tar.gz "$LATEST_URL"

    echo -e "${YELLOW}Extracting...${NC}"
    tar -xzf latest.tar.gz -C "$INSTALL_DIR" --strip-components=1
    rm -f latest.tar.gz

else
    echo -e "${GREEN}Directory exists, skipping download.${NC}"
fi

cd "$INSTALL_DIR"
$PYTHON installer.py