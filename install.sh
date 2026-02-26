#!/bin/bash
set -e

USER=&quot;magic&quot;
REPO_DIR=&quot;/home/${USER}/Remoteclaw&quot;
WAVESHARE_DIR=&quot;/home/${USER}/waveshare-epaper&quot;
EPAPER_LIB=&quot;${WAVESHARE_DIR}/RaspberryPi/python/lib&quot;

cd &quot;${REPO_DIR}&quot; || { echo &quot;Repo not found at ${REPO_DIR}&quot;; exit 1; }

echo &quot;=== RemoteClaw e-Paper Display Service Installer ===&quot;

# Update and install system deps
sudo apt update &amp;&amp; sudo apt upgrade -y
sudo apt install -y python3-pip python3-dev fonts-dejavu-core libfreetype6-dev libjpeg62-turbo-dev zlib1g-dev git

# Python deps
pip3 install --user -r requirements.txt

# Waveshare e-Paper library
if [ ! -d &quot;${WAVESHARE_DIR}&quot; ]; then
  echo &quot;Cloning Waveshare e-Paper library...&quot;
  git clone --depth 1 https://github.com/waveshareteam/e-Paper.git &quot;${WAVESHARE_DIR}&quot;
fi
chmod -R 755 &quot;${EPAPER_LIB}&quot;

# Systemd service
echo &quot;Setting up systemd service...&quot;
sudo cp remoteclaw-display.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable remoteclaw-display.service
sudo systemctl restart remoteclaw-display.service || sudo systemctl start remoteclaw-display.service

# Permissions
sudo chown -R ${USER}:${USER} &quot;${REPO_DIR}&quot; &quot;${WAVESHARE_DIR}&quot;

echo &quot;=== Installation complete! ===&quot;
echo &quot;Service status: systemctl status remoteclaw-display.service&quot;
echo &quot;The service reads /tmp/remoteclaw-messages.json and displays on e-Paper.&quot;
echo &quot;JSON format: {{\&quot;status\&quot;: \&quot;connected\&quot;, \&quot;messages\&quot;: [\&quot;msg1\&quot;, ...], \&quot;timestamp\&quot;: \&quot;...\&quot;}}&quot;