from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.interview import db, InterviewSession, Response
from app.models.interview import (
    create_session, store_interview_data, analyze_sentiment, 
    get_next_question, get_session_stats, classify_response,
    get_follow_up_question, calculate_response_score
)
import traceback
import os

# Get the absolute path to the backend directory
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

interview_bp = Blueprint('interview', __name__)

@interview_bp.route("/start", methods=["GET"])
@login_required
def start_interview():
    """Start a new interview session."""
    try:
        # Get interview mode from query parameters (default to text)
        interview_mode = request.args.get('mode', 'text')
        if interview_mode not in ['text', 'audio']:
            interview_mode = 'text'  # Default to text if invalid mode
        
        # Create new session with user_id using raw SQL
        conn = db.engine.raw_connection()
        cursor = conn.cursor()
        
        # Check if the interview_mode column exists
        cursor.execute("PRAGMA table_info(interview_session)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Insert a new session
        if 'interview_mode' in columns:
            cursor.execute(
                "INSERT INTO interview_session (user_id, start_time, question_count, total_score, completed, interview_mode) "
                "VALUES (?, datetime('now'), 0, 0.0, 0, ?)",
                (current_user.id, interview_mode)
            )
        else:
            cursor.execute(
                "INSERT INTO interview_session (user_id, start_time, question_count, total_score, completed) "
                "VALUES (?, datetime('now'), 0, 0.0, 0)",
                (current_user.id,)
            )
        
        # Get the last inserted row ID
        session_id = cursor.lastrowid
        conn.commit()
        
        # Get first question
        first_question = get_next_question()
        if not first_question:
            first_question = "Tell me about yourself."
        
        conn.close()
        return jsonify({
            "session_id": session_id,
            "next_question": first_question,
            "question_number": 1,
            "total_questions": 10,
            "interview_mode": interview_mode
        })
    except Exception as e:
        # Log the full error
        print(f"Error in start_interview: {str(e)}")
        print(traceback.format_exc())
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return jsonify({
            "error": "Failed to start interview",
            "next_question": "Tell me about yourself."
        }), 500

@interview_bp.route("", methods=["POST"])
@login_required
def handle_interview():
    conn = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        session_id = data.get("session_id")
        if not session_id:
            return jsonify({"error": "No session ID provided"}), 400

        # Verify session belongs to current user using raw SQL
        conn = db.engine.raw_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT user_id FROM interview_session WHERE id = ?",
            (session_id,)
        )
        session_data = cursor.fetchone()
        
        if not session_data or session_data[0] != current_user.id:
            conn.close()
            return jsonify({"error": "Invalid session"}), 403

        user_response = data.get("response", "")
        if not user_response:
            conn.close()
            return jsonify({"error": "No response provided"}), 400

        current_question = data.get("current_question", "")
        input_type = data.get("inputType", "text")
        prev_question_id = data.get("prev_question_id")
        question_number = data.get("question_number", 1)
        
        # Analyze response sentiment and category
        sentiment = analyze_sentiment(user_response)
        response_category = classify_response(user_response)
        
        print(f"Response category: {response_category}")  # Debug log
        
        try:
            # Check if input_type column exists in the response table
            cursor.execute("PRAGMA table_info(response)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Store the response using raw SQL
            # First, insert the response
            if 'input_type' in columns:
                cursor.execute(
                    "INSERT INTO response (session_id, question, response, sentiment, category, input_type, score) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (session_id, current_question, user_response, sentiment, response_category, input_type, 0.0)
                )
            else:
                cursor.execute(
                    "INSERT INTO response (session_id, question, response, sentiment, category, score) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (session_id, current_question, user_response, sentiment, response_category, 0.0)
                )
            
            # Calculate a simple score based on response length (similar to the original logic)
            score = min(10, max(1, len(user_response) / 20))
            
            # Use the proper scoring function from the models
            score = calculate_response_score(user_response, sentiment)
            
            # Update the response with the calculated score
            cursor.execute(
                "UPDATE response SET score = ? WHERE session_id = ? AND question = ?",
                (score, session_id, current_question)
            )
            
            # Update the session with the new question count and score
            cursor.execute(
                "UPDATE interview_session SET question_count = question_count + 1, "
                "total_score = total_score + ? WHERE id = ?",
                (score, session_id)
            )
            
            # Check if this is the last question (question_number >= 10)
            is_complete = question_number >= 10
            if is_complete:
                cursor.execute(
                    "UPDATE interview_session SET completed = 1 WHERE id = ?",
                    (session_id,)
                )
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error storing interview data: {str(e)}")
            raise
        
        if is_complete or question_number >= 10:
            # Get session statistics using the existing function
            # Close the connection before calling other functions that might open their own connections
            conn.close()
            conn = None
            stats = get_session_stats(session_id)
            return jsonify({
                "completed": True,
                "stats": stats
            })
        
        # Get next question
        next_question = get_next_question(session_id)
        if not next_question:
            next_question = "Thank you for your responses. Do you have any questions for me?"
        
        # Check for follow-up based on response category
        if response_category:
            follow_up = get_follow_up_question(response_category, prev_question_id)
            if follow_up:
                next_question = follow_up

        if conn:
            conn.close()
            
        return jsonify({
            "completed": False,
            "next_question": next_question,
            "sentiment": sentiment,
            "category": response_category,
            "score": score,
            "question_number": question_number + 1
        })
        
    except Exception as e:
        if conn:
            try:
                conn.rollback()
                conn.close()
            except:
                pass
        print(f"Error in handle_interview: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "error": "Internal server error",
            "next_question": "Could you please elaborate on that?"
        }), 500

@interview_bp.route("/stats/<int:session_id>", methods=["GET"])
@login_required
def get_interview_stats(session_id):
    try:
        # Use raw SQL to get the session and verify it belongs to the current user
        conn = db.engine.raw_connection()
        cursor = conn.cursor()
        
        # Check if interview_mode column exists
        cursor.execute("PRAGMA table_info(interview_session)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Verify the session belongs to the current user and get session data
        if 'interview_mode' in columns:
            cursor.execute(
                "SELECT id, completed, interview_mode FROM interview_session WHERE id = ? AND user_id = ?",
                (session_id, current_user.id)
            )
        else:
            cursor.execute(
                "SELECT id, completed FROM interview_session WHERE id = ? AND user_id = ?",
                (session_id, current_user.id)
            )
        
        session_data = cursor.fetchone()
        
        if not session_data:
            conn.close()
            return jsonify({'error': 'Session not found'}), 404
        
        # Get all responses for this session
        cursor.execute(
            "SELECT question, response, sentiment, category, score FROM response WHERE session_id = ?",
            (session_id,)
        )
        responses = cursor.fetchall()
        
        # Calculate statistics
        total_questions = len(responses)
        if total_questions == 0:
            response_data = {
                'total_questions': 0,
                'average_score': 0,
                'average_response_length': 0,
                'completed': bool(session_data[1]),  # completed
                'sentiment_distribution': {},
                'category_distribution': {},
                'detailed_responses': [],
                'interview_mode': session_data[2] if 'interview_mode' in columns else 'text'  # Add interview mode
            }
            conn.close()
            return jsonify(response_data)

        # Calculate averages
        total_score = sum(r[4] for r in responses if r[4] is not None)
        total_length = sum(len(r[1]) for r in responses if r[1])
        
        # Calculate sentiment distribution
        sentiment_dist = {}
        for r in responses:
            if r[2]:  # sentiment
                sentiment_dist[r[2]] = sentiment_dist.get(r[2], 0) + 1

        # Calculate category distribution
        category_dist = {}
        for r in responses:
            if r[3]:  # category
                category_dist[r[3]] = category_dist.get(r[3], 0) + 1

        # Format detailed responses
        detailed_responses = [{
            'question': r[0],  # question
            'response': r[1],  # response
            'sentiment': r[2],  # sentiment
            'category': r[3],  # category
            'score': r[4] if r[4] is not None else 0  # score
        } for r in responses]

        conn.close()
        
        # Create response data with interview_mode
        response_data = {
            'total_questions': total_questions,
            'average_score': total_score / total_questions if total_questions > 0 else 0,
            'average_response_length': total_length / total_questions if total_questions > 0 else 0,
            'completed': bool(session_data[1]),  # completed
            'sentiment_distribution': sentiment_dist,
            'category_distribution': category_dist,
            'detailed_responses': detailed_responses,
            'interview_mode': session_data[2] if 'interview_mode' in columns else 'text'  # Add interview mode
        }
        
        return jsonify(response_data)

    except Exception as e:
        print(f"Error getting session stats: {str(e)}")
        print(traceback.format_exc())
        try:
            conn.close()
        except:
            pass
        return jsonify({'error': 'Failed to get session statistics'}), 500

@interview_bp.route("/sessions", methods=["GET"])
@login_required
def get_user_sessions():
    """Get all interview sessions for the current user."""
    try:
        # Query all sessions for the current user using raw SQL to avoid SQLAlchemy ORM issues
        # This is a temporary workaround until the database schema is properly updated
        conn = db.engine.raw_connection()
        cursor = conn.cursor()
        
        # Check if the interview_mode column exists
        cursor.execute("PRAGMA table_info(interview_session)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Construct the SQL query based on whether the interview_mode column exists
        if 'interview_mode' in columns:
            cursor.execute(
                "SELECT id, user_id, start_time, question_count, total_score, completed, last_category, categories_asked, interview_mode "
                "FROM interview_session WHERE user_id = ?",
                (current_user.id,)
            )
        else:
            cursor.execute(
                "SELECT id, user_id, start_time, question_count, total_score, completed, last_category, categories_asked "
                "FROM interview_session WHERE user_id = ?",
                (current_user.id,)
            )
        
        # Fetch all sessions
        sessions_raw = cursor.fetchall()
        
        # Format the sessions data
        sessions_data = []
        for session_raw in sessions_raw:
            # Get the session ID (first column)
            session_id = session_raw[0]
            
            # Query responses for this session
            cursor.execute(
                "SELECT score FROM response WHERE session_id = ?",
                (session_id,)
            )
            responses = cursor.fetchall()
            
            # Calculate scores
            total_score = sum(r[0] for r in responses if r[0] is not None)
            question_count = len(responses)
            avg_score = total_score / question_count if question_count > 0 else 0
            
            # Create session data dictionary
            session_data = {
                "id": session_id,
                "start_time": session_raw[2],  # start_time
                "question_count": question_count,
                "total_score": avg_score,
                "completed": bool(session_raw[5]),  # completed
            }
            
            # Add interview_mode if it exists
            if 'interview_mode' in columns:
                session_data["interview_mode"] = session_raw[8] or "text"  # interview_mode with default
            else:
                session_data["interview_mode"] = "text"  # Default to "text" if column doesn't exist
            
            sessions_data.append(session_data)
        
        conn.close()
        return jsonify({"sessions": sessions_data})
    except Exception as e:
        print(f"Error getting user sessions: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": "Could not retrieve user sessions"}), 500

@interview_bp.route("/session/<int:session_id>", methods=["GET"])
@login_required
def get_session(session_id):
    """Get details for a specific interview session."""
    try:
        # Use raw SQL to avoid SQLAlchemy ORM issues
        conn = db.engine.raw_connection()
        cursor = conn.cursor()
        
        # Check if the interview_mode column exists
        cursor.execute("PRAGMA table_info(interview_session)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Verify the session belongs to the current user
        if 'interview_mode' in columns:
            cursor.execute(
                "SELECT id, user_id, start_time, question_count, total_score, completed, last_category, categories_asked, interview_mode "
                "FROM interview_session WHERE id = ? AND user_id = ?",
                (session_id, current_user.id)
            )
        else:
            cursor.execute(
                "SELECT id, user_id, start_time, question_count, total_score, completed, last_category, categories_asked "
                "FROM interview_session WHERE id = ? AND user_id = ?",
                (session_id, current_user.id)
            )
        
        session_raw = cursor.fetchone()
        
        if not session_raw:
            conn.close()
            return jsonify({"error": "Session not found"}), 404
        
        # Get all responses for this session
        cursor.execute(
            "SELECT question, response, sentiment, category, score "
            "FROM response WHERE session_id = ?",
            (session_id,)
        )
        responses_raw = cursor.fetchall()
        
        # Format the responses
        formatted_responses = []
        for response in responses_raw:
            formatted_responses.append({
                "question_text": response[0],  # question
                "response_text": response[1],  # response
                "sentiment": response[2],      # sentiment
                "category": response[3],       # category
                "score": response[4]           # score
            })
        
        # Calculate total score (average of all response scores)
        total_score = 0
        if responses_raw:
            total_score = sum(r[4] for r in responses_raw if r[4] is not None) / len(responses_raw)
        
        # Create the response JSON
        session_data = {
            "id": session_raw[0],              # id
            "start_time": session_raw[2],      # start_time
            "end_time": None,                  # We don't have end_time in the raw query
            "completed": bool(session_raw[5]), # completed
            "total_score": total_score,
            "responses": formatted_responses
        }
        
        # Add interview_mode if it exists
        if 'interview_mode' in columns:
            session_data["interview_mode"] = session_raw[8] or "text"  # interview_mode with default
        else:
            session_data["interview_mode"] = "text"  # Default to "text" if column doesn't exist
        
        conn.close()
        return jsonify(session_data)
    except Exception as e:
        # Log the full error
        print(f"Error in get_session: {str(e)}")
        print(traceback.format_exc())
        try:
            conn.close()
        except:
            pass
        return jsonify({"error": "Failed to get session data"}), 500

@interview_bp.route("/session/<int:session_id>", methods=["DELETE"])
@login_required
def delete_session(session_id):
    """Delete an interview session by ID."""
    conn = None
    try:
        # Log full request info
        print(f"\n==== DELETE REQUEST FOR SESSION {session_id} ====")
        print(f"Method: {request.method}")
        print(f"Headers: {dict(request.headers)}")
        print(f"Authenticated User ID: {current_user.id if current_user and current_user.is_authenticated else 'Not authenticated'}")
        print(f"Session Cookie: {'Present' if request.cookies.get('session') else 'Not present'}")
        
        if not current_user.is_authenticated:
            print("User not authenticated in delete_session")
            return jsonify({"error": "Authentication required"}), 401
        
        # Make sure the session belongs to the current user using raw SQL
        conn = db.engine.raw_connection()
        cursor = conn.cursor()
        
        # First check if the session exists
        cursor.execute(
            "SELECT id FROM interview_session WHERE id = ?",
            (session_id,)
        )
        session = cursor.fetchone()
        
        if not session:
            conn.close()
            print(f"Session {session_id} not found")
            return jsonify({"error": "Session not found"}), 404
            
        # Now check if user owns this session
        cursor.execute(
            "SELECT user_id FROM interview_session WHERE id = ?",
            (session_id,)
        )
        owner_data = cursor.fetchone()
        
        if not owner_data or owner_data[0] != current_user.id:
            conn.close()
            print(f"Session {session_id} not owned by user {current_user.id}")
            return jsonify({"error": "Unauthorized"}), 403
        
        print(f"Session {session_id} found and authorized for deletion")
        
        # Check what columns exist in the response table
        cursor.execute("PRAGMA table_info(response)")
        columns = [column[1] for column in cursor.fetchall()]
        has_question_number = 'question_number' in columns
        
        # Get response count
        cursor.execute("SELECT COUNT(*) FROM response WHERE session_id = ?", (session_id,))
        count_result = cursor.fetchone()
        response_count = count_result[0] if count_result else 0
        print(f"Found {response_count} responses for session {session_id}")
        
        # Generate a range of possible question numbers
        question_numbers = list(range(1, response_count + 1))
        
        # If question_number column exists, try to get actual question numbers
        if has_question_number:
            try:
                cursor.execute(
                    "SELECT question_number FROM response WHERE session_id = ? AND question_number IS NOT NULL",
                    (session_id,)
                )
                question_nums_results = cursor.fetchall()
                if question_nums_results:
                    question_numbers = [r[0] for r in question_nums_results if r[0]]
                    print(f"Retrieved question numbers from database: {question_numbers}")
            except Exception as e:
                print(f"Error getting question numbers: {e}")
                # Fall back to using range
        
        # Database operation for deletion
        try:
            # Begin transaction
            cursor.execute("BEGIN TRANSACTION")
            
            # Delete all responses for this session
            cursor.execute(
                "DELETE FROM response WHERE session_id = ?",
                (session_id,)
            )
            responses_deleted = cursor.rowcount
            print(f"Deleted {responses_deleted} responses for session {session_id}")
            
            # Delete the session
            cursor.execute(
                "DELETE FROM interview_session WHERE id = ?",
                (session_id,)
            )
            sessions_deleted = cursor.rowcount
            print(f"Deleted session {session_id}, affected {sessions_deleted} rows")
            
            # Commit the transaction
            cursor.execute("COMMIT")
            conn.close()
            conn = None
            
            # Now handle audio file deletion
            uploads_dir = os.path.join(BACKEND_DIR, 'uploads')
            deleted_files = 0
            
            # Find files based on naming pattern, regardless of database entries
            if os.path.exists(uploads_dir):
                # First, find all audio files that match the pattern for this session
                session_audio_pattern = f"audio_{session_id}_"
                
                for filename in os.listdir(uploads_dir):
                    if filename.startswith(session_audio_pattern) and filename.endswith('.wav'):
                        try:
                            file_path = os.path.join(uploads_dir, filename)
                            os.remove(file_path)
                            deleted_files += 1
                            print(f"Deleted audio file: {file_path}")
                        except Exception as e:
                            print(f"Could not delete audio file {file_path}: {str(e)}")
            
            # Also try specific filenames based on question numbers
            for qnum in question_numbers:
                try:
                    audio_filename = f'audio_{session_id}_{qnum}.wav'
                    file_path = os.path.join(uploads_dir, audio_filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        deleted_files += 1
                        print(f"Deleted audio file by question number: {file_path}")
                except Exception as e:
                    print(f"Error checking/deleting question-based audio file: {e}")
                            
            print(f"Successfully deleted session {session_id} with {responses_deleted} responses and {deleted_files} audio files")
            return jsonify({"success": True, "message": "Interview session deleted successfully"})
        except Exception as e:
            # Rollback the transaction in case of error
            print(f"Error during transaction, rolling back: {str(e)}")
            if conn:
                cursor.execute("ROLLBACK")
                conn.close()
                conn = None
            raise e
    except Exception as e:
        print(f"Error deleting session {session_id}: {str(e)}")
        print(traceback.format_exc())
        if conn:
            try:
                conn.close()
            except:
                pass
        return jsonify({"error": f"Could not delete session: {str(e)}"}), 500

@interview_bp.route("/submit-audio", methods=["POST"])
@login_required
def submit_audio():
    """Handle audio submission from the audio interview page."""
    try:
        # Check if audio file is in the request
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        if not audio_file:
            return jsonify({"error": "Empty audio file"}), 400
        
        # Ensure uploads directory exists
        uploads_dir = os.path.join(BACKEND_DIR, 'uploads')
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        
        # Get session ID and question number from form data
        session_id = request.form.get('session_id')
        question_number = request.form.get('question_number')
        current_question = request.form.get('current_question', 'Interview Question')
        
        if not session_id or not question_number:
            return jsonify({"error": "Missing session ID or question number"}), 400
        
        # Convert to integers
        try:
            session_id = int(session_id)
            question_number = int(question_number)
        except ValueError:
            return jsonify({"error": "Invalid session ID or question number"}), 400
        
        # Verify session belongs to current user
        conn = db.engine.raw_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT user_id, question_count FROM interview_session WHERE id = ?",
            (session_id,)
        )
        session_data = cursor.fetchone()
        
        if not session_data or session_data[0] != current_user.id:
            conn.close()
            return jsonify({"error": "Invalid session"}), 403
        
        # No need to query for current question since we get it from form data
        
        # Save audio file to a temporary location (optional)
        # audio_file.save(os.path.join('uploads', f'audio_{session_id}_{question_number}.wav'))
        
        # Save audio file
        audio_filename = f'audio_{session_id}_{question_number}.wav'
        audio_path = os.path.join(uploads_dir, audio_filename)
        audio_file.save(audio_path)
        print(f"Audio saved to: {audio_path}")
        
        try:
            # Calculate score based on multiple factors
            score = calculate_audio_response_score(audio_path, current_question)
            
            # For audio submissions, we'll use a placeholder response text
            response_text = f"[Audio Response for Question {question_number}]"
            
            # Analyze sentiment and classify response
            sentiment = analyze_audio_sentiment(audio_path)
            response_category = classify_audio_response(audio_path, current_question)
            
            # Store the response
            try:
                # Check if input_type column exists in the response table
                cursor.execute("PRAGMA table_info(response)")
                columns = [column[1] for column in cursor.fetchall()]
                
                # Insert the response
                if 'input_type' in columns:
                    cursor.execute(
                        "INSERT INTO response (session_id, question, response, sentiment, category, input_type, score) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (session_id, current_question, response_text, sentiment, response_category, 'audio', score)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO response (session_id, question, response, sentiment, category, score) "
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        (session_id, current_question, response_text, sentiment, response_category, score)
                    )
            
                # Update the session
                cursor.execute(
                    "UPDATE interview_session SET question_count = question_count + 1, "
                    "total_score = total_score + ? WHERE id = ?",
                    (score, session_id)
                )
                
                # Check if this is the last question
                is_complete = question_number >= 10
                if is_complete:
                    cursor.execute(
                        "UPDATE interview_session SET completed = 1 WHERE id = ?",
                        (session_id,)
                    )
            
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"Error storing audio response: {str(e)}")
                raise
            
            if is_complete:
                # Get session statistics
                conn.close()
                conn = None
                stats = get_session_stats(session_id)
                return jsonify({
                    "completed": True,
                    "stats": stats
                })
            
            # Get next question
            next_question = get_next_question(session_id)
            if not next_question:
                next_question = "Thank you for your responses. Do you have any questions for me?"
            
            # Update the current question in the session
            if conn:
                try:
                    cursor.execute(
                        "UPDATE interview_session SET last_category = ? WHERE id = ?",
                        (response_category, session_id)
                    )
                    conn.commit()
                except Exception as e:
                    print(f"Error updating session: {str(e)}")
                finally:
                    conn.close()
            
            return jsonify({
                "completed": False,
                "next_question": next_question,
                "sentiment": sentiment,
                "category": response_category,
                "score": score,
                "question_number": question_number + 1
            })
        
        except Exception as e:
            print(f"Error calculating audio score: {str(e)}")
            print(traceback.format_exc())
            return jsonify({
                "error": "Failed to process audio submission",
                "next_question": "Could you please try again?"
            }), 500
        
    except Exception as e:
        print(f"Error in submit_audio: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "error": "Failed to process audio submission",
            "next_question": "Could you please try again?"
        }), 500

def calculate_audio_response_score(audio_path, question):
    """
    Calculate a comprehensive score for an audio response based on multiple factors.
    Returns a score between 1.0 and 5.0.
    """
    try:
        import wave
        import contextlib
        import numpy as np
        import librosa
        from pydub import AudioSegment
        
        # 1. Duration Analysis (25%)
        with contextlib.closing(wave.open(audio_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
        
        duration_score = 0.0
        if duration < 10:  # Too short
            duration_score = 2.0
        elif duration < 30:  # A bit short
            duration_score = 3.0
        elif duration <= 120:  # Ideal range
            duration_score = 5.0
        elif duration <= 180:  # A bit long
            duration_score = 4.0
        else:  # Too long
            duration_score = 3.0
        
        # 2. Audio Quality Analysis (25%)
        y, sr = librosa.load(audio_path)
        
        # Calculate signal-to-noise ratio
        noise_floor = np.mean(np.abs(y[y < np.mean(y)]))
        signal_strength = np.mean(np.abs(y[y > np.mean(y)]))
        snr = 20 * np.log10(signal_strength / (noise_floor + 1e-6))
        quality_score = min(5.0, max(1.0, (snr + 20) / 20))
        
        # 3. Speech Clarity Analysis (25%)
        # Calculate speech clarity using MFCCs
        mfccs = librosa.feature.mfcc(y=y, sr=sr)
        mfcc_var = np.var(mfccs)
        clarity_score = min(5.0, max(1.0, 3 + mfcc_var))
        
        # 4. Engagement Analysis (25%)
        # Calculate engagement based on pitch variation and energy dynamics
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_variation = np.std(pitches[pitches > 0])
        energy_variation = np.std(librosa.feature.rms(y=y))
        
        engagement_score = min(5.0, max(1.0, 
            2.5 + (pitch_variation / 100) + (energy_variation * 10)))
        
        # 5. Calculate final weighted score
        final_score = (
            0.25 * duration_score +     # Duration weight
            0.25 * quality_score +      # Audio quality weight
            0.25 * clarity_score +      # Speech clarity weight
            0.25 * engagement_score     # Engagement weight
        )
        
        # Ensure score is between 1.0 and 5.0
        final_score = min(5.0, max(1.0, final_score))
        
        return round(final_score, 2)
        
    except Exception as e:
        print(f"Error calculating audio score: {str(e)}")
        return 3.0  # Default score if analysis fails

def analyze_audio_sentiment(audio_path):
    """
    Analyze the sentiment of an audio response using multiple audio characteristics.
    Returns 'positive', 'negative', or 'neutral' based on comprehensive analysis.
    """
    try:
        import librosa
        import numpy as np
        from scipy.stats import skew
        
        # Load the audio file
        y, sr = librosa.load(audio_path)
        
        # 1. Extract audio features
        # Mel-frequency cepstral coefficients (tone and vocal characteristics)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_means = np.mean(mfccs, axis=1)
        
        # Spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        
        # Energy and tempo features
        tempo = librosa.beat.tempo(y=y, sr=sr)[0]
        energy = np.mean(librosa.feature.rms(y=y))
        
        # Zero crossing rate (voice characteristics)
        zcr = librosa.feature.zero_crossing_rate(y=y)[0]
        
        # 2. Calculate derived metrics
        energy_variance = np.var(librosa.feature.rms(y=y))
        pitch_variance = np.var(librosa.yin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7')))
        speech_rate = len(librosa.onset.onset_detect(y=y, sr=sr)) / (len(y) / sr)
        
        # 3. Score each component
        scores = {
            'energy_score': 1 if energy > 0.1 else (-1 if energy < 0.05 else 0),
            'tempo_score': 1 if tempo > 120 else (-1 if tempo < 90 else 0),
            'variance_score': 1 if energy_variance > 0.01 else (-1 if energy_variance < 0.005 else 0),
            'pitch_score': 1 if pitch_variance > 0.1 else (-1 if pitch_variance < 0.05 else 0),
            'speech_rate_score': 1 if speech_rate > 2.5 else (-1 if speech_rate < 1.5 else 0)
        }
        
        # 4. Calculate weighted sentiment score
        weights = {
            'energy_score': 0.3,
            'tempo_score': 0.2,
            'variance_score': 0.2,
            'pitch_score': 0.15,
            'speech_rate_score': 0.15
        }
        
        total_score = sum(scores[key] * weights[key] for key in scores)
        
        # 5. Determine sentiment based on total score
        if total_score > 0.3:
            return 'positive'
        elif total_score < -0.3:
            return 'negative'
        else:
            return 'neutral'
            
    except Exception as e:
        print(f"Error analyzing audio sentiment: {str(e)}")
        return 'neutral'

def classify_audio_response(audio_path, question):
    """
    Classify the type of audio response based on the question and audio characteristics.
    Returns a response category.
    """
    try:
        # For now, return a basic classification based on the question
        question_lower = question.lower()
        
        if 'experience' in question_lower or 'tell me about' in question_lower:
            return 'narrative'
        elif 'why' in question_lower:
            return 'reasoning'
        elif 'how would you' in question_lower or 'what would you' in question_lower:
            return 'problem-solving'
        elif 'strength' in question_lower or 'weakness' in question_lower:
            return 'self-assessment'
        else:
            return 'general'
            
    except Exception as e:
        print(f"Error classifying audio response: {str(e)}")
        return 'general'
