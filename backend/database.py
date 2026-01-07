import sqlite3

def get_db():
    return sqlite3.connect("cleaning.db")

def init_db():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assignments (
        week TEXT,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS availability (
        user_id INTEGER,
        week TEXT,
        available INTEGER DEFAULT 1,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    db.commit()
    db.close()

def save_schedule(schedule, db=None):
    if not db:
        db = get_db()
    cursor = db.cursor()
    for week, users in schedule.items():
        for user_name in users:
            cursor.execute("SELECT id FROM users WHERE name=?", (user_name,))
            user = cursor.fetchone()
            if not user:
                cursor.execute("INSERT INTO users (name) VALUES (?)", (user_name,))
                user_id = cursor.lastrowid
            else:
                user_id = user[0]
            cursor.execute("INSERT INTO assignments (week, user_id) VALUES (?, ?)", (week, user_id))
    db.commit()
    db.close()
