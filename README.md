# RemoteClaw - RPi OpenClaw Node with e-Paper Display

Raspberry Pi Zero 2W based OpenClaw node with camera and e-Paper status display.

## Hardware

- **Raspberry Pi Zero 2W**  
- **Raspberry Pi Camera Module 3** (CSI port)  
- **Waveshare 2.13inch e-Paper HAT V3** (SPI/I2C)  

## Wiring

### Camera Module 3
CSI ribbon cable → Pi CSI port (no adapter needed for Zero 2W).

### e-Paper HAT GPIO Pinout

| e-Paper | GPIO | Pin |
|---------|------|-----|
| VCC | 3.3V | 1/17 |
| GND | GND | 6/9/14... |
| DIN | GPIO10 (MOSI) | 19 |
| CLK | GPIO11 (SCLK) | 23 |
| CS | GPIO8 (CE0) | 24 |
| DC | GPIO25 | 22 |
| RST | GPIO17 | 11 |
| BUSY | GPIO24 | 18 |

Stack the HAT directly on GPIO pins.

## Quick Setup

### 1. System Setup

```bash
# Enable interfaces
sudo raspi-config nonint do_camera 0
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0
sudo reboot
```

### 2. Install Dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-pil python3-numpy libatlas-base-dev git -y
```

### 3. Install RemoteClaw Display Service

```bash
git clone https://github.com/RobotKaln/Remoteclaw.git
cd Remoteclaw
chmod +x install.sh
./install.sh
```

The installer will:
- Install Waveshare e-Paper library
- Setup systemd service `remoteclaw-display`
- Enable auto-start on boot

### 4. Install OpenClaw

```bash
# Node.js required first
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install OpenClaw CLI
npm install -g openclaw

# Configure OpenClaw
openclaw config set nodes.enabled=true
```

## Display Service

The display service (`display_service.py`) shows:

- **RemoteClaw Pi Node** header
- **OpenClaw status**: running/stopped
- **Connected nodes count**
- **Last message** from `/tmp/remoteclaw-messages.json`
- **Timestamp** (auto-refreshes every 30 seconds)

### Service Management

```bash
# Check status
sudo systemctl status remoteclaw-display

# Start/stop/restart
sudo systemctl start remoteclaw-display
sudo systemctl stop remoteclaw-display
sudo systemctl restart remoteclaw-display

# View logs
sudo journalctl -u remoteclaw-display -f
```

### Manual Run

```bash
# For testing without systemd
python3 /home/pi/Remoteclaw/display_service.py
```

## OpenClaw Node Usage

### Pair the Node

```bash
# Get pairing token from main Gateway
openclaw nodes pairing
```

### Camera Commands

```bash
# Take a photo
openclaw nodes camera_snap front

# List cameras
openclaw nodes camera_list

# Screen record (to OpenClaw)
openclaw nodes screen_record outPath=/tmp/recording.mp4 duration=10s
```

### Send Notifications

```bash
openclaw nodes notify "Alert from Raspberry Pi!"
```

## Message File Format

Write to `/tmp/remoteclaw-messages.json` to update display:

```json
{
  "message": "Hello from OpenClaw!",
  "timestamp": "2026-02-26T10:15:00Z"
}
```

Example script:
```bash
echo '{"message": "Status: All systems nominal", "timestamp": "'$(date -Iseconds)'"}' > /tmp/remoteclaw-messages.json
```

## Files

| File | Purpose |
|------|---------|
| `display_service.py` | Main display service script |
| `remoteclaw-display.service` | systemd service definition |
| `install.sh` | One-line installer script |

## Troubleshooting

### Display Not Working
- Check SPI/I2C enabled: `ls /dev/spi*` and `ls /dev/i2c*`
- Check wiring connections
- Run `sudo raspi-config` → Interface Options → enable SPI/I2C
- View logs: `sudo journalctl -u remoteclaw-display -n 50`

### Camera Not Detected
```bash
vcgencmd get_camera
libcamera-hello --list-cameras
```

### Node Commands Fail
- Verify OpenClaw gateway is running: `openclaw gateway status`
- Check OpenClaw config: `openclaw config show`

## License

MIT

## Links

- Waveshare e-Paper Library: https://github.com/waveshare/e-Paper
- OpenClaw: https://github.com/openclaw/openclaw
