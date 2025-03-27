import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd

# Load the training data (for demonstration, we'll use a sample CSV file)
# You can replace this with your custom dataset
data = pd.read_csv("../data/interview_data.csv")  # Replace with your data file

# Split the dataset into features (X) and target labels (y)
X = data['response']  # Responses from the user (text data)
y = data['category']  # Categories of the responses (labels)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Initialize a TfidfVectorizer to convert text data into numeric features
vectorizer = TfidfVectorizer(stop_words='english')

# Fit the vectorizer to the training data and transform the responses
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Initialize a Logistic Regression model
model = LogisticRegression()

# Train the model
model.fit(X_train_tfidf, y_train)

# Predict on the test set
y_pred = model.predict(X_test_tfidf)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Save the trained model and vectorizer using pickle
with open('../ml_model/interview_classifier.pkl', 'wb') as model_file:
    pickle.dump(model, model_file)

with open('../ml_model/tfidf_vectorizer.pkl', 'wb') as vectorizer_file:
    pickle.dump(vectorizer, vectorizer_file)
