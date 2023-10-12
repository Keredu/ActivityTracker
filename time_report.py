import argparse
import sqlite3


def calculate_time_spent_for_topic(cursor):
    """Calculate time spent for each topic."""
    cursor.execute(
        """
        SELECT t.topic, SUM(CAST((julianday(a.end_time) - julianday(a.start_time)) * 24 * 60 * 60 AS INTEGER))
        FROM activities a
        JOIN topics_and_subtopics t ON a.topic_subtopic_id = t.id
        WHERE a.end_time IS NOT NULL
        GROUP BY t.topic
    """
    )
    return cursor.fetchall()


def calculate_time_spent_for_activity(cursor, topic):
    """Calculate time spent for each subtopic within a topic."""
    cursor.execute(
        """
        SELECT t.subtopic, SUM(CAST((julianday(a.end_time) - julianday(a.start_time)) * 24 * 60 * 60 AS INTEGER))
        FROM activities a
        JOIN topics_and_subtopics t ON a.topic_subtopic_id = t.id
        WHERE t.topic = ? AND a.end_time IS NOT NULL
        GROUP BY t.subtopic
    """,
        (topic,),
    )
    return cursor.fetchall()


def format_seconds_as_hms(seconds):
    """Format seconds as Hours, Minutes, Seconds."""
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return f"{hours}h {minutes}m {seconds}s"


def display_report(conn):
    """Display activity report."""
    cursor = conn.cursor()
    for topic, time in calculate_time_spent_for_topic(cursor):
        formatted_time = format_seconds_as_hms(time)
        print(f"- {topic}: {formatted_time}")
        for subtopic, time in calculate_time_spent_for_activity(cursor, topic):
            formatted_time = format_seconds_as_hms(time)
            print(f"    - {subtopic}: {formatted_time}")
        print("==========================")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Display Activity Report")
    parser.add_argument("db_path", type=str, help="Path to the SQLite database")
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_arguments()
    try:
        conn = sqlite3.connect(args.db_path)
        display_report(conn=conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
