#!/bin/bash

# Proxy logic removed as per Mobile Runner Refactor
# Proxies are checked internally or ignored by the python script now.

echo "🚀 Starting Mobile Runner (Direct Connection)..."

echo "🚀 Starting Runner with Proxy..."

# Start Python Script (Keep Alive Loop)
while true; do
    if ! kill -0 $PY_PID 2>/dev/null; then
        echo "⚠️ Python script exited. Restarting in 5s..."
        sleep 5
        python -u fb_otp_browser.py --daemon --headless &
        PY_PID=$!
    fi
    
    sleep 30
done

