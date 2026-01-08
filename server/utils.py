from server.models import Students, Classes

import random

def run_lottery(class_id):
    students = list(Students.find({"class_id": class_id}))
    # גרילת 4-5 תורנים לכל שבוע
    total_students = len(students)
    weeks = 4  # או חישוב לפי שבועות
    lottery_results = {}
    for week in range(1, weeks+1):
        lottery_results[f"week_{week}"] = random.sample(students, min(5, total_students))
    # שמירה או שליחת מיילים מתבצע ב-worker.py
    return lottery_results

from werkzeug.security import generate_password_hash, check_password_hash
def hash_password(password):
    return generate_password_hash(password)

def verify_password(password, hashed):
    return check_password_hash(hashed, password)
