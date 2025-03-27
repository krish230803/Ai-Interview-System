# AI Interview Assistant

An intelligent interview practice platform that conducts both text and audio-based mock interviews, providing real-time feedback and detailed analytics.

## Features

- Text and Audio-based interviews
- Real-time sentiment analysis
- Response scoring and feedback
- Detailed performance analytics and visualization
- Audio performance analysis
- User authentication and password recovery
- Interview history tracking
- Comprehensive performance statistics
- Interactive dashboard
- Secure file uploads and processing

## Project Structure

```
project/
├── backend/
│   ├── app/
│   ├── analytics/        # Analytics processing
│   ├── data/            # Data storage
│   ├── flask_session/   # Session management
│   ├── instance/        # Instance-specific files
│   ├── migrations/      # Database migrations
│   ├── ml_model/        # Machine learning models
│   ├── routes/          # API endpoints
│   ├── storage/         # Persistent storage
│   ├── uploads/         # User uploads
│   ├── AUDIO/          # Audio processing
│   ├── config.py        # Configuration
│   ├── init_db.py      # Database initialization
│   ├── requirements.txt # Dependencies
│   └── wsgi.py         # WSGI entry point
├── frontend/
│   ├── assets/
│   │   ├── css/
│   │   └── js/
│   ├── index.html       # Landing page
│   ├── login.html       # Authentication
│   ├── register.html    # User registration
│   ├── forgot-password.html  # Password recovery
│   ├── reset-password.html   # Password reset
│   ├── dashboard.html   # User dashboard
│   ├── stats.html       # Interview statistics
│   ├── text-interview.html   # Text interview interface
│   ├── audio-interview.html  # Audio interview interface
│   ├── audio-performance.html # Audio performance analysis
│   └── server.py       # Development server
├── fix_audio_complete.py
├── fix_audio_performance_complete.py
├── fix_audio_performance.py
├── fix_endpoint.py
├── fix_name_update.py
├── setup.sh
└── .gitignore
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher (for development)
- SQLite3
- Modern web browser with WebRTC support for audio features

### Backend Setup

1. Create a virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the backend directory with:
   ```
   FLASK_APP=wsgi.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///interview_data.db
   UPLOAD_FOLDER=uploads
   AUDIO_FOLDER=AUDIO
   ```

4. Initialize the database:
   ```bash
   python init_db.py
   ```

### Frontend Setup

1. Configure API endpoint:
   - Open `frontend/assets/js/config.js`
   - Update API endpoints if needed

2. Serve the frontend:
   - For development:
     ```bash
     cd frontend
     python server.py
     ```
   - For production, configure your web server (nginx/Apache) to serve the static files

### Running the Application

1. Start the backend server:
   ```bash
   cd backend
   flask run
   ```

2. Access the application:
   - Open `http://localhost:5000` in your browser (or the configured port)
   - Register a new account or login

### Audio Features Setup

1. Ensure proper microphone permissions in your browser
2. Create required directories:
   ```bash
   mkdir -p backend/AUDIO
   mkdir -p backend/uploads
   ```
3. Test audio recording functionality in a supported browser

## Development Guidelines

1. Code Style
   - Follow PEP 8 for Python code
   - Use ESLint for JavaScript
   - Maintain consistent HTML/CSS formatting

2. Version Control
   - Create feature branches for new development
   - Write descriptive commit messages
   - Review code before merging

3. Testing
   - Write unit tests for new features
   - Test both text and audio interview modes
   - Verify ML model performance

## Security Considerations

1. User Authentication
   - Implement rate limiting for login attempts
   - Use secure password hashing
   - Enable session timeout
   - Secure password reset functionality
   - Email verification for account changes

2. Data Protection
   - Sanitize user inputs
   - Validate file uploads and audio recordings
   - Secure API endpoints
   - Implement file size limits
   - Scan uploaded files for malware

3. Environment Variables
   - Never commit sensitive data
   - Use environment variables for configuration
   - Rotate secret keys regularly
   - Separate development and production configs

## Maintenance

1. Regular Tasks
   - Clean up uploaded files and audio recordings
   - Monitor log files
   - Update ML models
   - Backup database
   - Check audio processing performance
   - Monitor system resources

2. Updates
   - Keep dependencies updated
   - Check for security vulnerabilities
   - Update ML models periodically
   - Monitor audio processing quality
   - Update browser compatibility

3. Performance Monitoring
   - Track API response times
   - Monitor audio processing latency
   - Check database query performance
   - Analyze user feedback
   - Monitor error rates

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For support, please open an issue in the repository or contact the development team. 