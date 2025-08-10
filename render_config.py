# Render Streamlit Configuration
import os

# Render automatically sets PORT environment variable
PORT = int(os.environ.get("PORT", 8501))

# Streamlit config for Render
config = {
    "server.port": PORT,
    "server.address": "0.0.0.0",
    "server.headless": True,
    "server.enableCORS": False,
    "browser.serverAddress": "0.0.0.0",
    "browser.serverPort": PORT,
    "logger.level": "info"
}
