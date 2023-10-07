import sqlite3
from datetime import datetime

# Connect to SQLite database
conn = sqlite3.connect("activity_tracker.db")
cursor = conn.cursor()

def calculate_time_spent_for_topic():
    cursor.execute("""
        SELECT topic, SUM(CAST((julianday(end_time) - julianday(start_time)) * 24 * 60 * 60 AS INTEGER))
        FROM activities
        WHERE end_time IS NOT NULL
        GROUP BY topic
    """)
    return cursor.fetchall()

def calculate_time_spent_for_activity(topic):
    cursor.execute("""
        SELECT activity, SUM(CAST((julianday(end_time) - julianday(start_time)) * 24 * 60 * 60 AS INTEGER))
        FROM activities
        WHERE topic = ? AND end_time IS NOT NULL
        GROUP BY activity
    """, (topic,))
    return cursor.fetchall()

def format_seconds_as_dhms(seconds):
    days = seconds // 86400
    seconds %= 86400
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return f"{days}d {hours}h {minutes}m {seconds}s"

def display_report():
    print("Time Spent per Topic:")
    print("---------------------")
    for topic, time in calculate_time_spent_for_topic():
        formatted_time = format_seconds_as_dhms(time)
        print(f"{topic}: {formatted_time}")

        print(f"\nTime Spent in '{topic}' per Activity:")
        print("--------------------------------------")
        for activity, time in calculate_time_spent_for_activity(topic):
            formatted_time = format_seconds_as_dhms(time)
            print(f"{activity}: {formatted_time}")
        print()

if __name__ == "__main__":
    display_report()

# Close the connection when done
conn.close()
