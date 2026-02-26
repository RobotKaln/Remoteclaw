#!/usr/bin/env python3
"""
RemoteClaw e-Paper Display Service
For Raspberry Pi Zero 2W + Waveshare 2.13" e-Paper HAT V3

Displays:
- Last message from /tmp/remoteclaw-messages.json
- Timestamp
- OpenClaw status (running/stopped)
- Connected nodes count

Refreshes every 30 seconds.
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path

# Add Waveshare e-Paper library paths
try:
    from waveshare_epd import epd2in13_V3
except ImportError:
    # Fallback: try common install paths
    sys.path.insert(0, '/home/pi/e-Paper/RaspberryPi_JetsonNano/python/lib')
    sys.path.insert(0, '/opt/e-Paper/RaspberryPi_JetsonNano/python/lib')
    sys.path.insert(0, '/usr/local/lib/python3/dist-packages/waveshare_epd')
    try:
        from waveshare_epd import epd2in13_V3
    except ImportError:
        print("[Error] Could not import Waveshare e-Paper library")
        print("[Error] Install with: pip3 install waveshare-epd")
        sys.exit(1)

from PIL import Image, ImageDraw, ImageFont

# Configuration
MESSAGE_FILE = "/tmp/remoteclaw-messages.json"
REFRESH_INTERVAL = 30  # seconds

class DisplayService:
    def __init__(self):
        self.epd = None
        self.last_message = "Waiting for messages..."
        self.last_timestamp = "--:--:--"
        self.openclaw_status = "unknown"
        self.nodes_count = 0
        self.font_small = None
        self.font_medium = None
        self.font_large = None
        self.running = True
        
    def init_display(self):
        """Initialize the e-Paper display."""
        try:
            self.epd = epd2in13_V3.EPD()
            self.epd.init()
            self.epd.Clear(0xFF)
            print("[Display] e-Paper initialized successfully")
            return True
        except Exception as e:
            print(f"[Display] Error initializing e-Paper: {e}")
            return False
    
    def load_fonts(self):
        """Load system fonts for display."""
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
            "/usr/share/fonts/truetype/piboto/Piboto-Regular.ttf",
        ]
        
        font_path = None
        for fp in font_paths:
            if os.path.exists(fp):
                font_path = fp
                break
        
        try:
            if font_path:
                self.font_small = ImageFont.truetype(font_path, 10)
                self.font_medium = ImageFont.truetype(font_path, 12)
                self.font_large = ImageFont.truetype(font_path, 14)
                print(f"[Display] Loaded font: {font_path}")
            else:
                raise FileNotFoundError("No system fonts found")
        except Exception as e:
            print(f"[Display] Using default font: {e}")
            self.font_small = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_large = ImageFont.load_default()
    
    def check_openclaw_status(self):
        """Check if OpenClaw gateway is running."""
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "openclaw-gateway"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self.openclaw_status = "running"
            else:
                self.openclaw_status = "stopped"
        except Exception:
            self.openclaw_status = "unknown"
    
    def get_nodes_count(self):
        """Get count of connected OpenClaw nodes."""
        try:
            result = subprocess.run(
                ["openclaw", "nodes", "status", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                self.nodes_count = len(data.get('nodes', []))
            else:
                self.nodes_count = 0
        except Exception:
            self.nodes_count = 0
    
    def read_message_file(self):
        """Read message data from JSON file."""
        try:
            if not os.path.exists(MESSAGE_FILE):
                return False
            
            mtime = os.path.getmtime(MESSAGE_FILE)
            with open(MESSAGE_FILE, 'r') as f:
                data = json.load(f)
            
            if 'message' in data:
                self.last_message = str(data['message'])[:80]
            if 'timestamp' in data:
                self.last_timestamp = str(data['timestamp'])[:20]
            
            return True
        except Exception as e:
            print(f"[Display] Read error: {e}")
            return False
    
    def wrap_text(self, text, draw, font, max_width):
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test = current_line + " " + word if current_line else word
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines
    
    def draw_display(self):
        """Draw the display content."""
        # e-Paper dimensions (rotated)
        width = self.epd.height  # 250
        height = self.epd.width   # 122
        
        # Create black image
        image_black = Image.new('1', (width, height), 255)
        draw = ImageDraw.Draw(image_black)
        
        # Header background
        draw.rectangle([0, 0, width, 18], fill=0)
        draw.text((5, 2), "RemoteClaw Pi Node", font=self.font_medium, fill=255)
        
        # Status line
        status_text = f"OpenClaw: {self.openclaw_status.upper()} | Nodes: {self.nodes_count}"
        draw.text((5, 22), status_text, font=self.font_small, fill=0)
        
        # Divider
        draw.line([0, 35, width, 35], fill=0, width=1)
        
        # Current time
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        draw.text((5, 38), f"Time: {current_time}", font=self.font_small, fill=0)
        
        # Message section
        draw.text((5, 52), "Last Message:", font=self.font_medium, fill=0)
        
        # Wrapped message lines
        lines = self.wrap_text(self.last_message, draw, self.font_small, width - 10)
        y = 66
        for line in lines[:4]:
            draw.text((5, y), line, font=self.font_small, fill=0)
            y += 12
        
        # Footer
        draw.line([0, height - 10, width, height - 10], fill=0, width=1)
        draw.text((5, height - 9), f"Upd: {datetime.now().strftime('%H:%M')}", 
                  font=self.font_small, fill=0)
        
        # Display both buffers (B&W display)
        self.epd.display(self.epd.getbuffer(image_black), 
                         self.epd.getbuffer(Image.new('1', (width, height), 255)))
    
    def run(self):
        """Main service loop."""
        print("[Service] Starting RemoteClaw Display Service...")
        
        if not self.init_display():
            print("[Error] Failed to initialize display")
            sys.exit(1)
        
        self.load_fonts()
        
        # Handle graceful shutdown
        import signal
        def signal_handler(sig, frame):
            print("[Service] Shutdown signal received")
            self.running = False
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            while self.running:
                # Update data
                self.check_openclaw_status()
                self.get_nodes_count()
                self.read_message_file()
                
                # Update display
                self.draw_display()
                
                # Wait for next refresh
                print(f"[Service] Display updated. Sleeping {REFRESH_INTERVAL}s...")
                time.sleep(REFRESH_INTERVAL)
                
        except Exception as e:
            print(f"[Error] {e}")
            raise
        finally:
            # Clear display on exit
            try:
                self.epd.Clear(0xFF)
                self.epd.sleep()
            except:
                pass
            print("[Service] Display service stopped")

if __name__ == "__main__":
    service = DisplayService()
    service.run()