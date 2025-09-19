"""
Configuration for Hugging Face Spaces deployment
"""

import os

# Hugging Face Spaces configuration
HF_SPACE_CONFIG = {
    "title": "Context Graph Explorer",
    "emoji": "🔍",
    "colorFrom": "blue",
    "colorTo": "green",
    "sdk": "streamlit",
    "sdk_version": "1.28.1",
    "app_file": "app.py",
    "pinned": False
}

# Environment variables for production
def get_config():
    return {
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "port": int(os.getenv("PORT", 8501)),
        "host": os.getenv("HOST", "0.0.0.0")
    }
