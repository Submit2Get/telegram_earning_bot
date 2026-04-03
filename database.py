import sqlite3
import time

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    referrer INTEGER,
    balance REAL DEFAULT 0,
    last_bonus INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS withdraws (
    user_id INTEGER,
    amount REAL,
    status TEXT
)
""")

conn.commit()


def add_user(user_id, referrer=None):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (user_id, referrer) VALUES (?, ?)", (user_id, referrer))
        conn.commit()

        if referrer and referrer != user_id:
            cursor.execute("UPDATE users SET balance = balance + 1 WHERE user_id=?", (referrer,))
            conn.commit()


def get_balance(user_id):
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0


def add_balance(user_id, amount):
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    conn.commit()


def get_last_bonus(user_id):
    cursor.execute("SELECT last_bonus FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0


def update_bonus(user_id):
    cursor.execute("UPDATE users SET last_bonus=? WHERE user_id=?", (int(time.time()), user_id))
    conn.commit()


def create_withdraw(user_id, amount):
    cursor.execute("INSERT INTO withdraws VALUES (?, ?, ?)", (user_id, amount, "pending"))
    conn.commit()


def get_all_users():
    cursor.execute("SELECT user_id FROM users")
    return cursor.fetchall()