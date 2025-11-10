#!/bin/bash

# Install Streamlit service
echo "Installing Streamlit service..."

# Copy service file to systemd directory
sudo cp /home/piebat/App/streamlit-app.service /etc/systemd/system/

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable the service to start at boot
sudo systemctl enable streamlit-app.service

# Start the service
sudo systemctl start streamlit-app.service

# Check service status
sudo systemctl status streamlit-app.service

echo ""
echo "Service installed and started!"
echo "To check status: sudo systemctl status streamlit-app"
echo "To stop: sudo systemctl stop streamlit-app"
echo "To restart: sudo systemctl restart streamlit-app"
echo "To view logs: sudo journalctl -u streamlit-app -f"
