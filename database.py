import sqlite3
from datetime import datetime


class ActivityDatabase:
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, database_name):
        self.database_name = database_name
        self.conn = sqlite3.connect(database_name)
        self.create_tables()

    @staticmethod
    def validate_datetime_format(dt_str):
        """Validates if the given string is in the correct datetime format."""
        try:
            datetime.strptime(dt_str, ActivityDatabase.DATE_FORMAT)
            return True
        except ValueError:
            return False

    def create_tables(self):
        with self.conn:
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS topics_and_subtopics (
                id INTEGER PRIMARY KEY,
                topic TEXT NOT NULL,
                subtopic TEXT DEFAULT "",
                UNIQUE(topic, subtopic)
            )
            """)

            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY,
                start_time DATETIME,
                end_time DATETIME,
                topic_subtopic_id INTEGER,
                FOREIGN KEY(topic_subtopic_id) REFERENCES topics_and_subtopics(id)
            )
            """)

    def add_topic_or_subtopic(self, topic, subtopic="", exists_ok=False):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM topics_and_subtopics WHERE topic=? AND subtopic=?", (topic, subtopic))
        existing_entry = cursor.fetchone()
        if existing_entry is None:
            with self.conn:
                self.conn.execute("INSERT INTO topics_and_subtopics (topic, subtopic) VALUES (?, ?)", (topic, subtopic))
        elif not exists_ok:
            raise ValueError(f"Entry with topic '{topic}' and subtopic '{subtopic}' already exists.")

    def get_topics(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT topic FROM topics_and_subtopics")
        return [row[0] for row in cursor.fetchall()]

    def get_subtopics(self, topic):
        cursor = self.conn.cursor()
        cursor.execute("SELECT subtopic FROM topics_and_subtopics WHERE topic=?", (
        topic,))
        return [row[0] for row in cursor.fetchall()]

    def get_topics_and_subtopics(self):
        topics = self.get_topics()
        topics_and_subtopics = {}
        for topic in topics:
            subtopics = self.get_subtopics(topic)
            topics_and_subtopics[topic] = subtopics
        return topics_and_subtopics

    def insert_activity(self, start_time, end_time, topic, subtopic):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM topics_and_subtopics WHERE topic=? AND subtopic=?", (topic, subtopic))
        topic_subtopic_id = cursor.fetchone()
        if topic_subtopic_id:
            with self.conn:
                self.conn.execute("INSERT INTO activities (start_time, end_time, topic_subtopic_id) VALUES (?, ?, ?)",
                                  (start_time, end_time, topic_subtopic_id[0]))
        else:
            raise ValueError(f"Invalid topic '{topic}' or subtopic '{subtopic}'.")

    def initialize_topics_and_subtopics(self, topics_and_subtopics):
        for topic, subtopics in topics_and_subtopics.items():
            self.add_topic_or_subtopic(topic, exists_ok=True)
            for subtopic in subtopics:
                self.add_topic_or_subtopic(topic, subtopic, exists_ok=True)

    def close(self):
        if self.conn:
            self.conn.close()

