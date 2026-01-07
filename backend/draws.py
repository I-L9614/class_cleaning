from database import get_db
from datetime import datetime, timedelta
import random

def create_draw(class_id, start_date, end_date):
    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO draws (class_id, start_date, end_date) VALUES (?, ?, ?)",
                (class_id, start_date, end_date))
    draw_id = cur.lastrowid

    # מחלקים שבועות בין תלמידים
    cur.execute("SELECT id FROM students WHERE class_id=?", (class_id,))
    students = [row["id"] for row in cur.fetchall()]

    weeks = []
    s = datetime.strptime(start_date, "%Y-%m-%d")
    e = datetime.strptime(end_date, "%Y-%m-%d")
    while s <= e:
        weeks.append(s.strftime("%Y-%m-%d"))
        s += timedelta(days=7)

    student_index = 0
    for week in weeks:
        count = random.randint(4,5)
        for _ in range(count):
            if student_index >= len(students):
                student_index = 0
                random.shuffle(students)
            student_id = students[student_index]
            cur.execute("INSERT INTO assignments (draw_id, student_id, week_start) VALUES (?, ?, ?)",
                        (draw_id, student_id, week))
            student_index += 1

    db.commit()
    db.close()
