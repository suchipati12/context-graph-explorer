#!/bin/bash

# Create necessary directories
mkdir -p /tmp/streamlit
mkdir -p ~/.streamlit

# Set proper permissions
chmod -R 755 /home/user/app
chmod 777 /tmp

# Start Streamlit with proper configuration
exec streamlit run app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --browser.gatherUsageStats=false
