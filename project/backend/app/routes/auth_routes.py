from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app.models.user import User, db
from app.utils.email import send_verification_email, send_password_reset_email
from app.utils.tokens import generate_token, verify_token
from datetime import datetime, timedelta
import traceback

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        if not name or not email or not password:
            return jsonify({"error": "Missing required fields"}), 400
            
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 400
            
        user = User(name=name, email=email)
        user.set_password(password)
        user.verification_token = generate_token()
        
        # Always verify user in development mode
        user.is_verified = True
        user.verification_token = None
        
        db.session.add(user)
        db.session.commit()

        # Log the successful registration
        print(f"User registered successfully: {email}")
        
        # Login the user immediately after registration
        login_user(user)

        return jsonify({
            'message': 'Registration successful. You can now log in.',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        # Log the full error
        print(f"Registration error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': 'Registration failed. Please try again.'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401

        if not user.is_verified:
            return jsonify({'error': 'Please verify your email before logging in'}), 401

        # Set remember=True to keep the user logged in
        login_user(user, remember=True)
        
        # Log successful login
        print(f"User logged in successfully: {email}")
        
        response = jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        })
        
        # Set CORS headers
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        return response
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    response = jsonify({'message': 'Logout successful'})
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
    return response

@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    try:
        user = User.query.filter_by(verification_token=token).first()
        if not user:
            return jsonify({'error': 'Invalid verification token'}), 400

        user.is_verified = True
        user.verification_token = None
        db.session.commit()

        return jsonify({'message': 'Email verified successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        email = data.get('email')
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'message': 'If an account exists with this email, a reset link will be sent'}), 200

        # Generate a simple token for development
        reset_token = generate_token()
        user.reset_token = reset_token
        user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()

        # In development mode, return the reset token directly
        if current_app.env == 'development':
            reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password.html?token={reset_token}"
            return jsonify({
                'message': 'Development mode: Use the following link to reset your password',
                'reset_url': reset_url,
                'token': reset_token
            })

        # In production, this would send an email
        try:
            send_password_reset_email(user)
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            # Don't expose email errors to the user in production
            pass

        return jsonify({'message': 'If an account exists with this email, password reset instructions will be sent'})
    except Exception as e:
        db.session.rollback()
        print(f"Password reset error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    try:
        data = request.get_json()
        new_password = data.get('password')

        if not new_password:
            return jsonify({'error': 'New password is required'}), 400

        user = User.query.filter_by(reset_token=token).first()
        if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
            return jsonify({'error': 'Invalid or expired reset token'}), 400

        user.set_password(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()

        return jsonify({'message': 'Password reset successful'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me')
@login_required
def get_current_user():
    return jsonify({'user': current_user.to_dict()})

@auth_bp.route('/update-name', methods=['POST'])
@login_required
def update_name():
    try:
        data = request.get_json()
        new_name = data.get('name')
        
        if not new_name:
            return jsonify({'error': 'Name is required'}), 400
            
        current_user.name = new_name
        db.session.commit()
        
        return jsonify({
            'message': 'Name updated successfully',
            'user': current_user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        print(f"Name update error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': 'Failed to update name'}), 500 