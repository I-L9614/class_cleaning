from flask import Flask, render_template, request, jsonify
from database import get_db, save_schedule
from scheduler import generate_weeks, assign_cleaners
from notifications import send_weekly_notifications

app = Flask(__name__)

# --- Routes --- #

@app.route("/admin")
def admin_panel():
    return render_template("admin.html")

@app.route("/generate_schedule", methods=["POST"])
def generate_schedule():
    data = request.json
    class_id = data.get("class_id")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM users WHERE class_id=?", (class_id,))
    users = [row[0] for row in cursor.fetchall()]
    db.close()

    if not users:
        return jsonify({"error": "אין משתמשים בכיתה"}), 400

    weeks = generate_weeks(start_date, end_date)
    schedule = assign_cleaners(users, weeks)
    save_schedule(schedule, class_id)

    return jsonify({"message": "הגרלה נוצרה בהצלחה", "schedule": schedule})

# --- Users --- #
@app.route("/users")
def users():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name, email, class_id FROM users")
    rows = cursor.fetchall()
    db.close()
    return jsonify([{"id": r[0], "name": r[1], "email": r[2], "class_id": r[3]} for r in rows])

@app.route("/delete_user", methods=["POST"])
def delete_user():
    data = request.json
    user_id = data.get("id")
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    db.commit()
    db.close()
    return jsonify({"message": "User deleted"})

# --- Classes --- #
@app.route("/classes")
def classes():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name FROM classes")
    rows = cursor.fetchall()
    db.close()
    return jsonify([{"id": r[0], "name": r[1]} for r in rows])

@app.route("/add_class", methods=["POST"])
def add_class():
    data = request.json
    name = data.get("name")
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO classes (name) VALUES (?)", (name,))
    db.commit()
    db.close()
    return jsonify({"message": "כיתה נוספה"})

@app.route("/delete_class", methods=["POST"])
def delete_class():
    data = request.json
    class_id = data.get("id")
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM classes WHERE id=?", (class_id,))
    db.commit()
    db.close()
    return jsonify({"message": "כיתה נמחקה"})

# --- Scheduler --- #
if __name__ == "__main__":
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_weekly_notifications, 'cron', day_of_week='thu', hour=13, minute=0)
    scheduler.start()
    app.run(host="0.0.0.0", port=5000)
