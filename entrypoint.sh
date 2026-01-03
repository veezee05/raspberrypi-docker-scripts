#!/bin/bash

# Start the Flask server in the background
echo "[ENTRYPOINT] Starting Flask Server..."
python server.py &

# Wait for the server to be ready
echo "[ENTRYPOINT] Waiting for server to initialize..."
until curl -s http://localhost:5000 > /dev/null; do
  sleep 1
done

# Launch Chromium in Kiosk Mode
# --kiosk: Full screen without UI bits
# --no-first-run: Skip setup
# --disable-infobars: Hide "Chrome is being controlled"
# --user-data-dir: Separate profile for clean start
echo "[ENTRYPOINT] Launching Chromium in Kiosk Mode..."
chromium --kiosk \
    --no-first-run \
    --disable-infobars \
    --user-data-dir=/tmp/chromium-profile \
    http://localhost:5000

# Keep the script alive as long as chromium or the server is running
wait -n
