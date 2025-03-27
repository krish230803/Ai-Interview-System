from app.app import app, db
from app.models.user import User
from app.models.interview import InterviewSession, Response

def init_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Commit the changes
        db.session.commit()
        
        print("Database initialized successfully!")

if __name__ == "__main__":
    init_db() 