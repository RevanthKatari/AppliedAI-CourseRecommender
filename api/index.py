import sys
from pathlib import Path

# Ensure we can import from the project root
root = Path(__file__).parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

# Import Flask app
try:
    from app import app
except ImportError:
    # Alternative import if the above fails
    import app as app_module
    app = app_module.app

# Vercel expects 'handler'
handler = app
