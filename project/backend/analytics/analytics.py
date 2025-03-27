import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob
import os
import json
import datetime

# Directory to save analytics data
analytics_dir = "analytics_data"
if not os.path.exists(analytics_dir):
    os.makedirs(analytics_dir)

# Sample CSV file to store user responses
responses_file = os.path.join(analytics_dir, "user_responses.csv")

# Function to log user responses along with sentiment and category
def log_user_response(user_id, question, response, category, sentiment_score, response_time):
    data = {
        "user_id": user_id,
        "question": question,
        "response": response,
        "category": category,
        "sentiment_score": sentiment_score,
        "response_time": response_time,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Check if the CSV file exists
    if os.path.exists(responses_file):
        df = pd.read_csv(responses_file)
        df = df.append(data, ignore_index=True)
    else:
        # Create a new dataframe if file doesn't exist
        df = pd.DataFrame([data])

    # Save to CSV file
    df.to_csv(responses_file, index=False)
    print("Response logged successfully.")

# Function to calculate sentiment of user responses
def analyze_sentiment(response):
    blob = TextBlob(response)
    sentiment_score = blob.sentiment.polarity
    sentiment = "Positive" if sentiment_score > 0 else "Negative" if sentiment_score < 0 else "Neutral"
    return sentiment, sentiment_score

# Function to generate sentiment analysis report
def sentiment_analysis_report():
    if os.path.exists(responses_file):
        df = pd.read_csv(responses_file)
        sentiment_counts = df['sentiment_score'].apply(lambda x: "Positive" if x > 0 else "Negative" if x < 0 else "Neutral").value_counts()

        # Plotting sentiment distribution
        sentiment_counts.plot(kind='bar', color=['green', 'red', 'gray'], title='Sentiment Distribution')
        plt.xlabel('Sentiment')
        plt.ylabel('Number of Responses')
        plt.tight_layout()
        plt.savefig(os.path.join(analytics_dir, "sentiment_distribution.png"))
        plt.show()
        return sentiment_counts
    else:
        print("No data found for sentiment analysis.")
        return None

# Function to analyze user performance by category
def performance_by_category():
    if os.path.exists(responses_file):
        df = pd.read_csv(responses_file)
        category_performance = df['category'].value_counts()

        # Plotting performance by category
        category_performance.plot(kind='bar', color='skyblue', title='Performance by Category')
        plt.xlabel('Category')
        plt.ylabel('Number of Responses')
        plt.tight_layout()
        plt.savefig(os.path.join(analytics_dir, "performance_by_category.png"))
        plt.show()
        return category_performance
    else:
        print("No data found for performance analysis.")
        return None

# Function to track response time
def track_response_time():
    if os.path.exists(responses_file):
        df = pd.read_csv(responses_file)
        avg_response_time = df['response_time'].mean()
        max_response_time = df['response_time'].max()
        min_response_time = df['response_time'].min()

        print(f"Average Response Time: {avg_response_time:.2f} seconds")
        print(f"Maximum Response Time: {max_response_time:.2f} seconds")
        print(f"Minimum Response Time: {min_response_time:.2f} seconds")

        return avg_response_time, max_response_time, min_response_time
    else:
        print("No data found for response time analysis.")
        return None, None, None

# Function to generate a comprehensive report
def generate_comprehensive_report():
    sentiment_report = sentiment_analysis_report()
    category_report = performance_by_category()
    avg_response_time, max_response_time, min_response_time = track_response_time()

    # Create a JSON report with the results
    report = {
        "sentiment_report": sentiment_report.to_dict() if sentiment_report is not None else {},
        "category_report": category_report.to_dict() if category_report is not None else {},
        "response_time": {
            "average_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "min_response_time": min_response_time,
        }
    }

    report_file = os.path.join(analytics_dir, "comprehensive_report.json")
    with open(report_file, 'w') as json_file:
        json.dump(report, json_file, indent=4)
    
    print(f"Comprehensive report saved to {report_file}.")

# Example usage of the functions:
if __name__ == "__main__":
    # Simulate logging user responses (In your application, you would replace this part with actual responses)
    user_id = "user_001"
    question = "Tell me about yourself"
    response = "I am a software developer with experience in building web applications."
    category = "Personal"
    sentiment, sentiment_score = analyze_sentiment(response)
    response_time = 12.5  # In seconds (example)

    # Log the response
    log_user_response(user_id, question, response, category, sentiment_score, response_time)

    # Generate and display analytics
    generate_comprehensive_report()
