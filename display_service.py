#!/usr/bin/env python3
import json
import time
import os
import sys
import logging

from PIL import Image, ImageDraw, ImageFont

# Waveshare e-Paper library path (set by systemd service)
sys.path.insert(0, '/home/magic/waveshare-epaper/RaspberryPi/python/lib')
try:
    from waveshare_epd import epd2in13_V3
except ImportError as e:
    logging.error(f&quot;Failed to import epd library: {e}&quot;)
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

JSON_FILE = '/tmp/remoteclaw-messages.json'

def load_data():
    try:
        if not os.path.exists(JSON_FILE):
            return None
        with open(JSON_FILE, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        logger.error(f&quot;Error loading {JSON_FILE}: {e}&quot;)
        return None

def draw_display(epd, data, ts):
    img = Image.new('1', (epd.width, epd.height), 255)  # 122x250
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype(&quot;/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf&quot;, 18)
        font_small = ImageFont.truetype(&quot;/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf&quot;, 14)
    except:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Status
    status = data.get('status', 'unknown') if data else 'No data'
    draw.text((5, 5), f&quot;Status: {status}&quot;, font=font, fill=0)
    
    # Messages
    messages = data.get('messages', []) if data else ['Waiting for messages...']
    y = 40
    for msg in messages[:6]:  # Limit lines
        wrapped = ' '.join(msg.split())[:28]  # Approx chars per line
        draw.text((5, y), wrapped, font=font_small, fill=0)
        y += 22
        if y > 160:
            break
    
    # Timestamp
    draw.text((5, 210), f&quot;{ts}&quot;, font=font_small, fill=0)
    
    return img

def main():
    epd = epd2in13_V3.EPD()
    while True:
        try:
            data = load_data()
            ts = time.strftime(&quot;%Y-%m-%d %H:%M:%S&quot;)
            
            epd.init()
            epd.Clear()
            
            img = draw_display(epd, data, ts)
            epd.display(epd.getbuffer(img))
            
            epd.sleep()
            logger.info(&quot;Display updated and slept&quot;)
        except Exception as e:
            logger.error(f&quot;Error in main loop: {e}&quot;)
        
        time.sleep(30)  # Poll every 30 seconds

if __name__ == '__main__':
    main()