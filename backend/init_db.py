from database import get_db
import datetime

db = get_db()
cur = db.cursor()

# טבלת מנהלים
cur.execute("""
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password_hash TEXT,
    is_active INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# טבלת הזמנות מנהל
cur.execute("""
CREATE TABLE IF NOT EXISTS admin_invites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    token TEXT,
    expires_at DATETIME,
    used INTEGER DEFAULT 0
)
""")

# כיתות
cur.execute("""
CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    is_active INTEGER DEFAULT 1
)
""")

# תלמידים
cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    class_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id)
)
""")

# הגרלות
cur.execute("""
CREATE TABLE IF NOT EXISTS draws (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER,
    start_date DATE,
    end_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY (class_id) REFERENCES classes(id)
)
""")

# תורנויות
cur.execute("""
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    draw_id INTEGER,
    student_id INTEGER,
    week_start DATE,
    status TEXT DEFAULT 'active',
    FOREIGN KEY (draw_id) REFERENCES draws(id),
    FOREIGN KEY (student_id) REFERENCES students(id)
)
""")

# בקשות אי זמינות
cur.execute("""
CREATE TABLE IF NOT EXISTS unavailability_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER,
    requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    handled INTEGER DEFAULT 0,
    FOREIGN KEY (assignment_id) REFERENCES assignments(id)
)
""")

# הגדרות מערכת
cur.execute("""
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
)
""")

# הגדרה ראשונית של settings
default_settings = [
    ("system_name", "Class Cleaning"),
    ("email_sender", os.getenv("SMTP_USER", "your_email@gmail.com")),
    ("notify_day", "thu"),
    ("notify_hour", "13"),
    ("notify_minute", "0")
]

for key, value in default_settings:
    cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))

db.commit()
db.close()

print("Database initialized")
