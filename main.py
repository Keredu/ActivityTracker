import sqlite3
from datetime import datetime

# Connect to SQLite database (it will create it if not existent)
conn = sqlite3.connect("activity_tracker.db")
cursor = conn.cursor()

def create_tables():
    """Create necessary tables in the database."""
    
    # Table for tracking activities
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY,
        start_time DATETIME,
        end_time DATETIME,
        topic TEXT,
        activity TEXT,
        FOREIGN KEY(topic) REFERENCES valid_topics(topic),
        FOREIGN KEY(activity) REFERENCES valid_activities(activity)
    )
    """)
    
    # Table for valid topics
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS valid_topics (
        topic TEXT PRIMARY KEY
    )
    """)
    
    # Table for valid activities associated with topics
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS valid_activities (
        activity TEXT,
        topic TEXT,
        FOREIGN KEY(topic) REFERENCES valid_topics(topic)
    )
    """)
    
    conn.commit()

def validate_datetime_format(dt_str):
    """Validate if the given string matches the datetime format."""
    try:
        datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        return True
    except ValueError:
        return False

def add_valid_topic(topic):
    """Add a valid topic to the database."""
    cursor.execute("INSERT OR IGNORE INTO valid_topics (topic) VALUES (?)", (topic,))
    conn.commit()

def add_valid_activity(activity, topic):
    """Add a valid activity associated with a topic to the database."""
    cursor.execute("INSERT OR IGNORE INTO valid_activities (activity, topic) VALUES (?, ?)", (activity, topic))
    conn.commit()

def list_valid_topics():
    """List all valid topics."""
    cursor.execute("SELECT topic FROM valid_topics")
    topics = cursor.fetchall()
    return [t[0] for t in topics]

def list_valid_activities(topic):
    """List valid activities for a given topic."""
    cursor.execute("SELECT activity FROM valid_activities WHERE topic=?", (topic,))
    activities = cursor.fetchall()
    return [a[0] for a in activities]

def start_activity(topic, activity):
    """Start a new activity and store the start time."""
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
    INSERT INTO activities (start_time, end_time, topic, activity) 
    VALUES (?, ?, ?, ?)
    """, (start_time, None, topic, activity))
    conn.commit()
    return cursor.lastrowid

def end_activity(activity_id):
    """End the current activity and store the end time."""
    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
    UPDATE activities SET end_time = ? WHERE id = ?
    """, (end_time, activity_id))
    conn.commit()

def add_previous_activity(start_time, end_time, topic, activity):
    """Add details of a previously done activity."""
    cursor.execute("""
    INSERT INTO activities (start_time, end_time, topic, activity) 
    VALUES (?, ?, ?, ?)
    """, (start_time, end_time, topic, activity))
    conn.commit()

def main():
    """Main function for the Activity Tracker."""
    create_tables()
    current_activity_id = None

    while True:
        print("\nActivity Tracker:")
        print("1. Start new activity")
        print("2. End current activity")
        print("3. Add a previous activity")
        print("4. Add a valid topic")
        print("5. Add a valid activity to a topic")
        print("6. List valid topics and activities")
        print("7. Quit")

        choice = input("Enter your choice: ")

        if choice == "1":
            topic = input("Enter the topic (e.g., work, projects): ")
            activity = input("Enter the activity: ")
            if topic in list_valid_topics() and activity in list_valid_activities(topic):
                current_activity_id = start_activity(topic, activity)
                print(f"Started activity '{activity}'.")
            else:
                print("Invalid topic or activity. Make sure they are added to the valid list.")

        elif choice == "2":
            if not current_activity_id:
                print("No ongoing activity to end.")
                continue
            end_activity(current_activity_id)
            print("Activity ended successfully!")
            current_activity_id = None

        elif choice == "3":
            start_time = input("Enter the start time (YYYY-MM-DD HH:MM:SS): ")
            if not validate_datetime_format(start_time):
                print("Invalid start time format. Please use 'YYYY-MM-DD HH:MM:SS'")
                continue

            end_time = input("Enter the end time (YYYY-MM-DD HH:MM:SS): ")
            if not validate_datetime_format(end_time):
                print("Invalid end time format. Please use 'YYYY-MM-DD HH:MM:SS'")
                continue

            topic = input("Enter the topic (e.g., work, personal-projects): ")
            activity = input("Describe the activity: ")
            if topic in list_valid_topics() and activity in list_valid_activities(topic):
                add_previous_activity(start_time, end_time, topic, activity)
                print("Previous activity added successfully!")
            else:
                print("Invalid topic or activity. Make sure they are added to the valid list.")

        elif choice == "4":
            topic = input("Enter a valid topic: ")
            add_valid_topic(topic)
            print(f"Added topic '{topic}' to valid topics.")

        elif choice == "5":
            topic = input("Enter the topic for the activity: ")
            if topic not in list_valid_topics():
                print("Invalid topic. Please enter a valid topic first.")
                continue
            activity = input("Enter a valid activity for the topic: ")
            add_valid_activity(activity, topic)
            print(f"Added activity '{activity}' for topic '{topic}'.")

        elif choice == "6":
            print("Valid Topics and Activities:")
            for topic in list_valid_topics():
                print(f"- {topic}:")
                for activity in list_valid_activities(topic):
                    print(f"  - {activity}")

        elif choice == "7":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

# Close the connection when done
conn.close()
