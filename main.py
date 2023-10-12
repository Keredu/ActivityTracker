import argparse
import json
import os
from datetime import datetime

from database import ActivityDatabase


def clear_console():
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
    except Exception:
        print("Error clearing console.")


def wait_for_user(prompt="Press any key to continue..."):
    try:
        input(prompt)
    except KeyboardInterrupt:
        print("\nGoodbye!")
        exit()


def display_topics(db):
    topics = list(db.get_topics_and_subtopics().keys())
    for index, topic in enumerate(topics, 1):
        print(f"{index}. {topic}")
    return topics


def get_topic_by_number(topics):
    while True:
        try:
            topic_num = int(get_user_input("Enter the topic number: "))
            if 1 <= topic_num <= len(topics):
                return topics[topic_num - 1]
            else:
                print("❌ Invalid topic number. Please try again.")
        except ValueError:
            print("❌ Please enter a valid number.")


def display_subtopics(db, topic):
    subtopics = db.get_topics_and_subtopics().get(topic, [])
    for sub_index, subtopic in enumerate(subtopics, 1):
        print(f"  {sub_index}. {subtopic}")
    return subtopics


def get_subtopic_by_number(subtopics):
    while True:
        try:
            subtopic_num = int(get_user_input("Enter the subtopic number: "))
            if 1 <= subtopic_num <= len(subtopics):
                return subtopics[subtopic_num - 1]
            else:
                print("❌ Invalid subtopic number. Please try again.")
        except ValueError:
            print("❌ Please enter a valid number.")


def validate_topic_and_subtopic(db, topic, subtopic):
    topics_and_subtopics = db.get_topics_and_subtopics()
    topic_ok = topic in topics_and_subtopics.keys()
    subtopic_ok = subtopic in topics_and_subtopics.get(topic, [])
    return topic_ok and subtopic_ok


def get_user_input(prompt, validation_func=None):
    while True:
        user_input = input(prompt)
        if validation_func and not validation_func(user_input):
            print("❌ Invalid input. Please try again.")
        else:
            return user_input


def start_new_activity(db):
    print("Select a topic:")
    topics = display_topics(db)
    topic  = get_topic_by_number(topics)
    print(f"Selected topic: {topic}")

    print("Select a subtopic:")
    subtopics = display_subtopics(db, topic)
    subtopic  = get_subtopic_by_number(subtopics)
    print(f"Selected subtopic: {subtopic}")

    start_time = datetime.now().strftime(db.DATE_FORMAT)
    print(f"Activity on '{topic} -> {subtopic}' started at {start_time}.")

    while True:
        key = get_user_input("➤ Press 'e' to end or 'c' to cancel the activity: ")
        if key.lower() == 'e':
            end_time = datetime.now().strftime(db.DATE_FORMAT)
            db.insert_activity(start_time=start_time,
                            end_time=end_time,
                            topic=topic,
                            subtopic=subtopic)
            print("Activity ended successfully!")
            break
        elif key.lower() == 'c':
            print("Activity cancelled.")
            break
        else:
            print(f"❌ Invalid input '{key}'. Try again.")
    print(80 * "=")


def add_previous_activity(db):
    print("Select a topic:")
    topics = display_topics(db)
    topic  = get_topic_by_number(topics)
    print(f"Selected topic: {topic}")

    print("Select a subtopic:")
    subtopics = display_subtopics(db, topic)
    subtopic  = get_subtopic_by_number(subtopics)
    print(f"Selected subtopic: {subtopic}")

    st_msg = "Enter the start time (YYYY-MM-DD HH:MM:SS): "
    et_msg = "Enter the end time (YYYY-MM-DD HH:MM:SS): "
    start_time = get_user_input(st_msg, db.validate_datetime_format)
    end_time   = get_user_input(et_msg, db.validate_datetime_format)
    while start_time > end_time:
        print("❌ End time should be later than the start time.")
        start_time = get_user_input(st_msg, db.validate_datetime_format)
        end_time   = get_user_input(et_msg, db.validate_datetime_format)
    
    try:
        db.insert_activity(start_time=start_time,
                            end_time=end_time,
                            topic=topic,
                            subtopic=subtopic)
        print("Previous activity added successfully!")
        print(80 * "=")
    except Exception as e:
        print(f"An error occurred while inserting previous activity: {e}")


def list_valid_topics_and_subtopics(db):
    print("Valid Topics and Subtopics:")
    topics_and_subtopics = db.get_topics_and_subtopics()
    
    for index, (topic, subtopics) in enumerate(topics_and_subtopics.items(), 1):
        print(f"{index}. {topic}:")
        for sub_index, subtopic in enumerate(subtopics, 1):
            print(f"  {sub_index}. {subtopic}")
    wait_for_user()
    clear_console()


def main(db):
    menu_options = {
        "1": ("Start new activity", start_new_activity, ),
        "2": ("Add a previous activity", add_previous_activity),
        "3": ("List valid topics and subtopics", list_valid_topics_and_subtopics),
        "4": ("Quit", None)
    }

    text = None
    while text != 'Quit':

        # Print menu options
        print("Activity Tracker:")
        for key, (text, _) in menu_options.items():
            print(f"{key}. {text}")

        # Get user input
        choice = get_user_input("➤ Enter your choice: ", lambda x: x in menu_options.keys())
        text, action = menu_options[choice]

        # Execute action
        if action:
            action(db)


if __name__ == "__main__":
    CONFIG_KEYS = ['database_name', 'topics_and_subtopics']
    parser = argparse.ArgumentParser(description='Activity Tracker')
    parser.add_argument('--conf', required=True, help='Path to the configuration file')
    args = parser.parse_args()

    config_path = args.conf

    db = None
    try:
        with open(config_path, "r") as file:
            config = json.load(file)

        for key in CONFIG_KEYS:
            if key not in config:
                raise KeyError(f"Key '{key}' not found.")

        db = ActivityDatabase(database_name=config['database_name'])

        config_topics_and_subtopics = config['topics_and_subtopics']

        db.initialize_topics_and_subtopics(config_topics_and_subtopics)

        main(db)

    except FileNotFoundError:
        print(f"Config file '{config_path}' not found.")

    except json.JSONDecodeError:
        print("Error decoding JSON config file.")

    except KeyError as e:
        print(f"Configuration error: {e}")

    except KeyboardInterrupt:
        print("\nGoodbye!")

    except Exception as e:
        print(f"An error occurred: {e}")

    else:
        print("Goodbye!")

    finally:
        if db:
            db.close()
