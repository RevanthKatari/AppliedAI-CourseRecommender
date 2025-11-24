import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from app import app
    
    # Add a test route
    @app.route('/test')
    def test():
        return {'status': 'ok', 'path': str(project_root)}
    
    handler = app
except Exception as e:
    # Create a minimal error handler
    from flask import Flask
    error_app = Flask(__name__)
    
    @error_app.route('/<path:path>')
    def error_handler(path):
        return {'error': str(e), 'type': type(e).__name__}, 500
    
    handler = error_app
