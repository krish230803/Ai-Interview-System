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
    # List all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("\nTables in the database:")
    for table in tables:
        print(f"- {table[0]}")
    
    # Check the schema of the response table
    cursor.execute("PRAGMA table_info(response)")
    columns = cursor.fetchall()
    
    print("\nColumns in response table:")
    for column in columns:
        print(f"Column {column[0]}: {column[1]} ({column[2]})")
    
    # Check if the input_type column exists
    if any(column[1] == 'input_type' for column in columns):
        print("\nThe input_type column exists in the response table.")
    else:
        print("\nThe input_type column DOES NOT exist in the response table.")
        
        # Add the column if it doesn't exist
        print("Adding the input_type column...")
        cursor.execute('ALTER TABLE response ADD COLUMN input_type VARCHAR(20) DEFAULT "text"')
        conn.commit()
        print("Column added successfully.")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(response)")
        columns = cursor.fetchall()
        if any(column[1] == 'input_type' for column in columns):
            print("Verified: The input_type column now exists in the response table.")
        else:
            print("Error: Failed to add the input_type column.")
    
    # Check the schema of the interview_session table
    cursor.execute("PRAGMA table_info(interview_session)")
    columns = cursor.fetchall()
    
    print("\nColumns in interview_session table:")
    for column in columns:
        print(f"Column {column[0]}: {column[1]} ({column[2]})")
    
except sqlite3.Error as e:
    print(f"Database error: {e}")
    conn.rollback()
finally:
    conn.close() 