#!/bin/bash
set -e

# 1. Install System Dependencies
echo "[SETUP] Installing System Dependencies..."
apt-get update && apt-get install -y \
    build-essential \
    curl \
    pcscd \
    libpcsclite-dev \
    swig \
    chromium \
    x11-xserver-utils \
    xauth \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Docker CLI
DOCKER_VERSION=${1:-24.0.5}
echo "[SETUP] Installing Docker CLI version ${DOCKER_VERSION}..."
curl -fsSL "https://download.docker.com/linux/static/stable/x86_64/docker-${DOCKER_VERSION}.tgz" -o docker.tgz \
    && tar xzvf docker.tgz --strip 1 -C /usr/local/bin docker/docker \
    && rm docker.tgz

# 3. Install Python Dependencies
echo "[SETUP] Installing Python Dependencies..."
pip install --no-cache-dir flask requests pyscard RPi.GPIO gpiozero

echo "[SETUP] All installations complete."
