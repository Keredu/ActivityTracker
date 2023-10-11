import argparse  # Import argparse module
import json
from datetime import datetime
from database import ActivityDatabase  # Import the ActivityDatabase class

def validate_datetime_format(dt_str):
    """Validate if the given string matches the datetime format."""
    try:
        datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        return True
    except ValueError:
        return False

def validate_end_time(start_time, end_time):
    """Validate if the end time is later than the start time."""
    start = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    return end > start

def get_user_input(prompt, validation_func=None):
    """Get user input and validate it if a validation function is provided."""
    while True:
        user_input = input(prompt)
        if validation_func and not validation_func(user_input):
            print("Invalid input. Please try again.")
        else:
            return user_input

def start_activity(topic, activity):
    """Start a new activity and return the start time."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S'), topic, activity



def main(db):
    """Main function for the Activity Tracker."""
    current_activity = None
    valid_topics = db.list_valid_topics()
    valid_activities = {topic: db.list_valid_activities(topic) for topic in valid_topics}

    while True:
        print("\nActivity Tracker:")
        print("1. Start new activity")
        print("2. Add a previous activity")
        print("3. Add a valid topic")
        print("4. Add a valid activity to a topic")
        print("5. List valid topics and activities")
        print("6. Quit")
        choice = get_user_input("Enter your choice: ", lambda x: x in "123456")

        if choice == "1":
            topic = get_user_input("Enter the topic (e.g., work, projects): ")
            activity = get_user_input("Enter the activity: ")
            if topic in valid_topics and activity in valid_activities.get(topic, []):
                if current_activity:
                    print("There's an ongoing activity. Please end or cancel it first.")
                    continue
                current_activity = start_activity(topic, activity)
                print(f"Started activity '{activity}'.")
                print("Press 'e' and Enter to end the activity. Press 'c' and Enter to cancel the activity.")

                while True:
                    key = get_user_input("Press 'e' and Enter to end the activity. Press 'c' and Enter to cancel the activity: ")
                    if key.lower() == 'e':
                        db.store_activity(*current_activity)
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
            start_time = get_user_input("Enter the start time (YYYY-MM-DD HH:MM:SS): ", validate_datetime_format)
            end_time = get_user_input("Enter the end time (YYYY-MM-DD HH:MM:SS): ", validate_datetime_format)

            if not validate_end_time(start_time, end_time):
                print("End time should be later than the start time.")
                continue
            topic = get_user_input("Enter the topic (e.g., work, personal-projects): ")
            activity = get_user_input("Describe the activity: ")
            if topic in valid_topics and activity in valid_activities.get(topic, []):
                db.add_previous_activity(start_time, end_time, topic, activity)
                print("Previous activity added successfully!")
            else:
                print("Invalid topic or activity. Make sure they are added to the valid list.")

        elif choice == "3":
            topic = get_user_input("Enter a valid topic: ")
            db.add_valid_topic(topic)
            valid_topics.append(topic)
            print(f"Added topic '{topic}' to valid topics.")

        elif choice == "4":
            topic = get_user_input("Enter the topic for the activity: ")
            if topic not in valid_topics:
                print("Invalid topic. Please enter a valid topic first.")
                continue
            activity = get_user_input("Enter a valid activity for the topic: ")
            db.add_valid_activity(activity, topic)
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
    parser = argparse.ArgumentParser(description='Activity Tracker')  # Create argument parser
    parser.add_argument('--conf', default='test_config.json', help='Path to the configuration file')  # Add argument for configuration file path
    args = parser.parse_args()  # Parse the arguments

    config_path = args.conf  # Get the configuration file path from arguments
    
    # Load the configuration
    with open(config_path, "r") as file:  # Use config_path instead of hardcoded 'config.json'
        config = json.load(file)
    db = None
    try:
        database_name = config['database_name']
        db = ActivityDatabase(database_name)  # Create an instance of ActivityDatabase
        
        valid_config_topics = set(config['valid_topics_and_activities'].keys())
        valid_config_activities = config['valid_topics_and_activities']
        
        db.initialize_valid_topics_and_activities(valid_config_topics, valid_config_activities)
        
        main(db)
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if db:
            db.close()  # Close the database connection using the close method of ActivityDatabase

       
