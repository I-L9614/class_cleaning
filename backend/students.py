from flask import request, render_template, redirect, flash
from database import get_db

def register_student():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        class_id = request.form["class_id"]

        db = get_db()
        cur = db.cursor()
        # בדיקה אם התלמיד כבר קיים
        cur.execute("SELECT * FROM students WHERE email=?", (email,))
        exists = cur.fetchone()
        if exists:
            flash("אתה כבר רשום")
            return redirect("/register")

        # הכנסת תלמיד חדש
        cur.execute("INSERT INTO students (name, email, class_id) VALUES (?, ?, ?)",
                    (name, email, class_id))
        db.commit()
        db.close()
        return render_template("success.html", name=name)
    else:
        # קבלת רשימת כיתות
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM classes WHERE is_active=1")
        classes = cur.fetchall()
        db.close()
        return render_template("register.html", classes=classes)
