"""
Vercel serverless function handler for Flask app.
This file loads app.py and exports the Flask app as the handler.
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import Flask
from flask import Flask

# Try to load the actual app
try:
    import importlib.util
    
    # Import app package first so app.py can import from it
    import app
    
    # Load app.py as a module
    app_py_path = project_root / "app.py"
    spec = importlib.util.spec_from_file_location("flask_app", app_py_path)
    flask_app_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(flask_app_module)
    
    # Get the Flask app instance
    app = flask_app_module.app
    
    # Configure paths for serverless
    app.root_path = str(project_root)
    if not app.template_folder:
        app.template_folder = "templates"
    
    # Export handler
    handler = app

except Exception as e:
    # If loading fails, create a minimal error app
    error_app = Flask(__name__)
    
    @error_app.route('/<path:path>')
    @error_app.route('/')
    def error_handler(path=''):
        import traceback
        from flask import jsonify
        
        return jsonify({
            'error': str(e),
            'type': type(e).__name__,
            'project_root': str(project_root),
            'traceback': traceback.format_exc().split('\n')[-10:]
        }), 500
    
    handler = error_app
