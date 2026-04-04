import sqlite3, time

conn = sqlite3.connect("bot.db", check_same_thread=False)
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS users(user INTEGER PRIMARY KEY, points INTEGER DEFAULT 0, bonus INTEGER DEFAULT 0)")
c.execute("CREATE TABLE IF NOT EXISTS withdraw(user INTEGER, points INTEGER, method TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS activity(text TEXT)")
conn.commit()

# USERS

def add_user(u):
    c.execute("INSERT OR IGNORE INTO users(user) VALUES(?)", (u,))
    conn.commit()

def get_total_users():
    return len(c.execute("SELECT user FROM users").fetchall())

# POINTS

def get_points(u):
    r = c.execute("SELECT points FROM users WHERE user=?", (u,)).fetchone()
    return r[0] if r else 0


def add_points(u,p):
    c.execute("UPDATE users SET points=points+? WHERE user=?", (p,u))
    conn.commit()


def reset_points(u):
    c.execute("UPDATE users SET points=0 WHERE user=?", (u,))
    conn.commit()

# BONUS

def can_claim_bonus(u):
    r = c.execute("SELECT bonus FROM users WHERE user=?", (u,)).fetchone()
    return time.time() - r[0] > 86400 if r else True


def update_bonus(u):
    c.execute("UPDATE users SET bonus=? WHERE user=?", (int(time.time()),u))
    conn.commit()

# WITHDRAW

def create_withdraw(u,p,m):
    c.execute("INSERT INTO withdraw VALUES(?,?,?)", (u,p,m))
    conn.commit()

# ACTIVITY

def save_activity(t):
    c.execute("INSERT INTO activity VALUES(?)", (t,))
    conn.commit()
