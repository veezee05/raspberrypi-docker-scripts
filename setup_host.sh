#!/bin/bash
set -e

echo "[HOST SETUP] Starting Docker installation for Raspberry Pi..."

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Download and run Docker installation script
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add current user to docker group to avoid using 'sudo' with docker commands
echo "[HOST SETUP] Adding user $USER to 'docker' group..."
sudo usermod -aG docker $USER

# Clean up
rm get-docker.sh

echo "[HOST SETUP] Docker installation complete!"
echo "[HOST SETUP] IMPORTANT: You MUST log out and log back in (or reboot) for the group changes to take effect."
echo "[HOST SETUP] After that, you can run: ./run_container.sh"
