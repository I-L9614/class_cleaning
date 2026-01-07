import sqlite3

DB_FILE = "cleaning.db"

def get_db():
    conn = sqlite3.connect(DB_FILE)
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            week TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS availability (
            user_id INTEGER,
            week TEXT,
            available INTEGER,
            PRIMARY KEY (user_id, week),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

def save_schedule(schedule):
    conn = get_db()
    cursor = conn.cursor()
    for week, names in schedule.items():
        for name in names:
            cursor.execute("SELECT id FROM users WHERE name=?", (name,))
            user = cursor.fetchone()
            if user:
                user_id = user[0]
                cursor.execute("INSERT INTO assignments (user_id, week) VALUES (?, ?)", (user_id, week))
    conn.commit()
    conn.close()
