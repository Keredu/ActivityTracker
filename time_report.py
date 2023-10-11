import sqlite3
from datetime import datetime

# Create an instance of ActivityDatabase
conn = sqlite3.connect("test.db")
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

def format_seconds_as_hms(seconds):
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return f"{hours}h {minutes}m {seconds}s"

def display_report():
    for topic, time in calculate_time_spent_for_topic():
        formatted_time = format_seconds_as_hms(time)
        print(f"- {topic}: {formatted_time}")
        for activity, time in calculate_time_spent_for_activity(topic):
            formatted_time = format_seconds_as_hms(time)
            print(f"    - {activity}: {formatted_time}")
        print("==========================")

if __name__ == "__main__":
    display_report()

# Close the connection when done
conn.close()
