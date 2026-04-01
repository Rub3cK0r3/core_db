#!/usr/bin/env bash
set -e
# Installer script for installing all the dependencies located in this project before running it
APP_NAME="3v3nTr4cer"
INSTALL_DIR="/opt/$APP_NAME"
REPO_URL="https://github.com/Rub3cK0r3/3v3nTr4cer.git"
echo "[+] Installing $APP_NAME (Docker mode)"

detect_pm() {
    if command -v apt >/dev/null; then
        PM="apt"
    elif command -v dnf >/dev/null; then
        PM="dnf"
    elif command -v yum >/dev/null; then
        PM="yum"
    elif command -v pacman >/dev/null; then
        PM="pacman"
    else
        echo "Unknown distro..."
        exit 1
    fi
}

install_docker() {
    echo "[+] Installing Docker..."

    case $PM in
        apt)
            sudo apt update
            sudo apt install -y docker.io docker-compose git curl
            ;;
        dnf|yum)
            sudo $PM install -y docker docker-compose git curl
            ;;
        pacman)
            sudo pacman -Sy --noconfirm docker docker-compose git curl
            ;;
    esac

    sudo systemctl enable docker
    sudo systemctl start docker

    # Add user to docker group
    sudo usermod -aG docker $USER || true

    echo "You may need to log out/in for docker group to apply..."
}

setup_app() {
    echo "Cloning repository..."

    sudo rm -rf $INSTALL_DIR
    sudo git clone $REPO_URL $INSTALL_DIR
    sudo chown -R $USER:$USER $INSTALL_DIR

    cd $INSTALL_DIR
}

detect_pm
install_docker
setup_app

echo "Installation complete..!"

######################
# Author : Rub3ck0r3 #
######################
