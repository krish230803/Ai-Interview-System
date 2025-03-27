import secrets
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generate_token():
    """Generate a random token for email verification or password reset."""
    return secrets.token_urlsafe(32)

def generate_timed_token(data, salt='email-confirm-key'):
    """Generate a timed token for sensitive operations."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(data, salt=salt)

def verify_timed_token(token, salt='email-confirm-key', expiration=3600):
    """Verify a timed token."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        data = serializer.loads(token, salt=salt, max_age=expiration)
        return data
    except:
        return None

def verify_token(token):
    """Verify a simple token."""
    if not token:
        return False
    return True 