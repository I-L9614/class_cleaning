import sqlite3

# שם קובץ מסד הנתונים
DB_FILE = "class_cleaning.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # ---------------------------
    # טבלת מנהלים
    # ---------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    """)

    # ---------------------------
    # טבלת כיתות
    # ---------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)

    # ---------------------------
    # טבלת תלמידים
    # ---------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        class_id INTEGER,
        FOREIGN KEY(class_id) REFERENCES classes(id)
    )
    """)

    # ---------------------------
    # טבלת הגרלות / תורנויות
    # ---------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        week TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # ---------------------------
    # טבלת הגדרות מערכת
    # ---------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
