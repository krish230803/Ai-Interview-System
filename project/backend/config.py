import os

# Get the absolute path to the backend directory
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuration for Flask and SQLAlchemy
class Config:
    # Ensure SQLite database directory exists
    DB_DIR = os.path.join(BACKEND_DIR, 'instance')
    os.makedirs(DB_DIR, exist_ok=True)
    
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(DB_DIR, "interview_data.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-123')
    
    # Email Configuration - Using a test account for development
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'test@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'your-app-specific-password')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@aiinterviewassistant.com')
    
    # Frontend URL for email links
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:8000')
    
    # Session Configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours in seconds
    
    # CORS Configuration
    CORS_ORIGINS = [
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
