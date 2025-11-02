#!/bin/bash
set -e

APP_NAME="ov-panel"
INSTALL_DIR="/opt/$APP_NAME"
REPO_URL="https://github.com/primeZdev/ov-panel"

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m"

# Detect system info
detect_system() {
    echo -e "${BLUE}🔍 Detecting system information...${NC}"
    
    if [ -f /etc/os-release ]; then
        source /etc/os-release
        OS_NAME=$NAME
        OS_VERSION=$VERSION_ID
        OS_ID=$ID
    else
        OS_NAME=$(uname -s)
        OS_VERSION=$(uname -r)
        OS_ID="unknown"
    fi
    
    PYTHON_VERSION=$(python3 --version 2>/dev/null | cut -d' ' -f2 || echo "not installed")
    PIP_VERSION=$(pip3 --version 2>/dev/null | cut -d' ' -f2 || echo "not installed")
    
    echo -e "${GREEN}✓ System: $OS_NAME $OS_VERSION${NC}"
    echo -e "${GREEN}✓ Python: $PYTHON_VERSION${NC}"
    echo -e "${GREEN}✓ Pip: $PIP_VERSION${NC}"
}

# Check if system uses externally managed environment
check_externally_managed() {
    if python3 -c "import sys; print(sys.base_prefix != sys.prefix)" 2>/dev/null | grep -q "False"; then
        if [ -f "/etc/python3*/EXTERNALLY-MANAGED" ] || [ -f "/usr/lib/python3*/EXTERNALLY-MANAGED" ]; then
            echo -e "${YELLOW}⚠ System uses externally managed Python environment${NC}"
            return 0
        fi
    fi
    return 1
}

# Install system dependencies
install_dependencies() {
    echo -e "${BLUE}📦 Installing system dependencies...${NC}"
    
    apt update -y
    
    # Base packages
    apt install -y python3 wget curl git
    
    # Detect and install package manager specific packages
    case $OS_ID in
        ubuntu|debian)
            if command -v bc &> /dev/null && [ $(echo "$OS_VERSION >= 23.04" | bc -l 2>/dev/null || echo "0") -eq 1 ]; then
                echo -e "${YELLOW}📝 Ubuntu 23.04+ detected, installing additional packages...${NC}"
                apt install -y python3-pip python3-venv python3-full
            else
                apt install -y python3-pip
            fi
            ;;
        fedora|rhel|centos)
            if command -v dnf &> /dev/null; then
                dnf install -y python3 python3-pip wget curl git
            else
                yum install -y python3 python3-pip wget curl git
            fi
            ;;
        arch|manjaro)
            pacman -Sy --noconfirm python python-pip wget curl git
            ;;
        *)
            echo -e "${YELLOW}⚠ Unknown distribution, trying to install basic packages...${NC}"
            apt install -y python3-pip python3-venv 2>/dev/null || \
            yum install -y python3-pip 2>/dev/null || \
            echo -e "${RED}❌ Cannot install packages automatically${NC}"
            ;;
    esac
    
    # Upgrade pip
    if command -v pip3 &> /dev/null; then
        echo -e "${BLUE}🔄 Upgrading pip...${NC}"
        pip3 install --upgrade pip --break-system-packages 2>/dev/null || \
        pip3 install --upgrade pip
    fi
}

# Install Python packages based on system type
install_python_packages() {
    local packages="colorama pexpect requests uuid uv alembic"
    
    echo -e "${BLUE}🐍 Installing Python packages: $packages${NC}"
    
    if check_externally_managed; then
        echo -e "${YELLOW}📦 Using virtual environment for package installation${NC}"
        
        # Create virtual environment
        if [ ! -d "$INSTALL_DIR/venv" ]; then
            python3 -m venv "$INSTALL_DIR/venv"
        fi
        
        # Install packages in venv
        source "$INSTALL_DIR/venv/bin/activate"
        pip install $packages
        
        # Update Python path to use venv
        export PYTHON="$INSTALL_DIR/venv/bin/python"
        
    else
        echo -e "${GREEN}📦 Installing packages system-wide${NC}"
        
        # Try different installation methods
        pip3 install $packages --break-system-packages 2>/dev/null || \
        pip3 install $packages 2>/dev/null || \
        {
            echo -e "${YELLOW}⚠ Falling back to virtual environment${NC}"
            python3 -m venv "$INSTALL_DIR/venv"
            source "$INSTALL_DIR/venv/bin/activate"
            pip install $packages
            export PYTHON="$INSTALL_DIR/venv/bin/python"
        }
    fi
}

# Download and install application
download_and_install() {
    if [ ! -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}📥 Downloading latest release...${NC}"

    # Try to get latest release URL
    LATEST_URL=$(curl -s https://api.github.com/repos/primeZdev/ov-panel/releases/latest \
        | grep "tarball_url" \
        | cut -d '"' -f 4)

    if [ -z "$LATEST_URL" ]; then
        echo -e "${RED}❌ Cannot fetch latest release URL${NC}"
        echo -e "${YELLOW}🔄 Trying alternative download method...${NC}"
        LATEST_URL="https://github.com/primeZdev/ov-panel/archive/refs/heads/main.tar.gz"
    fi

    mkdir -p "$INSTALL_DIR"
    cd /tmp

    echo -e "${BLUE}⬇️ Downloading from: $LATEST_URL${NC}"
    wget -q --show-progress -O latest.tar.gz "$LATEST_URL"

    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Download failed${NC}"
        exit 1
    fi

    echo -e "${YELLOW}📁 Extracting to $INSTALL_DIR...${NC}"
    tar -xzf latest.tar.gz -C "$INSTALL_DIR" --strip-components=1
    rm -f latest.tar.gz

    echo -e "${GREEN}✅ Download and extraction completed${NC}"
    else
        echo -e "${GREEN}📁 Directory exists, skipping download.${NC}"
    fi
}

# Main installation function
main() {
    echo -e "${BLUE}🚀 Starting smart installation of $APP_NAME${NC}"
    
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}❌ Please run as root${NC}"
        exit 1
    fi
    
    # System detection
    detect_system
    
    # Install dependencies
    install_dependencies
    
    # Download application
    download_and_install
    
    # Install Python packages
    cd "$INSTALL_DIR"
    install_python_packages
    
    # Run installer
    echo -e "${GREEN}🎯 Running installer...${NC}"
    
    # Use appropriate Python executable
    if [ -f "$INSTALL_DIR/venv/bin/python" ]; then
        PYTHON_EXEC="$INSTALL_DIR/venv/bin/python"
    else
        PYTHON_EXEC="python3"
    fi
    
    $PYTHON_EXEC installer.py
    
    echo -e "${GREEN}✨ Installation completed successfully!${NC}"
    echo -e "${BLUE}📖 Installation directory: $INSTALL_DIR${NC}"
    
    if [ -f "$INSTALL_DIR/venv/bin/python" ]; then
        echo -e "${YELLOW}💡 Virtual environment activated at: $INSTALL_DIR/venv${NC}"
        echo -e "${YELLOW}💡 To activate manually: source $INSTALL_DIR/venv/bin/activate${NC}"
    fi
}

# Error handling
trap 'echo -e "${RED}❌ Installation failed at line $LINENO${NC}"; exit 1' ERR

# Run main function
main "$@"
