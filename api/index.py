import sys
import importlib.util
import traceback
import os
from pathlib import Path

# Import Flask FIRST - this should always work
from flask import Flask, jsonify

# Get project root (parent of api directory)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Create a basic error handler FIRST - this ensures handler is always defined
def create_error_handler(error_msg, error_type, tb_lines=None):
    """Create an error handler Flask app"""
    error_app = Flask(__name__)
    
    @error_app.route('/<path:path>')
    @error_app.route('/')
    def error_handler(path=''):
        data_dir = project_root / "data" / "synthetic"
        templates_dir = project_root / "templates"
        
        error_info = {
            'error': str(error_msg),
            'type': error_type,
            'project_root': str(project_root),
            'app_py_exists': (project_root / "app.py").exists(),
            'data_dir_exists': data_dir.exists(),
            'templates_dir_exists': templates_dir.exists(),
            'cwd': os.getcwd(),
            'python_path': sys.path[:5],
        }
        
        if tb_lines:
            error_info['traceback'] = tb_lines
        
        return jsonify(error_info), 500
    
    return error_app

# Initialize handler with a basic error handler (will be replaced if app loads successfully)
handler = create_error_handler("Initializing...", "Initialization")

try:
    # Ensure the app package is importable
    import app  # This makes the app package available
    
except Exception as e:
    tb_lines = traceback.format_exc().split('\n')[-15:]
    handler = create_error_handler(
        f"Failed to import app package: {str(e)}",
        type(e).__name__,
        tb_lines
    )
else:
    try:
        # Import app.py as a module
        app_py_path = project_root / "app.py"
        
        if not app_py_path.exists():
            raise FileNotFoundError(f"app.py not found at {app_py_path}")
        
        # Load app.py as a module
        spec = importlib.util.spec_from_file_location("flask_app", app_py_path)
        if spec is None or spec.loader is None:
            raise ImportError("Failed to create module spec for app.py")
        
        flask_app_module = importlib.util.module_from_spec(spec)
        
        # Execute the module (this runs all the imports and route definitions)
        spec.loader.exec_module(flask_app_module)
        
        # Get the Flask app instance
        if not hasattr(flask_app_module, 'app'):
            raise AttributeError("app.py does not define an 'app' variable")
        
        app = flask_app_module.app
        
        # Configure Flask paths for serverless environment
        app.root_path = str(project_root)
        if not app.template_folder:
            app.template_folder = "templates"
        
        # Success! Replace error handler with real app
        handler = app
        
    except Exception as e:
        tb_lines = traceback.format_exc().split('\n')[-15:]
        handler = create_error_handler(
            f"Failed to load Flask app: {str(e)}",
            type(e).__name__,
            tb_lines
        )

# Ensure handler is always defined (final fallback)
if handler is None:
    handler = create_error_handler(
        "Handler initialization completely failed",
        "UnknownError"
    )
