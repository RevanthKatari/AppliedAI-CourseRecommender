"""
Vercel serverless function entry point for Flask app.
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import from app.py
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the Flask app instance from app.py
import app as flask_app_module

# Export the Flask app for Vercel
handler = flask_app_module.app
