import sqlite3
import random
from datetime import datetime, timedelta

# Connect to the SQLite database
conn = sqlite3.connect("activity_tracker.db")
cursor = conn.cursor()

def get_valid_topics():
    """Retrieve a list of valid topics from the database."""
    cursor.execute("SELECT topic FROM valid_topics")
    topics = cursor.fetchall()
    return [t[0] for t in topics]

def get_valid_activities(topic):
    """Retrieve a list of valid activities for a given topic."""
    cursor.execute("SELECT activity FROM valid_activities WHERE topic=?", (topic,))
    activities = cursor.fetchall()
    return [a[0] for a in activities]

def generate_random_time_range():
    """Generate a random start and end time for an activity."""
    current_time = datetime.now()
    random_offset = timedelta(days=random.randint(1, 30),  # up to 30 days before
                              minutes=random.randint(0, 24*60))  # any time of the day

    start_time = (current_time - random_offset).strftime('%Y-%m-%d %H:%M:%S')
    end_time = (datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=random.randint(15, 180))).strftime('%Y-%m-%d %H:%M:%S')  # 15 minutes to 3 hours

    return start_time, end_time

def add_activity(start_time, end_time, topic, activity):
    """Add an activity with a given start and end time to the database."""
    cursor.execute("""
    INSERT INTO activities (start_time, end_time, topic, activity) 
    VALUES (?, ?, ?, ?)
    """, (start_time, end_time, topic, activity))
    conn.commit()

def input_random_data():
    """Insert random data into the database."""
    topics = get_valid_topics()

    if not topics:
        print("No valid topics found. Please add some to continue.")
        return

    for _ in range(100):  # adding 100 random activities
        topic = random.choice(topics)
        activities = get_valid_activities(topic)

        if not activities:
            continue  # skip the topic if there are no valid activities

        activity = random.choice(activities)

        start_time, end_time = generate_random_time_range()
        add_activity(start_time, end_time, topic, activity)

    print("Random activities added successfully!")

if __name__ == "__main__":
    input_random_data()
    conn.close()
