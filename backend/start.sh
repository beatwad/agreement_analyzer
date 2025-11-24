#!/bin/bash

# Start tailscaled in the background
/usr/sbin/tailscaled --state=/var/lib/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock &

# Wait for tailscaled to start
sleep 5

# Authenticate if we have an auth key
if [ ! -z "$TS_AUTHKEY" ]; then
    tailscale up --authkey=$TS_AUTHKEY --hostname=agreement-analyzer
fi

# Start serving the app via Tailscale Funnel
# Pointing to localhost:8001 since we are in the same container now
tailscale serve https / http://localhost:8001 &

# Start the FastAPI application
uvicorn server:app --host 0.0.0.0 --port 8001

