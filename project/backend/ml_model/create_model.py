from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
import os

# Get the absolute path to the backend directory
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Sample training data with more examples for each category
X_train = [
    # Introduction examples
    "I am a software engineer with 5 years of experience",
    "I have been working in tech for the past 3 years",
    "My background is in computer science and software development",
    "I recently graduated with a degree in computer engineering",
    "I'm currently working as a full-stack developer",
    
    # Strengths examples
    "I am good at problem solving and communication",
    "My strongest skills are debugging and system design",
    "I excel at team collaboration and project management",
    "I have strong analytical and technical skills",
    "Time management and organization are my key strengths",
    
    # Goals examples
    "I want to grow in my career and take on leadership roles",
    "My goal is to become a technical architect",
    "I aim to develop expertise in cloud technologies",
    "I want to lead development teams and mentor others",
    "I see myself growing into a senior technical position",
    
    # Project examples
    "I worked on a large-scale distributed system",
    "I developed a real-time data processing pipeline",
    "I built a machine learning model for customer predictions",
    "I implemented a microservices architecture",
    "I created a mobile application from scratch",
    
    # Stress management examples
    "I handle stress by breaking down tasks into smaller parts",
    "I maintain work-life balance through proper planning",
    "I use time management techniques to handle pressure",
    "I stay organized and prioritize tasks when stressed",
    "I practice mindfulness and take regular breaks",
    
    # Leadership examples
    "I led a team of five developers on a critical project",
    "I mentored junior developers and helped them grow",
    "I coordinated between different teams to deliver projects",
    "I initiated and managed code review processes",
    "I organized technical training sessions for the team"
]

y_train = (
    ["introduction"] * 5 +
    ["strengths"] * 5 +
    ["goals"] * 5 +
    ["project"] * 5 +
    ["stress"] * 5 +
    ["leadership"] * 5
)

# Create and train the vectorizer
vectorizer = TfidfVectorizer(
    max_features=1000,
    stop_words='english',
    ngram_range=(1, 2)
)
X_train_tfidf = vectorizer.fit_transform(X_train)

# Train the model
model = MultinomialNB(alpha=1.0)
model.fit(X_train_tfidf, y_train)

# Save the model and vectorizer
model_path = os.path.join(BACKEND_DIR, 'ml_model', 'interview_classifier.pkl')
vectorizer_path = os.path.join(BACKEND_DIR, 'ml_model', 'tfidf_vectorizer.pkl')

with open(model_path, 'wb') as f:
    pickle.dump(model, f)
with open(vectorizer_path, 'wb') as f:
    pickle.dump(vectorizer, f)

print("Model and vectorizer have been created and saved successfully!")
print(f"Model saved to: {model_path}")
print(f"Vectorizer saved to: {vectorizer_path}") 