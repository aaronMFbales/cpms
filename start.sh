#!/bin/bash
# Start script for Render deployment

# Set environment variables for Render
export RENDER=true
export PYTHONUNBUFFERED=1

# Start Streamlit with Render configuration
streamlit run main.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --browser.serverAddress=0.0.0.0 \
    --browser.serverPort=$PORT
