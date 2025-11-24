import sys
import traceback
import os
from pathlib import Path

# Wrap EVERYTHING in try/except to catch any import-time errors
try:
    # Import Flask - wrap in try/except in case it fails
    try:
        from flask import Flask, jsonify
    except ImportError as e:
        # If Flask isn't installed, create a minimal handler
        sys.stderr.write(f"Flask import error: {e}\n")
        # Create a minimal WSGI app without Flask
        class MinimalHandler:
            def __call__(self, environ, start_response):
                status = '500 Internal Server Error'
                headers = [('Content-Type', 'application/json')]
                response_body = {'error': f'Flask not installed: {e}'}
                start_response(status, headers)
                return [str(response_body).encode()]
        handler = MinimalHandler()
        raise
    
    # Get project root (parent of api directory)
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Create a basic error handler function
    def create_error_handler(error_msg, error_type, tb_lines=None):
        """Create an error handler Flask app"""
        error_app = Flask(__name__)
        
        @error_app.route('/<path:path>')
        @error_app.route('/')
        def error_handler(path=''):
            try:
                data_dir = project_root / "data" / "synthetic"
                templates_dir = project_root / "templates"
                
                error_info = {
                    'error': str(error_msg),
                    'type': str(error_type),
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
            except Exception as e2:
                return jsonify({'error': str(e2), 'original_error': str(error_msg)}), 500
        
        return error_app
    
    # Initialize handler with a basic error handler
    handler = create_error_handler("Initializing...", "Initialization")
    
    # Now try to load the actual app
    try:
        import importlib.util
        
        # Ensure the app package is importable
        import app  # This makes the app package available
        
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
        # If loading the app fails, use error handler
        tb_lines = traceback.format_exc().split('\n')[-15:]
        handler = create_error_handler(
            f"Failed to load Flask app: {str(e)}",
            type(e).__name__,
            tb_lines
        )

except Exception as e:
    # Fatal error during module initialization
    # Try to create a minimal handler
    try:
        from flask import Flask, jsonify
        fatal_app = Flask(__name__)
        
        @fatal_app.route('/<path:path>')
        @fatal_app.route('/')
        def fatal_handler(path=''):
            tb = traceback.format_exc()
            return jsonify({
                'error': f'Fatal initialization error: {str(e)}',
                'type': type(e).__name__,
                'traceback': tb.split('\n')[-20:]
            }), 500
        
        handler = fatal_app
    except:
        # Last resort - create minimal WSGI handler
        class FatalHandler:
            def __call__(self, environ, start_response):
                status = '500 Internal Server Error'
                headers = [('Content-Type', 'text/plain')]
                start_response(status, headers)
                return [f'Fatal error: {str(e)}'.encode()]
        handler = FatalHandler()

# Ensure handler is always defined
if 'handler' not in globals() or handler is None:
    try:
        from flask import Flask, jsonify
        final_app = Flask(__name__)
        @final_app.route('/<path:path>')
        @final_app.route('/')
        def final_handler(path=''):
            return jsonify({'error': 'Handler not initialized'}), 500
        handler = final_app
    except:
        class FinalHandler:
            def __call__(self, environ, start_response):
                status = '500 Internal Server Error'
                headers = [('Content-Type', 'text/plain')]
                start_response(status, headers)
                return [b'Handler initialization failed']
        handler = FinalHandler()
