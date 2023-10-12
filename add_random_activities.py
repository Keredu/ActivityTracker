import random
import json
from datetime import datetime, timedelta
from database import ActivityDatabase  # Import the ActivityDatabase class

def generate_random_time_range():
    """Generate a random start and end time for an activity."""
    current_time = datetime.now()
    random_offset = timedelta(days=random.randint(1, 30),  # up to 30 days before
                              minutes=random.randint(0, 24*60))  # any time of the day

    start_time = (current_time - random_offset).strftime(ActivityDatabase.DATE_FORMAT)
    end_time = (datetime.strptime(start_time, ActivityDatabase.DATE_FORMAT) + timedelta(minutes=random.randint(15, 180))).strftime(ActivityDatabase.DATE_FORMAT)  # 15 minutes to 3 hours

    return start_time, end_time

def input_random_data(db):
    """Insert random data into the database."""
    topics = db.get_topics()

    if not topics:
        print("No valid topics found. Please add some to continue.")
        return

    for _ in range(100):  # adding 100 random activities
        topic = random.choice(topics)
        subtopics = db.get_subtopics(topic)

        if not subtopics:
            continue  # skip the topic if there are no valid subtopics

        subtopic = random.choice(subtopics)

        start_time, end_time = generate_random_time_range()
        try:
            db.insert_activity(start_time, end_time, topic, subtopic)
        except Exception as e:
            print(f"An error occurred while inserting random activity: {e}")

    print("Random activities added successfully!")

if __name__ == "__main__":
    # Load the configuration from test_config.json
    with open("test_config.json", "r") as file:
        config = json.load(file)

    # Create an instance of ActivityDatabase
    db = ActivityDatabase(config['database_name'])
    db.initialize_topics_and_subtopics(config['topics_and_subtopics'])

    input_random_data(db)
    db.close()  # Close the database connection using the close method of ActivityDatabase
