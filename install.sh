#!/bin/bash
set -e

APP_NAME="ov-panel"
INSTALL_DIR="/opt/$APP_NAME"
VENV_DIR="/opt/${APP_NAME}_venv"
REPO_URL="https://github.com/primeZdev/ov-panel"
PYTHON="/usr/bin/python3"

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
BLUE="\033[0;34m"
NC="\033[0m"

    curl -s ifconfig.me 2>/dev/null || echo "Unavailable"
}

show_welcome() {
    clear
    echo -e "${CYAN}"
    echo "██████╗  █████╗ ██╗   ██╗██████╗  █████╗ ███╗   ██╗███████╗██╗     "
    echo "██╔══██╗██╔══██╗██║   ██║██╔══██╗██╔══██╗████╗  ██║██╔════╝██║     "
    echo "██████╔╝███████║██║   ██║██████╔╝███████║██╔██╗ ██║█████╗  ██║     "
    echo "██╔══██╗██╔══██║╚██╗ ██╔╝██╔══██╗██╔══██║██║╚██╗██║██╔══╝  ██║     "
    echo "██████╔╝██║  ██║ ╚████╔╝ ██║  ██║██║  ██║██║ ╚████║███████╗███████╗"
    echo "╚═════╝ ╚═╝  ╚═╝  ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝"
    echo -e "${NC}"
    echo
    echo -e "${GREEN}Server IP:${NC} $(get_server_ip)"
    echo -e "${GREEN}Telegram:${NC} @OVPanel"
    echo
}

show_welcome

echo -e "${YELLOW}Updating system...${NC}"
apt update -y
apt install -y python3 python3-full python3-venv python3-pip wget curl git

# Node.js
echo -e "${YELLOW}Installing NodeJS...${NC}"
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs build-essential

python3 -m venv "$VENV_DIR"

echo -e "${YELLOW}Activating venv...${NC}"
source "$VENV_DIR/bin/activate"

pip install --upgrade pip setuptools wheel

echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install colorama pexpect requests uuid uv alembic

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

echo -e "${YELLOW}Running installer...${NC}"
cd "$INSTALL_DIR"
$VENV_DIR/bin/python installer.py

echo -e "${GREEN}✓ OVPANEL installation completed!${NC}"
