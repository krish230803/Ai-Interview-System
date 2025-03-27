import sqlite3
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'interview_data.db')

print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Add the input_type column to the response table
    print("Adding the input_type column to the response table...")
    cursor.execute('ALTER TABLE response ADD COLUMN input_type VARCHAR(20) DEFAULT "text"')
    conn.commit()
    print("Column added successfully.")
    
    # Verify the column was added
    cursor.execute("PRAGMA table_info(response)")
    columns = cursor.fetchall()
    
    print("\nColumns in response table after adding input_type:")
    for column in columns:
        print(f"Column {column[0]}: {column[1]} ({column[2]})")
    
    if any(column[1] == 'input_type' for column in columns):
        print("\nVerified: The input_type column now exists in the response table.")
    else:
        print("\nError: Failed to add the input_type column.")
    
except sqlite3.Error as e:
    print(f"Database error: {e}")
    conn.rollback()
finally:
    conn.close()
    print("Database connection closed.") 