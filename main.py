import sqlite3
from datetime import datetime

DB_NAME = "activity_tracker.db"

def connect_db():
    """Create a connection to the SQLite database."""
    return sqlite3.connect(DB_NAME)

def create_tables(conn):
    """Create necessary tables in the database."""
    cursor = conn.cursor()
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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS valid_topics (
        topic TEXT PRIMARY KEY
    )
    """)

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

def add_valid_topic(conn, topic):
    """Add a valid topic to the database."""
    with conn:  # Using the connection as a context manager
        conn.execute("INSERT OR IGNORE INTO valid_topics (topic) VALUES (?)", (topic,))

def add_valid_activity(conn, activity, topic):
    """Add a valid activity associated with a topic to the database."""
    with conn:
        conn.execute("INSERT OR IGNORE INTO valid_activities (activity, topic) VALUES (?, ?)", (activity, topic))

def list_valid_topics(conn):
    """List all valid topics."""
    cursor = conn.cursor()
    cursor.execute("SELECT topic FROM valid_topics")
    topics = cursor.fetchall()
    return [t[0] for t in topics]

def list_valid_activities(conn, topic):
    """List valid activities for a given topic."""
    cursor = conn.cursor()
    cursor.execute("SELECT activity FROM valid_activities WHERE topic=?", (topic,))
    activities = cursor.fetchall()
    return [a[0] for a in activities]

def add_previous_activity(conn, start_time, end_time, topic, activity):
    """Add details of a previously done activity."""
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO activities (start_time, end_time, topic, activity) 
    VALUES (?, ?, ?, ?)
    """, (start_time, end_time, topic, activity))
    conn.commit()

def start_activity(topic, activity):
    """Start a new activity and return the start time."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S'), topic, activity

def store_activity(conn, start_time, topic, activity):
    """Store the started activity in the database."""
    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with conn:
        conn.execute("""
        INSERT INTO activities (start_time, end_time, topic, activity) 
        VALUES (?, ?, ?, ?)
        """, (start_time, end_time, topic, activity))

def main(conn):
    """Main function for the Activity Tracker."""
    create_tables(conn)
    current_activity = None  
    valid_topics = list_valid_topics(conn)
    valid_activities = {topic: list_valid_activities(conn, topic) for topic in valid_topics}
        
    while True:
        print("\nActivity Tracker:")
        print("1. Start new activity")
        print("2. Add a previous activity")
        print("3. Add a valid topic")
        print("4. Add a valid activity to a topic")
        print("5. List valid topics and activities")
        print("6. Quit")
        choice = input("Enter your choice: ")

        if choice == "1":
            topic = input("Enter the topic (e.g., work, projects): ")
            activity = input("Enter the activity: ")
            if topic in valid_topics and activity in valid_activities.get(topic, []):
                if current_activity:
                    print("There's an ongoing activity. Please end or cancel it first.")
                    continue
                current_activity = start_activity(topic, activity)
                print(f"Started activity '{activity}'.")
                print("Press 'e' and Enter to end the activity. Press 'c' and Enter to cancel the activity.")
                
                while True:
                    key = input()
                    if key.lower() == 'e':
                        store_activity(conn, *current_activity)
                        print("Activity ended successfully!")
                        current_activity = None
                        break
                    elif key.lower() == 'c':
                        print("Activity cancelled.")
                        current_activity = None
                        break
            else:
                print("Invalid topic or activity. Make sure they are added to the valid list.")

        elif choice == "2":
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
            if topic in valid_topics and activity in valid_activities.get(topic, []):
                add_previous_activity(conn, start_time, end_time, topic, activity)
                print("Previous activity added successfully!")
            else:
                print("Invalid topic or activity. Make sure they are added to the valid list.")

        elif choice == "3":
            topic = input("Enter a valid topic: ")
            add_valid_topic(conn, topic)
            valid_topics.append(topic)
            print(f"Added topic '{topic}' to valid topics.")

        elif choice == "4":
            topic = input("Enter the topic for the activity: ")
            if topic not in valid_topics:
                print("Invalid topic. Please enter a valid topic first.")
                continue
            activity = input("Enter a valid activity for the topic: ")
            add_valid_activity(conn, activity, topic)
            valid_activities.setdefault(topic, []).append(activity)
            print(f"Added activity '{activity}' for topic '{topic}'.")

        elif choice == "5":
            print("Valid Topics and Activities:")
            for topic, activities in valid_activities.items():
                print(f"- {topic}:")
                for activity in activities:
                    print(f"  - {activity}")

        elif choice == "6":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        conn = connect_db()  # create the DB connection at the beginning
        main(conn)
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()  # ensure that the DB connection is closed at the end