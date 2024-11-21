import sqlite3

import bcrypt


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
                        password TEXT NOT NULL,
                        feature_vector TEXT NOT NULL
                    )
                """)
        conn.commit()
        conn.close()

    def hash_password(self, password):
        '''Hashes a password using bcrypt'''
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    def verify_password(self, stored_password, provided_password):
        '''Verify if the provided password matches the stored hashed password'''
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))

    def user_exists(self, name):
        '''Check if a user with the given name exists in the database'''
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT password, feature_vector FROM users WHERE name = ?", (name,))
        result = cursor.fetchone()
        return result

    def register_user(self, name, password, feature_vector, overwrite=False):
        """Registers a new user with name, surname, and facial feature vector in the database."""
        if isinstance(feature_vector, list):
            feature_vector = ','.join(map(str, feature_vector))

        try:
            hashed_password = self.hash_password(password)
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            if overwrite:
                cursor.execute("""
                                UPDATE users SET password = ?, feature_vector = ?
                                WHERE name = ?
                            """, (hashed_password, feature_vector, name))
            else:
                cursor.execute("""
                                INSERT INTO users (name, password, feature_vector)
                                VALUES (?, ?, ?)
                            """, (name, hashed_password, feature_vector))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

    def get_all_users(self):
        '''Fetches all users from the database'''
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, surname, feature_vector FROM users")
        users = cursor.fetchall()
        conn.close()
        return users
