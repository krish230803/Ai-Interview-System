import os
import sys
from flask import Flask, session, request
from flask_cors import CORS
from flask_login import LoginManager
from app.routes.interview_routes import interview_bp
from app.routes.auth_routes import auth_bp
from app.utils.email import mail

# Add the backend directory to Python path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BACKEND_DIR)

from config import Config
from app.models.interview import db
from app.models.user import User

app = Flask(__name__)
app.config.from_object(Config)

# Ensure development mode is set
app.env = os.environ.get('FLASK_ENV', 'development')
app.debug = os.environ.get('FLASK_DEBUG', '1') == '1'

# Initialize extensions
db.init_app(app)
mail.init_app(app)

# Configure CORS with more permissive settings for development
CORS(app, 
     resources={r"/*": {
         "origins": ["http://localhost:8000", "http://127.0.0.1:8000"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization", "Accept", "X-Requested-With"],
         "supports_credentials": True,
         "expose_headers": ["Set-Cookie", "Authorization"],
         "max_age": 600
     }},
     supports_credentials=True)

# Configure session
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_DOMAIN'] = None

@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin in ["http://localhost:8000", "http://127.0.0.1:8000"]:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    return response

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = None
login_manager.session_protection = "strong"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database
with app.app_context():
    db.create_all()
    db.session.commit()

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(interview_bp, url_prefix='/interview')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
