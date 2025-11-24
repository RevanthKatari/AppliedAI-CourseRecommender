import sys
import importlib.util
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    # Import app.py as a module (since 'app' is a directory, we need to load app.py directly)
    app_py_path = project_root / "app.py"
    spec = importlib.util.spec_from_file_location("app_module", app_py_path)
    app_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app_module)
    
    # Get the Flask app instance
    app = app_module.app
    
    handler = app
except Exception as e:
    # Create a minimal error handler
    from flask import Flask
    error_app = Flask(__name__)
    
    @error_app.route('/<path:path>')
    def error_handler(path):
        return {'error': str(e), 'type': type(e).__name__}, 500
    
    handler = error_app
