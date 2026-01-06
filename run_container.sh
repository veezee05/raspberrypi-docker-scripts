#!/bin/bash

# Build the image
echo "[SCRIPT] Building Docker Image..."
docker build --network=host -t fps-vending-app .

# Stop existing container if running
docker stop fps_container >/dev/null 2>&1 || true
docker rm fps_container >/dev/null 2>&1 || true

# Run the container
# --privileged: Required for GPIO access
# -v /var/run/docker.sock:/var/run/docker.sock: Required for BlockchainClient to talk to host Docker
# -v /run/pcscd/pcscd.comm:/run/pcscd/pcscd.comm: Required for Smart Card Reader access (if running locally)
# -p 5000:5000: Expose Web UI

# Allow Docker to access X11
xhost +local:docker >/dev/null 2>&1

echo "[SCRIPT] Starting Container..."
docker run -d \
    --name fps_container \
    --privileged \
    --network host \
    --cpus="1.2" \
    --memory="512m" \
    --restart unless-stopped \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /run/pcscd/pcscd.comm:/run/pcscd/pcscd.comm \
    fps-vending-app

echo "[SCRIPT] Container Started!"
echo "[SCRIPT] Access the UI at http://localhost:5000"