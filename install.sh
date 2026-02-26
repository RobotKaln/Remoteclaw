#!/bin/bash
#
# RemoteClaw e-Paper Display Service Installer
# For Raspberry Pi Zero 2W + Waveshare 2.13" e-Paper HAT V3
#

set -e

REPO_URL="https://github.com/waveshare/e-Paper.git"
INSTALL_DIR="/home/pi/Remoteclaw"
SERVICE_NAME="remoteclaw-display"

print_header() {
    echo "=========================================="
    echo "  RemoteClaw Display Service Installer"
    echo "=========================================="
    echo ""
}

check_root() {
    if [[ $EUID -eq 0 ]]; then
        echo "[WARNING] Running as root. This script should run as user 'pi' with sudo."
        echo "[INFO] Continuing anyway..."
    fi
}

check_dependencies() {
    echo "[1/7] Checking dependencies..."
    
    # Check Python3
    if ! command -v python3 &> /dev/null; then
        echo "[ERROR] Python3 not found. Please install it first."
        exit 1
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        echo "[INFO] Installing pip3..."
        sudo apt-get update
        sudo apt-get install -y python3-pip
    fi
    
    # Check SPI
    if ! [ -e /dev/spidev0.0 ]; then
        echo "[WARNING] SPI not enabled. Enabling now..."
        sudo raspi-config nonint do_spi 0
        echo "[INFO] SPI enabled. Reboot required after installation."
        NEEDS_REBOOT=1
    fi
    
    # Check I2C
    if ! [ -e /dev/i2c-1 ]; then
        echo "[WARNING] I2C not enabled. Enabling now..."
        sudo raspi-config nonint do_i2c 0
        echo "[INFO] I2C enabled. Reboot required after installation."
        NEEDS_REBOOT=1
    fi
    
    echo "[INFO] Dependencies check complete."
}

install_system_packages() {
    echo "[2/7] Installing system packages..."
    sudo apt-get update
    sudo apt-get install -y \
        python3-pil \
        python3-numpy \
        libatlas-base-dev \
        git \
        2>/dev/null || true
    echo "[INFO] System packages installed."
}

install_waveshare_lib() {
    echo "[3/7] Installing Waveshare e-Paper library..."
    
    if [ -d "/home/pi/e-Paper" ]; then
        echo "[INFO] Waveshare library already exists at /home/pi/e-Paper"
        cd /home/pi/e-Paper
        git pull origin master 2>/dev/null || true
    else
        echo "[INFO] Cloning Waveshare e-Paper repository..."
        cd /home/pi
        git clone $REPO_URL || true
    fi
    
    # Install Python library
    if [ -d "/home/pi/e-Paper/RaspberryPi_JetsonNano/python" ]; then
        echo "[INFO] Installing waveshare-epd via pip..."
        pip3 install waveshare-epd || {
            echo "[WARNING] pip install failed, trying manual install..."
            cd /home/pi/e-Paper/RaspberryPi_JetsonNano/python
            sudo python3 setup.py install 2>/dev/null || pip3 install . --user || true
        }
    fi
    
    echo "[INFO] Waveshare library setup complete."
}

install_service_files() {
    echo "[4/7] Installing service files..."
    
    # Create install directory
    mkdir -p $INSTALL_DIR
    
    # Copy service script
    if [ -f "display_service.py" ]; then
        cp display_service.py $INSTALL_DIR/
        chmod +x $INSTALL_DIR/display_service.py
        echo "[INFO] Copied display_service.py"
    else
        echo "[ERROR] display_service.py not found in current directory"
        exit 1
    fi
    
    # Copy service file
    if [ -f "remoteclaw-display.service" ]; then
        sudo cp remoteclaw-display.service /etc/systemd/system/
        sudo systemctl daemon-reload
        echo "[INFO] Installed systemd service file"
    else
        echo "[ERROR] remoteclaw-display.service not found"
        exit 1
    fi
    
    # Fix permissions
    sudo chown -R pi:pi $INSTALL_DIR
    
    echo "[INFO] Service files installed."
}

create_message_file() {
    echo "[5/7] Creating message file..."
    
    # Create the message file with sample data
    MESSAGE_FILE="/tmp/remoteclaw-messages.json"
    cat > $MESSAGE_FILE << 'EOF'
{
    "message": "Display service initialized. Waiting for OpenClaw messages...",
    "timestamp": "$(date +%s)",
    "source": "install"
}
EOF
    
    sudo chmod 666 $MESSAGE_FILE
    echo "[INFO] Created $MESSAGE_FILE"
}

enable_service() {
    echo "[6/7] Enabling service..."
    sudo systemctl enable $SERVICE_NAME.service
    echo "[INFO] Service enabled to start on boot."
}

start_service() {
    echo "[7/7] Starting service..."
    
    if [ "$NEEDS_REBOOT" = "1" ]; then
        echo "[WARNING] SPI/I2C was enabled. Please reboot before starting service."
        echo "[INFO] After reboot, run: sudo systemctl start $SERVICE_NAME"
        return 0
    fi
    
    sudo systemctl start $SERVICE_NAME.service || {
        echo "[WARNING] Service failed to start. Check: sudo systemctl status $SERVICE_NAME"
    }
    
    sleep 2
    
    # Check status
    if systemctl is-active --quiet $SERVICE_NAME.service; then
        echo "[SUCCESS] Service is running!"
    else
        echo "[WARNING] Service may need manual troubleshooting."
        echo "[INFO] Check status with: sudo systemctl status $SERVICE_NAME"
    fi
}

print_footer() {
    echo ""
    echo "=========================================="
    echo "  Installation Complete!"
    echo "=========================================="
    echo ""
    echo "Service commands:"
    echo "  sudo systemctl start $SERVICE_NAME   - Start service"
    echo "  sudo systemctl stop $SERVICE_NAME    - Stop service"
    echo "  sudo systemctl status $SERVICE_NAME  - Check status"
    echo "  sudo journalctl -u $SERVICE_NAME -f  - View logs"
    echo ""
    echo "Test display: python3 $INSTALL_DIR/display_service.py"
    echo ""
    
    if [ "$NEEDS_REBOOT" = "1" ]; then
        echo "[IMPORTANT] Reboot required: sudo reboot"
    fi
}

# Main
check_root
check_dependencies
install_system_packages
install_waveshare_lib
install_service_files
create_message_file
enable_service
start_service
print_header
print_footer
