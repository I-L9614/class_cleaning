from flask import request, redirect, flash
from database import get_db

def add_class(name):
    db = get_db()
    try:
        db.execute("INSERT INTO classes (name) VALUES (?)", (name,))
        db.commit()
    except:
        flash("כיתה כבר קיימת")
    finally:
        db.close()

def delete_class(class_id):
    db = get_db()
    db.execute("DELETE FROM classes WHERE id=?", (class_id,))
    db.execute("DELETE FROM students WHERE class_id=?", (class_id,))
    db.commit()
    db.close()
