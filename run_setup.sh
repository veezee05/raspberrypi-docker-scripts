#!/bin/bash

# Build the setup image
echo "[SCRIPT] Building Setup Docker Image..."
docker build -t fps-vending-setup -f Dockerfile.setup .

# Run the setup container
echo "[SCRIPT] Running Setup Container..."
docker run --rm fps-vending-setup

echo "[SCRIPT] Setup process complete!"
