from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from scheduler import generate_weeks, assign_cleaners
from database import save_schedule, get_db, init_db
from notifications import send_weekly_notifications
import os

app = Flask(__name__)
CORS(app)

if not os.path.exists("cleaning.db"):
    init_db()

@app.route("/health")
def health():
    return {"status": "ok"}

# --- הרשמה ---
@app.route("/register", methods=["GET"])
def register_form():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name FROM classes")
    classes = cursor.fetchall()
    db.close()
    return render_template("register.html", classes=classes)

@app.route("/register", methods=["POST"])
def register_user():
    name = request.form.get("name")
    email = request.form.get("email")
    class_id = request.form.get("class_id")
    if not name or not email or not class_id:
        return "<h3>חובה למלא שם, אימייל ובחירת כיתה</h3>", 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    if user:
        message = "המשתמש כבר רשום."
    else:
        cursor.execute("INSERT INTO users (name, email, class_id) VALUES (?, ?, ?)", (name, email, class_id))
        db.commit()
        message = "הרשמתך בוצעה בהצלחה!"
    db.close()
    return f"<h3>{message}</h3>"

# --- הרשמה קבועה / צפייה ביוסרס ---
@app.route("/users", methods=["GET"])
def get_users():
    class_id = request.args.get("class_id")
    db = get_db()
    cursor = db.cursor()
    if class_id:
        cursor.execute("SELECT id, name, email, class_id FROM users WHERE class_id=? ORDER BY id", (class_id,))
    else:
        cursor.execute("SELECT id, name, email, class_id FROM users ORDER BY id")
    rows = cursor.fetchall()
    db.close()
    return jsonify([{"id": uid, "name": name, "email": email, "class_id": cid} for uid, name, email, cid in rows])

# --- מחיקת משתמש ---
@app.route("/delete_user", methods=["POST"])
def delete_user():
    data = request.json
    user_id = data.get("id")
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    db.commit()
    db.close()
    return jsonify({"message": "User deleted successfully"})

# --- ניהול כיתות ---
@app.route("/classes", methods=["GET"])
def get_classes():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name FROM classes ORDER BY id")
    rows = cursor.fetchall()
    db.close()
    return jsonify([{"id": cid, "name": name} for cid, name in rows])

@app.route("/add_class", methods=["POST"])
def add_class():
    data = request.json
    name = data.get("name")
    admin_id = data.get("admin_id")
    if not name or not admin_id:
        return jsonify({"error": "Missing name or admin_id"}), 400
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO classes (name, created_by) VALUES (?, ?)", (name, admin_id))
        db.commit()
        message = "Class created successfully"
    except:
        message = "Class already exists"
    db.close()
    return jsonify({"message": message})

@app.route("/delete_class", methods=["POST"])
def delete_class():
    data = request.json
    class_id = data.get("class_id")
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM classes WHERE id=?", (class_id,))
    db.commit()
    db.close()
    return jsonify({"message": "Class deleted successfully"})

# --- הגרלה אוטומטית לפי כיתה ---
@app.route("/generate_auto", methods=["POST"])
def generate_auto():
    data = request.json
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    class_id = data.get("class_id")
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM users WHERE class_id=?", (class_id,))
    users = [row[0] for row in cursor.fetchall()]
    db.close()
    if not users:
        return jsonify({"error": "No users in this class"}), 400
    weeks = generate_weeks(start_date, end_date)
    schedule = assign_cleaners(users, weeks)
    save_schedule(schedule, class_id)
    return jsonify(schedule)

# --- סימון לא זמין והחלפה ---
@app.route("/unavailable", methods=["POST", "GET"])
def mark_unavailable():
    if request.method == "POST":
        data = request.json
        user_name = data.get("name")
        week = data.get("week")
        class_id = data.get("class_id")
    else:
        user_name = request.args.get("name")
        week = request.args.get("week")
        class_id = request.args.get("class_id")
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE name=? AND class_id=?", (user_name, class_id))
    user = cursor.fetchone()
    if not user:
        db.close()
        return jsonify({"error": "User not found"}), 404
    user_id = user[0]

    cursor.execute("""
        INSERT OR REPLACE INTO availability (user_id, week, available)
        VALUES (?, ?, 0)
    """, (user_id, week))
    db.commit()

    # החלפת תורן
    cursor.execute("""
        SELECT a.user_id
        FROM assignments a
        LEFT JOIN availability av ON a.user_id = av.user_id AND a.week = av.week
        WHERE a.week = ? AND a.class_id=? AND (av.available IS NULL OR av.available = 1) AND a.user_id != ?
    """, (week, class_id, user_id))
    available_users = cursor.fetchall()
    if available_users:
        new_user_id = available_users[0][0]
        cursor.execute("""
            UPDATE assignments
            SET user_id = ?
            WHERE week = ? AND user_id = ? AND class_id=?
        """, (new_user_id, week, user_id, class_id))
        db.commit()
        message = f"{user_name} סומן כלא זמין והוחלף."
    else:
        message = f"{user_name} סומן כלא זמין, אך לא נמצא מחליף."
    db.close()
    if request.method == "GET":
        return f"<h2>{message}</h2>"
    return jsonify({"message": message})

# --- APScheduler לשליחת מיילים שבועיים ---
scheduler = BackgroundScheduler()
scheduler.add_job(send_weekly_notifications, 'cron', day_of_week='thu', hour=13, minute=0)
scheduler.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
