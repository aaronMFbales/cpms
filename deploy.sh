#!/bin/bash

# Deployment script for DTI CPMS on Render
# This script handles JavaScript module loading issues

echo "Starting DTI CPMS deployment..."

# Set environment variables for production
export PYTHONUNBUFFERED=1
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_ENABLE_CORS=false
export STREAMLIT_SERVER_ENABLE_STATIC_SERVING=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Clear any cached Streamlit files
echo "Clearing Streamlit cache..."
rm -rf ~/.streamlit/logs/*
rm -rf ~/.streamlit/credentials.toml

# Install dependencies with retries
echo "Installing dependencies..."
pip install --no-cache-dir --force-reinstall -r requirements-render.txt

# Verify Streamlit installation
echo "Verifying Streamlit installation..."
python -c "import streamlit; print(f'Streamlit version: {streamlit.__version__}')"

# Start the application with error handling
echo "Starting Streamlit application..."
streamlit run main.py \
    --server.port ${PORT:-8501} \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableStaticServing true \
    --browser.gatherUsageStats false \
    --client.showErrorDetails true \
    --global.developmentMode false
