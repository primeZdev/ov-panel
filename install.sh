#!/bin/bash
set -e

APP_NAME="ov-panel"
INSTALL_DIR="/opt/$APP_NAME"
REPO_URL="https://github.com/primeZdev/ov-panel"
PYTHON="/usr/bin/python3"

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m"

apt update -y
apt install -y python3 python3-pip wget curl git -y
pip3 install --upgrade pip
pip3 install colorama pexpect requests uuid uv

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