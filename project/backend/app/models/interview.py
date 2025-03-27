import os
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
import pickle
from textblob import TextBlob
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from datetime import datetime
import random

db = SQLAlchemy()

# Get the absolute path to the backend directory
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load pre-trained model and vectorizer
MODEL_PATH = os.path.join(BACKEND_DIR, 'ml_model', 'interview_classifier.pkl')
VECTORIZER_PATH = os.path.join(BACKEND_DIR, 'ml_model', 'tfidf_vectorizer.pkl')
QUESTIONS_PATH = os.path.join(BACKEND_DIR, 'data', 'questions.csv')

# Initialize model and vectorizer
try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    with open(VECTORIZER_PATH, 'rb') as f:
        vectorizer = pickle.load(f)
except FileNotFoundError:
    model = None
    vectorizer = None

class InterviewSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    question_count = db.Column(db.Integer, default=0)
    total_score = db.Column(db.Float, default=0.0)
    completed = db.Column(db.Boolean, default=False)
    last_category = db.Column(db.String(50))  # Track last question category
    categories_asked = db.Column(db.String(500), default='')  # Track categories asked
    interview_mode = db.Column(db.String(20), default='text')  # Store interview mode (text or audio)

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('interview_session.id'), nullable=False)
    question = db.Column(db.String(500), nullable=False)
    response = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(20))
    category = db.Column(db.String(50))
    score = db.Column(db.Float, default=0.0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with interview session
    session = db.relationship('InterviewSession', backref='responses')

def create_session(user_id):
    """Create a new interview session for the user."""
    session = InterviewSession(user_id=user_id)
    db.session.add(session)
    db.session.commit()
    return session.id

def get_session_stats(session_id):
    """Get statistics for an interview session using raw SQL."""
    from app.app import db
    
    conn = db.engine.raw_connection()
    cursor = conn.cursor()
    
    try:
        # Check if interview_mode column exists
        cursor.execute("PRAGMA table_info(interview_session)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Get session data including interview_mode if it exists
        if 'interview_mode' in columns:
            cursor.execute(
                "SELECT question_count, total_score, interview_mode FROM interview_session WHERE id = ?",
                (session_id,)
            )
            session_data = cursor.fetchone()
            if not session_data:
                conn.close()
                return {
                    'total_questions': 0,
                    'average_score': 0,
                    'sentiment_distribution': {},
                    'category_distribution': {},
                    'response_lengths': [],
                    'detailed_responses': [],
                    'interview_mode': 'text'  # Default to text
                }
            question_count, total_score, interview_mode = session_data
        else:
            cursor.execute(
                "SELECT question_count, total_score FROM interview_session WHERE id = ?",
                (session_id,)
            )
            session_data = cursor.fetchone()
            if not session_data:
                conn.close()
                return {
                    'total_questions': 0,
                    'average_score': 0,
                    'sentiment_distribution': {},
                    'category_distribution': {},
                    'response_lengths': [],
                    'detailed_responses': [],
                    'interview_mode': 'text'  # Default to text
                }
            question_count, total_score = session_data
            interview_mode = 'text'  # Default to text if column doesn't exist
        
        # Get all responses for this session
        cursor.execute(
            "SELECT question, response, sentiment, category, score FROM response WHERE session_id = ? ORDER BY id ASC",
            (session_id,)
        )
        responses = cursor.fetchall()
        
        # Calculate sentiment distribution
        sentiment_distribution = {}
        category_distribution = {}
        response_lengths = []
        detailed_responses = []
        
        for question, response, sentiment, category, score in responses:
            # Ensure score is a valid number
            if score is None:
                score = 0.0
                
            # Update sentiment distribution
            if sentiment:
                sentiment_distribution[sentiment] = sentiment_distribution.get(sentiment, 0) + 1
            
            # Update category distribution
            if category:
                category_distribution[category] = category_distribution.get(category, 0) + 1
            
            # Add response length
            if response:
                response_lengths.append(len(response.split()))
            
            # Add detailed response
            detailed_responses.append({
                'question': question,
                'response': response,
                'sentiment': sentiment,
                'category': category,
                'score': float(score)  # Ensure score is a float
            })
        
        # Calculate average score and response length
        average_score = total_score / question_count if question_count > 0 else 0
        average_response_length = sum(response_lengths) / len(response_lengths) if response_lengths else 0
        
        stats = {
            'total_questions': question_count,
            'average_score': average_score,
            'average_response_length': average_response_length,
            'sentiment_distribution': sentiment_distribution,
            'category_distribution': category_distribution,
            'response_lengths': response_lengths,
            'detailed_responses': detailed_responses,
            'interview_mode': interview_mode or 'text'  # Include interview mode in response
        }
        
        conn.close()
        return stats
    except Exception as e:
        print(f"Error getting session stats: {str(e)}")
        try:
            conn.close()
        except:
            pass
        raise

def calculate_response_score(response_text, sentiment):
    # Score based on response length (1-5 points)
    length_score = min(5, len(response_text.split()) / 20)
    
    # Score based on sentiment (1-5 points)
    sentiment_scores = {'positive': 5, 'neutral': 3, 'negative': 1}
    sentiment_score = sentiment_scores.get(sentiment, 3)
    
    # Calculate final score (average of both metrics)
    final_score = (length_score + sentiment_score) / 2
    return round(final_score, 2)

def store_interview_data(session_id, question, response_text, sentiment, input_type, response_category):
    """Store interview data using raw SQL to avoid ORM issues."""
    from app.app import db
    
    # Calculate response score
    score = calculate_response_score(response_text, sentiment)
    
    conn = db.engine.raw_connection()
    cursor = conn.cursor()
    
    try:
        # Check if input_type column exists in the response table
        cursor.execute("PRAGMA table_info(response)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Store response
        if 'input_type' in columns:
            cursor.execute(
                "INSERT INTO response (session_id, question, response, sentiment, category, input_type, score) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (session_id, question, response_text, sentiment, response_category, input_type, score)
            )
        else:
            cursor.execute(
                "INSERT INTO response (session_id, question, response, sentiment, category, score) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (session_id, question, response_text, sentiment, response_category, score)
            )
        
        # Update session
        cursor.execute(
            "UPDATE interview_session SET question_count = question_count + 1, total_score = total_score + ? "
            "WHERE id = ?",
            (score, session_id)
        )
        
        # Get the question category from questions_df
        question_info = questions_df[questions_df['question'] == question]
        if not question_info.empty:
            category = question_info.iloc[0]['follow_up_trigger']
            
            # Get current categories
            cursor.execute(
                "SELECT categories_asked FROM interview_session WHERE id = ?",
                (session_id,)
            )
            categories_data = cursor.fetchone()
            
            if categories_data and category:
                current_categories = categories_data[0].split(',') if categories_data[0] else []
                
                if category not in current_categories:
                    current_categories.append(category)
                    categories_str = ','.join(filter(None, current_categories))
                    
                    cursor.execute(
                        "UPDATE interview_session SET categories_asked = ?, last_category = ? "
                        "WHERE id = ?",
                        (categories_str, category, session_id)
                    )
        
        # Check if this is the last question
        cursor.execute(
            "SELECT question_count FROM interview_session WHERE id = ?",
            (session_id,)
        )
        question_count_data = cursor.fetchone()
        
        is_complete = False
        if question_count_data and question_count_data[0] >= 10:
            cursor.execute(
                "UPDATE interview_session SET completed = 1 WHERE id = ?",
                (session_id,)
            )
            is_complete = True
        
        conn.commit()
        conn.close()
        
        return score, is_complete
    except Exception as e:
        print(f"Error in store_interview_data: {str(e)}")
        import traceback
        print(traceback.format_exc())
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        raise

def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    if sentiment > 0.1:
        return "positive"
    elif sentiment < -0.1:
        return "negative"
    else:
        return "neutral"

def get_random_question(exclude_questions=None, question_type=None):
    """Get a random question that hasn't been asked before."""
    if exclude_questions is None:
        exclude_questions = []
    
    # Filter questions based on type and exclusions
    available_questions = questions_df[~questions_df['question'].isin(exclude_questions)]
    
    if question_type:
        available_questions = available_questions[available_questions['type'] == question_type]
    
    if available_questions.empty:
        # If no questions of specified type, try any unasked questions
        available_questions = questions_df[~questions_df['question'].isin(exclude_questions)]
    
    if available_questions.empty:
        return None
    
    selected = available_questions.sample(n=1).iloc[0]
    return selected['question']

def get_next_question(session_id=None):
    """Get the next question based on session history and category distribution."""
    from app.app import db
    
    if not session_id:
        # For first question, always get the first introduction question
        initial_questions = questions_df[
            (questions_df['type'] == 'initial') & 
            (questions_df['follow_up_trigger'] == 'introduction')
        ]
        if not initial_questions.empty:
            return initial_questions.iloc[0]['question']
        return "Tell me about yourself"
    
    conn = db.engine.raw_connection()
    cursor = conn.cursor()
    
    try:
        # Get session data
        cursor.execute(
            "SELECT last_category, categories_asked FROM interview_session WHERE id = ?",
            (session_id,)
        )
        session_data = cursor.fetchone()
        
        if not session_data:
            conn.close()
            return "Tell me about yourself"
        
        last_category, categories_asked_str = session_data
        categories_asked = categories_asked_str.split(',') if categories_asked_str else []
        
        # Get previously asked questions
        cursor.execute(
            "SELECT question FROM response WHERE session_id = ?",
            (session_id,)
        )
        asked_questions_data = cursor.fetchall()
        asked_questions = [row[0] for row in asked_questions_data]
        
        # Define the desired category order with weights for variety
        category_order = [
            ('introduction', 2),  # Start with introduction questions
            ('strengths', 2),     # Then assess strengths
            ('experience', 2),    # Past experience
            ('project', 2),       # Specific examples
            ('goals', 1),        # Future outlook
            ('motivation', 1),    # Personal drive
            ('teamwork', 1),      # Collaboration
            ('leadership', 1),    # Leadership potential
            ('problem_solving', 1), # Technical skills
            ('learning', 1),      # Growth mindset
            ('stress', 1),        # Stress handling
            ('company', 1),       # Company fit
            ('task_management', 1) # Organization skills
        ]
        
        # First, try to get a question from an unused category
        unused_categories = [(cat, weight) for cat, weight in category_order 
                            if cat not in categories_asked]
        
        if unused_categories:
            # Prioritize categories based on their weights
            weighted_categories = []
            for cat, weight in unused_categories:
                weighted_categories.extend([cat] * weight)
            
            # Randomly select from weighted categories
            if weighted_categories:
                next_category = random.choice(weighted_categories)
                
                # Try to get an initial question from this category
                category_questions = questions_df[
                    (questions_df['type'] == 'initial') & 
                    (questions_df['follow_up_trigger'] == next_category) & 
                    (~questions_df['question'].isin(asked_questions))
                ]
                
                if not category_questions.empty:
                    question = category_questions.sample(n=1).iloc[0]['question']
                    # Update session with the new category
                    new_categories = ','.join(filter(None, categories_asked + [next_category]))
                    cursor.execute(
                        "UPDATE interview_session SET last_category = ?, categories_asked = ? WHERE id = ?",
                        (next_category, new_categories, session_id)
                    )
                    conn.commit()
                    conn.close()
                    return question
        
        # If we can't get a new category question, try a follow-up from the last category
        if last_category:
            follow_up_questions = questions_df[
                (questions_df['type'] == 'follow_up') & 
                (questions_df['follow_up_trigger'] == last_category) & 
                (~questions_df['question'].isin(asked_questions))
            ]
            if not follow_up_questions.empty:
                conn.close()
                return follow_up_questions.sample(n=1).iloc[0]['question']
        
        # If still no question found, get any unasked question
        available_questions = questions_df[~questions_df['question'].isin(asked_questions)]
        if not available_questions.empty:
            conn.close()
            return available_questions.sample(n=1).iloc[0]['question']
        
        conn.close()
        return "Thank you for your responses. Do you have any questions for me?"
    except Exception as e:
        print(f"Error in get_next_question: {str(e)}")
        import traceback
        print(traceback.format_exc())
        try:
            conn.close()
        except:
            pass
        return "Thank you for your responses. Do you have any questions for me?"

def get_follow_up_question(response_category, prev_question_id):
    """Get a follow-up question based on response category."""
    if not response_category:
        return None
        
    follow_up_questions = questions_df[
        (questions_df['type'] == 'follow_up') & 
        (questions_df['follow_up_trigger'] == response_category)
    ]
    
    if not follow_up_questions.empty:
        return follow_up_questions.sample(n=1).iloc[0]['question']
    return None

def preprocess_text(text):
    """Clean and preprocess text for classification."""
    # Convert to lowercase
    text = text.lower()
    # Remove special characters and extra whitespace
    text = re.sub(r'[^\w\s]', '', text)
    text = ' '.join(text.split())
    return text

def classify_response(text):
    """Classify the response into predefined categories."""
    if model is None or vectorizer is None:
        return "general"
        
    try:
        # Preprocess the text
        processed_text = preprocess_text(text)
        # Transform text using the vectorizer
        text_vector = vectorizer.transform([processed_text])
        # Predict the category
        category = model.predict(text_vector)[0]
        return category
    except Exception as e:
        print(f"Error in classify_response: {str(e)}")
        return "general"

# Load questions from CSV file
try:
    questions_df = pd.read_csv(QUESTIONS_PATH)
except FileNotFoundError:
    questions_df = pd.DataFrame({
        'type': ['initial'],
        'question': ['Tell me about yourself.'],
        'follow_up_trigger': ['introduction']
    })
