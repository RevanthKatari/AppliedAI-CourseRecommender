import sys
import importlib.util
import traceback
from pathlib import Path

# Get project root (parent of api directory)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    # Ensure the app package is importable
    # This is needed because app.py imports from app.data_loader, etc.
    import app  # This makes the app package available
    
    # Import app.py as a module
    # We need to load it this way because 'app' is a directory/package
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
    # This ensures templates and static files are found correctly
    app.root_path = str(project_root)
    if not app.template_folder:
        app.template_folder = "templates"
    
    # Export handler for Vercel
    handler = app
    
except Exception as e:
    # Create error handler that shows detailed error information
    from flask import Flask, jsonify
    
    error_app = Flask(__name__)
    error_traceback = traceback.format_exc()
    
    @error_app.route('/<path:path>')
    @error_app.route('/')
    def error_handler(path=''):
        error_info = {
            'error': str(e),
            'type': type(e).__name__,
            'project_root': str(project_root),
            'app_py_exists': (project_root / "app.py").exists(),
            'traceback': error_traceback.split('\n')[-10:],  # Last 10 lines
        }
        return jsonify(error_info), 500
    
    handler = error_app
