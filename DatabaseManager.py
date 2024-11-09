import sqlite3


class DatabaseManager:
    '''Handles database operations for user registration and identification'''

    def __init__(self, db_name="user_identification.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        '''Initializes the database with a users table'''
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            feature_vector TEXT NOT NULL  -- Store facial ratios as a comma-separated string
        )
        """)
        conn.commit()
        conn.close()

    def register_user(self, name, surname, feature_vector):
        """Registers a new user with name, surname, and facial feature vector in the database."""
        # Ensure feature_vector is properly formatted as a comma-separated string
        if isinstance(feature_vector, list):
            feature_vector = ','.join(map(str, feature_vector))

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (name, surname, feature_vector)
                VALUES (?, ?, ?)
            """, (name, surname, feature_vector))
            conn.commit()
            conn.close()
            return "User registered successfully."
        except sqlite3.Error as e:
            return f"An error occurred: {e}"

    def get_all_users(self):
        '''Fetches all users from the database'''
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, surname, feature_vector FROM users")
        users = cursor.fetchall()
        conn.close()
        return users
