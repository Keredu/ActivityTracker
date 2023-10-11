import sqlite3
import datetime


class ActivityDatabase:
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, database_name):
        self.conn = sqlite3.connect(database_name)
        self.create_tables()

    def create_tables(self):
        commands = [
            """
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY,
                start_time DATETIME,
                end_time DATETIME,
                topic TEXT,
                activity TEXT,
                FOREIGN KEY(topic) REFERENCES valid_topics(topic),
                FOREIGN KEY(activity) REFERENCES valid_activities(activity)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS valid_topics (
                topic TEXT PRIMARY KEY
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS valid_activities (
                activity TEXT,
                topic TEXT,
                FOREIGN KEY(topic) REFERENCES valid_topics(topic)
            )
            """
        ]
        with self.conn:
            cursor = self.conn.cursor()
            for command in commands:
                cursor.execute(command)

    def add_valid_topic(self, topic, exists_ok=False):
        cursor = self.conn.cursor()
        cursor.execute("SELECT topic FROM valid_topics WHERE topic=?", (topic,))
        existing_topic = cursor.fetchone()
        if existing_topic is None:
            with self.conn:
                self.conn.execute("INSERT INTO valid_topics (topic) VALUES (?)", (topic,))
        elif not exists_ok:
            print(f"Warning: Topic '{topic}' already exists.")

    def add_valid_activity(self, activity, topic, exists_ok=False):
        cursor = self.conn.cursor()
        cursor.execute("SELECT activity FROM valid_activities WHERE activity=? AND topic=?", (activity, topic))
        existing_activity = cursor.fetchone()
        if existing_activity is None:
            with self.conn:
                self.conn.execute("INSERT INTO valid_activities (activity, topic) VALUES (?, ?)", (activity, topic))
        elif not exists_ok:
            print(f"Warning: Activity '{activity}' under topic '{topic}' already exists.")


    def list_valid_topics(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT topic FROM valid_topics")
        topics = cursor.fetchall()
        return [t[0] for t in topics]

    def list_valid_activities(self, topic):
        cursor = self.conn.cursor()
        cursor.execute("SELECT activity FROM valid_activities WHERE topic=?", (topic,))
        activities = cursor.fetchall()
        return [a[0] for a in activities]

    def add_previous_activity(self, start_time, end_time, topic, activity):
        with self.conn:
            self.conn.execute("""
            INSERT INTO activities (start_time, end_time, topic, activity) 
            VALUES (?, ?, ?, ?)
            """, (start_time, end_time, topic, activity))

    def store_activity(self, start_time, topic, activity):
        end_time = datetime.now().strftime(self.DATE_FORMAT)
        with self.conn:
            self.conn.execute("""
            INSERT INTO activities (start_time, end_time, topic, activity) 
            VALUES (?, ?, ?, ?)
            """, (start_time, end_time, topic, activity))

    def initialize_valid_topics_and_activities(self, valid_config_topics, valid_config_activities):
        for topic in valid_config_topics:
            self.add_valid_topic(topic, exists_ok=True)
        for topic, activities in valid_config_activities.items():
            for activity in activities:
                self.add_valid_activity(activity, topic, exists_ok=True)


    def close(self):
        self.conn.close()
