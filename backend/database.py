import sqlite3
import os

DB_PATH = "cleaning.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # טבלת כיתות
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        created_by INTEGER
    )
    """)

    # טבלת משתמשים
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        class_id INTEGER,
        is_admin INTEGER DEFAULT 0
    )
    """)

    # טבלת לוח תורנים
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        week TEXT NOT NULL,
        user_id INTEGER,
        class_id INTEGER
    )
    """)

    # טבלת זמינות
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS availability (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        week TEXT,
        available INTEGER DEFAULT 1
    )
    """)

    conn.commit()
    conn.close()

def save_schedule(schedule, class_id):
    conn = get_db()
    cursor = conn.cursor()
    for week, names in schedule.items():
        for name in names:
            cursor.execute("SELECT id FROM users WHERE name=? AND class_id=?", (name, class_id))
            user = cursor.fetchone()
            if user:
                user_id = user[0]
                cursor.execute("INSERT INTO assignments (week, user_id, class_id) VALUES (?, ?, ?)", (week, user_id, class_id))
    conn.commit()
    conn.close()
