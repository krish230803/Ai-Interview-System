from flask import current_app
from flask_mail import Message, Mail

mail = Mail()

def send_email(to, subject, template):
    """Send an email using Flask-Mail."""
    try:
        msg = Message(
            subject,
            recipients=[to],
            html=template,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise

def send_verification_email(user):
    """Send account verification email."""
    verification_url = f"{current_app.config['FRONTEND_URL']}/verify-email/{user.verification_token}"
    template = f"""
    <h1>Welcome to AI Interview Assistant!</h1>
    <p>Please click the link below to verify your email address:</p>
    <p><a href="{verification_url}">Verify Email</a></p>
    <p>If you did not create this account, please ignore this email.</p>
    """
    send_email(user.email, "Verify Your Email", template)

def send_password_reset_email(user):
    """Send password reset email."""
    reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password/{user.reset_token}"
    template = f"""
    <h1>Password Reset Request</h1>
    <p>Click the link below to reset your password:</p>
    <p><a href="{reset_url}">Reset Password</a></p>
    <p>If you did not request a password reset, please ignore this email.</p>
    <p>This link will expire in 1 hour.</p>
    """
    send_email(user.email, "Reset Your Password", template) 