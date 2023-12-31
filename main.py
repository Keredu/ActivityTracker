import argparse
import json
import os
import select
import sys
import time
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


def pomodoro_timer_with_input(minutes, valid_inputs=['c', 'e']):
    """Timer that waits for a specified amount of minutes and checks for user input."""
    end_time = time.time() + minutes * 60

    while time.time() < end_time:
        try:
            time.sleep(1)
            # For UNIX, Linux, etc.
            i, o, e = select.select([sys.stdin], [], [], 0.0001)
            if i:
                user_input = sys.stdin.readline().strip()
                if user_input in valid_inputs:
                    return user_input
        except KeyboardInterrupt:
            pass
    return None


def start_pomodoro(db, pomodoro_time, short_break, long_break, max_pomodoros):
    pomodoros_done = 0

    print("Select a topic:")
    topics = display_topics(db)
    topic = get_topic_by_number(topics)
    print(f"Selected topic: {topic}")

    print("Select a subtopic:")
    subtopics = display_subtopics(db, topic)
    subtopic = get_subtopic_by_number(subtopics)
    print(f"Selected subtopic: {subtopic}")

    while True:
        clear_console()
        print(f"\nStarting Pomodoro #{pomodoros_done + 1} on '{topic} -> {subtopic}'.")
        print("Press 'e' to end and save the Pomodoro. Press 'c' to cancel the Pomodoro.")
        start_time = datetime.now().strftime(db.DATE_FORMAT)
        user_choice = pomodoro_timer_with_input(pomodoro_time)
        
        if user_choice == 'c':
            print("Pomodoro cancelled.")
            msg = "Would you like to start another Pomodoro (p) or return to the menu (m)? [p/m]: "
            decision = get_user_input(msg, lambda x: x in ['p', 'm'])
            if decision == 'p':
                continue
            else:
                break
        elif user_choice == 'e' or user_choice is None:
            end_time = datetime.now().strftime(db.DATE_FORMAT)
            db.insert_activity(start_time=start_time,
                               end_time=end_time,
                               topic=topic,
                               subtopic=subtopic)
            print("Pomodoro ended successfully!")
        
        pomodoros_done += 1

        if pomodoros_done == max_pomodoros:
            print(f"You've completed {max_pomodoros} Pomodoros!")
            
            decision = get_user_input("Would you like to take a long break (l) or return to the menu (m)? [l/m]: ", lambda x: x in ['l', 'm'])
            if decision == 'l':
                print(f"\nStarting a {long_break}-minute break. Press 'c' to cancel.")
                if pomodoro_timer_with_input(long_break, ['c']) == 'c':
                    print("Break cancelled.")
                # After the long break, ask the user if they want to start another round of pomodoros or return to the menu.
                decision_after_break = get_user_input("Would you like to start another round of Pomodoros (r) or return to the menu (m)? [r/m]: ", lambda x: x in ['r', 'm'])
                if decision_after_break == 'r':
                    pomodoros_done = 0  # reset pomodoro count and continue with the while loop
                    continue
                else:
                    break  # return to main menu
            else:
                break  # return to main menu
        else:
            msg  = "Would you like to take a short break (s), "
            msg += "start another Pomodoro (p), or return to the menu (m)? [s/p/m]: "
            decision = get_user_input(msg, lambda x: x in ['s', 'p', 'm'])
            if decision == 's':
                print(f"\nStarting a {short_break}-minute break. Press 'c' to cancel.")
                if pomodoro_timer_with_input(short_break, ['c']) == 'c':
                    print("Break cancelled.")
            elif decision == 'p':
                continue
            else:
                break



def main(db, pomodoro_config):
    menu_options = {
        "1": ("Start new activity", start_new_activity),
        "2": ("Add a previous activity", add_previous_activity),
        "3": ("List valid topics and subtopics", list_valid_topics_and_subtopics),
        "4": ("Start a Pomodoro", lambda db: start_pomodoro(db, **pomodoro_config)),
        "5": ("Quit", None)
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
    CONFIG_KEYS = ['database_name', 'topics_and_subtopics', 'pomodoro']
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

        main(db, pomodoro_config=config['pomodoro'])

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
