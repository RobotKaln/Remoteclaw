# RPi OpenClaw Node: Eyes & Display

## Hardware
- **Raspberry Pi Zero 2W**
- **Raspberry Pi Camera Module 3** (CSI port)
- **Waveshare 2.13inch e-Paper HAT** (SPI/I2C)

## Wiring
### Camera 3
CSI ribbon cable → Pi CSI port (no adapter needed for Zero 2W).

### e-Paper HAT
Stack HAT on GPIO pins. Default SPI0, I2C1.

Pinout:
```
VCC → 3.3V (Pin 1/17)
GND → GND (Pin 6/9/14...)
DIN → GPIO10 (MOSI, Pin 19)
CLK → GPIO11 (SCLK, Pin 23)
CS → GPIO8 (CE0, Pin 24)
DC → GPIO25 (Pin 22)
RST → GPIO17 (Pin 11)
BUSY → GPIO24 (Pin 18)
```

## Setup
1. **Enable interfaces** (raspi-config or CLI):
```
sudo raspi-config nonint do_camera 0
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0
sudo reboot
```

2. **Update**:
```
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-pil python3-numpy libatlas-base-dev -y
sudo reboot
```

3. **Camera**:
```
sudo apt install libcamera-apps -y
libcamera-hello --list-cameras
```

4. **e-Paper**:
```
git clone https://github.com/waveshare/e-Paper
cd e-Paper/RaspberryPi_JetsonNano/python/lib
pip3 install .
cd examples
python3 epd_2in13_V3_test.py  # test
```

5. **OpenClaw nodes**:
- Gateway config: nodes.enabled=true
- `nodes status`
- `nodes camera_list`
- `nodes screen_record` (e-Paper as canvas?)

## Software
- OpenClaw on Pi: `npm i -g openclaw`
- Pair node: `nodes pairing` (QR/ token from main Gateway)

## Usage
- Camera snap: `nodes camera_snap front`
- Screen: `nodes screen_record outPath=test.mp4 duration=10`
- Notify: `nodes notify "Hello from Pi!"`

## Troubleshooting
- Camera not detected: `vcgencmd get_camera`
- e-Paper blank: check wiring, busy pin.
- Nodes: gatewayUrl/token in config.

Commit history for changes.
