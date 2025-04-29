import sqlite3
from contextlib import contextmanager

DATABASE = "bot.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        # Foydalanuvchilar jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Majburiy kanallar jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mandatory_channels (
                channel_id INTEGER PRIMARY KEY,
                channel_username TEXT NOT NULL
            )
        """)
        conn.commit()

def add_user(user_id, username, first_name):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        """, (user_id, username, first_name))
        conn.commit()

def get_all_users():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        return [row[0] for row in cursor.fetchall()]

def add_mandatory_channel(channel_id, channel_username):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO mandatory_channels (channel_id, channel_username)
            VALUES (?, ?)
        """, (channel_id, channel_username))
        conn.commit()

def get_mandatory_channels():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT channel_id, channel_username FROM mandatory_channels")
        return cursor.fetchall()

def remove_mandatory_channel(channel_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM mandatory_channels WHERE channel_id = ?", (channel_id,))
        conn.commit()