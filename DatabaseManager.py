import os
import sqlite3
import bcrypt
from cryptography.fernet import Fernet, InvalidToken

def load_or_create_key():
    """Loads an existing encryption key or creates a new one if it doesn't exist."""
    key_file = "db_key.key"
    if os.path.exists(key_file):
        with open(key_file, "rb") as file:
            return file.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, "wb") as file:
            file.write(key)
        return key


class DatabaseManager:
    """Handles database operations with file-level encryption."""

    def __init__(self, db_name="user_identification.db"):
        self.db_name = db_name
        self.key = load_or_create_key()
        self.cipher_suite = Fernet(self.key)

        if not os.path.exists(self.db_name):
            self.init_db()

    def encrypt_file(self):
        """Encrypts the database file if it is not already encrypted."""
        if os.path.exists(self.db_name):
            with open(self.db_name, "rb") as file:
                file_data = file.read()

            if file_data.startswith(b'SQLite format 3'):
                encrypted_data = self.cipher_suite.encrypt(file_data)
                with open(self.db_name, "wb") as file:
                    file.write(encrypted_data)

    def decrypt_file(self):
        """Decrypts the database file if it is encrypted."""
        if not os.path.exists(self.db_name):
            return

        with open(self.db_name, "rb") as file:
            encrypted_data = file.read()

        if encrypted_data.startswith(b'SQLite format 3'):
            return

        try:
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            with open(self.db_name, "wb") as file:
                file.write(decrypted_data)
        except InvalidToken:
            raise

    def connect(self):
        """Establishes a connection to the database after decryption."""
        self.decrypt_file()
        conn = sqlite3.connect(self.db_name)
        return conn

    def init_db(self):
        """Initializes the database by creating the users table if it doesn't exist."""
        conn = self.connect()
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
        self.encrypt_file()

    def hash_password(self, password):
        """Hashes a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    def verify_password(self, stored_password, provided_password):
        """Verifies the provided password against the stored hash."""
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))

    def user_exists(self, name):
        """Checks if a user with the specified name exists in the database."""
        self.decrypt_file()
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT password, feature_vector FROM users WHERE name = ?", (name,))
        result = cursor.fetchone()
        conn.close()
        self.encrypt_file()
        return result

    def register_user(self, name, password, feature_vector, overwrite=False):
        """Registers a new user or updates an existing one.

        Args:
            name (str): The user's name.
            password (str): The user's password.
            feature_vector (list/str): The user's facial feature vector.
            overwrite (bool): If True, updates the existing user's record.

        Returns:
            bool: True if registration was successful, False otherwise.
        """
        if isinstance(feature_vector, list):
            feature_vector = ','.join(map(str, feature_vector))

        hashed_password = self.hash_password(password)

        try:
            self.decrypt_file()

            conn = self.connect()
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

            self.encrypt_file()
            return True

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

        except Exception as e:
            print(f"Error: {e}")
            return False

    def get_all_users(self):
        """Retrieves all users from the database."""
        self.decrypt_file()
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, feature_vector FROM users")
        users = cursor.fetchall()
        conn.close()
        self.encrypt_file()
        return users
