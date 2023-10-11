import random
import json
from datetime import datetime, timedelta
from database import ActivityDatabase  # Import the ActivityDatabase class

def generate_random_time_range():
    """Generate a random start and end time for an activity."""
    current_time = datetime.now()
    random_offset = timedelta(days=random.randint(1, 30),  # up to 30 days before
                              minutes=random.randint(0, 24*60))  # any time of the day

    start_time = (current_time - random_offset).strftime('%Y-%m-%d %H:%M:%S')
    end_time = (datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=random.randint(15, 180))).strftime('%Y-%m-%d %H:%M:%S')  # 15 minutes to 3 hours

    return start_time, end_time

def input_random_data(db):
    """Insert random data into the database."""
    topics = db.list_valid_topics()

    if not topics:
        print("No valid topics found. Please add some to continue.")
        return

    for _ in range(100):  # adding 100 random activities
        topic = random.choice(topics)
        activities = db.list_valid_activities(topic)

        if not activities:
            continue  # skip the topic if there are no valid activities

        activity = random.choice(activities)

        start_time, end_time = generate_random_time_range()
        db.add_previous_activity(start_time, end_time, topic, activity)

    print("Random activities added successfully!")


if __name__ == "__main__":
    # Load the configuration from test_config.json
    with open("test_config.json", "r") as file:
        config = json.load(file)
    database_name = config['database_name']
    
    valid_config_topics = set(config['valid_topics_and_activities'].keys())
    valid_config_activities = config['valid_topics_and_activities']
    
    # Create an instance of ActivityDatabase
    db = ActivityDatabase(config['database_name'])

    # Initialize valid topics and activities from config
    db.initialize_valid_topics_and_activities(valid_config_topics, valid_config_activities)

    input_random_data(db)
    db.close()  # Close the database connection using the close method of ActivityDatabase
