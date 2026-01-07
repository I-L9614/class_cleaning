from flask import Flask, render_template, request, redirect, flash
from students import register_student
from auth import login_admin, invite_admin
from classes import add_class, delete_class
from draws import create_draw
from database import get_db
from scheduler import start_scheduler
from notifications import send_weekly_notifications
from datetime import datetime
from auth import login_admin, invite_admin, set_password
import random

app = Flask(__name__)
app.secret_key = "replace_with_secure_key"

# ----------------------------
# הרשמה תלמידים
# ----------------------------

app.add_url_rule("/login", view_func=login_admin, methods=["GET","POST"])
app.add_url_rule("/invite_admin", view_func=invite_admin, methods=["GET","POST"])
app.add_url_rule("/set_password", view_func=set_password, methods=["GET","POST"])


@app.route("/register", methods=["GET","POST"])
def register():
    return register_student()

# ----------------------------
# התחברות מנהלים
# ----------------------------
@app.route("/login", methods=["GET","POST"])
def login():
    return login_admin()

# ----------------------------
# ניהול כיתות (Admin)
# ----------------------------
@app.route("/admin/add_class", methods=["POST"])
def route_add_class():
    name = request.form["name"]
    add_class(name)
    flash(f"כיתה '{name}' נוספה בהצלחה")
    return redirect("/admin")

@app.route("/admin/delete_class", methods=["POST"])
def route_delete_class():
    class_id = request.form["class_id"]
    delete_class(class_id)
    flash("כיתה נמחקה בהצלחה")
    return redirect("/admin")

# ----------------------------
# יצירת הגרלה
# ----------------------------
@app.route("/admin/create_draw", methods=["POST"])
def route_create_draw():
    class_id = request.form["class_id"]
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]
    create_draw(class_id, start_date, end_date)
    flash("הגרלה נוצרה בהצלחה")
    return redirect("/admin")

# ----------------------------
# דף מנהל ראשי
# ----------------------------
@app.route("/admin")
def admin_page():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM classes WHERE is_active=1")
    classes = cur.fetchall()
    db.close()
    return render_template("admin.html", classes=classes)

# ----------------------------
# כפתור "לא יכול השבוע" – החלפת תורן
# ----------------------------
@app.route("/unavailable")
def mark_unavailable():
    name = request.args.get("name")
    week = request.args.get("week")

    db = get_db()
    cur = db.cursor()

    # מזהה התורן
    cur.execute("SELECT id, class_id FROM students WHERE name=?", (name,))
    student = cur.fetchone()
    if not student:
        flash("תורן לא נמצא")
        db.close()
        return redirect("/register")

    student_id = student["id"]
    class_id = student["class_id"]

    # מזהה משבצת שבועית
    cur.execute("SELECT id FROM assignments WHERE student_id=? AND week_start=?", (student_id, week))
    assignment = cur.fetchone()
    if not assignment:
        flash("לא נמצאה משבצת שבועית")
        db.close()
        return redirect("/register")

    assignment_id = assignment["id"]

    # מוצא מחליף זמין
    cur.execute("""
        SELECT id FROM students
        WHERE class_id=? AND id!=? AND id NOT IN (
            SELECT student_id FROM assignments WHERE week_start=?
        )
    """, (class_id, student_id, week))
    available = cur.fetchall()

    if available:
        replacement_id = random.choice([a["id"] for a in available])
        cur.execute("UPDATE assignments SET student_id=? WHERE id=?", (replacement_id, assignment_id))
        db.commit()
        flash("הוחלף תורן בהצלחה")
    else:
        flash("אין מחליפים זמינים לשבוע זה – תורן זה יועבר לשבוע הבא")

    db.close()
    return redirect("/register")

# ----------------------------
# הפעלת Scheduler והשרת
# ----------------------------
if __name__ == "__main__":
    start_scheduler()
    app.run(debug=True)
