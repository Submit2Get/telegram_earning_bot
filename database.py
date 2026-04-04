import sqlite3
import time

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

# USERS
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    referrer INTEGER,
    balance REAL DEFAULT 0,
    last_bonus INTEGER DEFAULT 0
)
""")

# TASK SUBMIT
cursor.execute("""
CREATE TABLE IF NOT EXISTS submissions (
    user_id INTEGER,
    task_id TEXT,
    file_id TEXT,
    status TEXT
)
""")

# WITHDRAW
cursor.execute("""
CREATE TABLE IF NOT EXISTS withdraws (
    user_id INTEGER,
    amount REAL,
    upi TEXT,
    status TEXT
)
""")

conn.commit()

# ===== USER =====
def add_user(user_id, referrer=None):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (user_id, referrer) VALUES (?,?)", (user_id, referrer))
        conn.commit()

        if referrer and referrer != user_id:
            cursor.execute("UPDATE users SET balance=balance+1 WHERE user_id=?", (referrer,))
            conn.commit()

def get_balance(user_id):
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    r = cursor.fetchone()
    return r[0] if r else 0

def add_balance(user_id, amount):
    cursor.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (amount, user_id))
    conn.commit()

# ===== BONUS =====
def get_last_bonus(user_id):
    cursor.execute("SELECT last_bonus FROM users WHERE user_id=?", (user_id,))
    r = cursor.fetchone()
    return r[0] if r else 0

def update_bonus(user_id):
    cursor.execute("UPDATE users SET last_bonus=? WHERE user_id=?", (int(time.time()), user_id))
    conn.commit()

# ===== TASK =====
def submit_task(user_id, task_id, file_id):
    cursor.execute("INSERT INTO submissions VALUES (?,?,?,?)", (user_id, task_id, file_id, "pending"))
    conn.commit()

def get_pending_tasks():
    cursor.execute("SELECT * FROM submissions WHERE status='pending'")
    return cursor.fetchall()

def approve_task(user_id, task_id, reward):
    cursor.execute("UPDATE submissions SET status='approved' WHERE user_id=? AND task_id=?", (user_id, task_id))
    cursor.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (reward, user_id))
    conn.commit()

def reject_task(user_id, task_id):
    cursor.execute("UPDATE submissions SET status='rejected' WHERE user_id=? AND task_id=?", (user_id, task_id))
    conn.commit()

# ===== WITHDRAW =====
def create_withdraw(user_id, amount, upi):
    cursor.execute("INSERT INTO withdraws VALUES (?,?,?,?)", (user_id, amount, upi, "pending"))
    conn.commit()

def get_withdraws():
    cursor.execute("SELECT * FROM withdraws WHERE status='pending'")
    return cursor.fetchall()

def approve_withdraw(user_id):
    cursor.execute("UPDATE withdraws SET status='approved' WHERE user_id=?", (user_id,))
    cursor.execute("UPDATE users SET balance=0 WHERE user_id=?", (user_id,))
    conn.commit()

def reject_withdraw(user_id):
    cursor.execute("UPDATE withdraws SET status='rejected' WHERE user_id=?", (user_id,))
    conn.commit()