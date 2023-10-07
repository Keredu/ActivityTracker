import sqlite3

def clear_activities():
    # Connect to the SQLite database
    conn = sqlite3.connect("activity_tracker.db")
    cursor = conn.cursor()

    # Clear the activities table
    cursor.execute("DELETE FROM activities")
    conn.commit()

    print("All activities have been cleared!")

    # Close the connection
    conn.close()

if __name__ == "__main__":
    clear_activities()
