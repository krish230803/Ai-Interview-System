import sys
import os
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import KFold
import seaborn as sns
import matplotlib.pyplot as plt

# Add the backend directory to Python path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BACKEND_DIR)

from app.models.interview import classify_response, preprocess_text

# Test data with different variations of responses
TEST_DATA = {
    "introduction": [
        "I've been a software developer for 6 years",
        "My background is in computer engineering",
        "I work as a full-stack developer",
        "I have experience in cloud computing and DevOps",
        "Recently graduated with a Masters in AI"
    ],
    "strengths": [
        "I'm excellent at debugging complex issues",
        "Communication is my strongest skill",
        "I have great attention to detail",
        "Time management is one of my key strengths",
        "I'm very good at coordinating with teams"
    ],
    "goals": [
        "I plan to become a solution architect",
        "Looking to expand my skills in cloud technologies",
        "Want to move into a senior developer position",
        "Interested in learning more about AI and ML",
        "Hope to lead development teams in the future"
    ],
    "project": [
        "Built a scalable microservices architecture",
        "Implemented a real-time chat application",
        "Created an automated testing framework",
        "Developed a mobile payment system",
        "Led the migration to cloud infrastructure"
    ],
    "stress": [
        "I use time management to handle pressure",
        "Taking short breaks helps me stay focused",
        "I prioritize tasks when under deadline",
        "Exercise helps me manage work stress",
        "I stay calm by breaking down complex problems"
    ],
    "teamwork": [
        "I enjoy pair programming sessions",
        "Regular team meetings help align our goals",
        "I support my colleagues when needed",
        "Communication is key in team projects",
        "I value feedback from team members"
    ],
    "leadership": [
        "I coordinated a team of 3 developers",
        "Mentored 2 junior developers last year",
        "Started our weekly tech sharing sessions",
        "Implemented agile methodologies in our team",
        "Managed the release process for our product"
    ]
}

def evaluate_model():
    try:
        # Prepare test data
        X_test = []
        y_test = []
        for category, examples in TEST_DATA.items():
            for example in examples:
                X_test.append(example)
                y_test.append(category)
        
        print("\nStarting model evaluation...")
        print(f"Total test samples: {len(X_test)}")
        print(f"Categories: {list(TEST_DATA.keys())}")
        print("-" * 80)
        
        # Get predictions
        y_pred = []
        print("Making predictions...")
        for i, text in enumerate(X_test, 1):
            try:
                prediction = classify_response(text)
                y_pred.append(prediction)
                print(f"Processed {i}/{len(X_test)} samples", end='\r')
            except Exception as e:
                print(f"\nError predicting for text: {text}")
                print(f"Error: {str(e)}")
                y_pred.append(None)
        
        # Remove any None predictions
        valid_predictions = [(y_t, y_p) for y_t, y_p in zip(y_test, y_pred) if y_p is not None]
        if not valid_predictions:
            print("\nNo valid predictions were made!")
            return
        
        y_test_valid, y_pred_valid = zip(*valid_predictions)
        
        # Calculate and display accuracy
        accuracy = accuracy_score(y_test_valid, y_pred_valid)
        print(f"\nOverall Model Accuracy: {accuracy:.2%}")
        
        # Print detailed classification report
        print("\nDetailed Classification Report:")
        print("-" * 80)
        report = classification_report(y_test_valid, y_pred_valid)
        print(report)
        
        # Create and save confusion matrix
        print("\nGenerating confusion matrix...")
        cm = confusion_matrix(y_test_valid, y_pred_valid)
        plt.figure(figsize=(12, 8))
        sns.heatmap(cm, 
                    annot=True, 
                    fmt='d', 
                    xticklabels=list(TEST_DATA.keys()),
                    yticklabels=list(TEST_DATA.keys()))
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.xticks(rotation=45)
        plt.yticks(rotation=45)
        plt.tight_layout()
        
        # Save confusion matrix
        matrix_path = os.path.join(BACKEND_DIR, 'ml_model', 'confusion_matrix.png')
        plt.savefig(matrix_path)
        plt.close()
        print(f"Confusion matrix saved to: {matrix_path}")
        
        # Print example predictions
        print("\nExample Predictions:")
        print("-" * 80)
        for i, (text, true_label, pred_label) in enumerate(zip(X_test, y_test, y_pred)):
            if i % 5 == 0:  # Print one example from each category
                print(f"Text: {text}")
                print(f"True Category: {true_label}")
                print(f"Predicted Category: {pred_label}")
                print(f"Correct: {true_label == pred_label}")
                print("-" * 80)
        
    except Exception as e:
        print(f"\nAn error occurred during evaluation: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    evaluate_model()
