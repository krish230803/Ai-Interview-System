import sys
import os

# Get the absolute path to the backend directory
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BACKEND_DIR)

# Set Flask environment variables
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

from app.app import app

if __name__ == "__main__":
    # Explicitly set environment to development
    app.env = 'development'
    app.debug = True
    # Allow connections from all interfaces
    app.run(host='0.0.0.0', port=5000, debug=True) 