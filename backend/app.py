from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from scheduler import generate_weeks, assign_cleaners
from database import save_schedule, get_db, init_db
from notifications import send_weekly_notifications
import os

app = Flask(__name__)
CORS(app)

# --- יצירת DB אם לא קיים ---
if not os.path.exists("cleaning.db"):
    init_db()

# --- ROUTES קיימים ---
@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/schedule", methods=["GET"])
def get_schedule():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT a.week, u.name
        FROM assignments a
        JOIN users u ON a.user_id = u.id
        ORDER BY a.week
    """)
    rows = cursor.fetchall()
    db.close()
    result = {}
    for week, name in rows:
        if week not in result:
            result[week] = []
        result[week].append(name)
    return jsonify(result)

# --- Route להצגת כל המשתמשים ---
@app.route("/users", methods=["GET"])
def get_users():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name, email FROM users ORDER BY id")
    rows = cursor.fetchall()
    db.close()

    users_list = []
    for user_id, name, email in rows:
        users_list.append({
            "id": user_id,
            "name": name,
            "email": email
        })

    return jsonify(users_list)

# --- Route להרצת הגרלה ידנית ---
@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    names = data.get("names", [])
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    if not names or not start_date or not end_date:
        return jsonify({"error": "Missing names or dates"}), 400
    weeks = generate_weeks(start_date, end_date)
    schedule = assign_cleaners(names, weeks)
    save_schedule(schedule)
    return jsonify(schedule)

# --- Route להרצת הגרלה אוטומטית מהמשתמשים שנרשמו ---
@app.route("/generate_auto", methods=["POST"])
def generate_auto():
    data = request.json
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    if not start_date or not end_date:
        return jsonify({"error": "Missing start_date or end_date"}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM users")
    users = [row[0] for row in cursor.fetchall()]
    db.close()

    if not users:
        return jsonify({"error": "No users registered"}), 400

    weeks = generate_weeks(start_date, end_date)
    schedule = assign_cleaners(users, weeks)
    save_schedule(schedule)

    return jsonify(schedule)

# --- Route למשתמשים שאינם זמינים ---
@app.route("/unavailable", methods=["POST", "GET"])
def mark_unavailable():
    if request.method == "POST":
        data = request.json
        user_name = data.get("name")
        week = data.get("week")
    else:
        user_name = request.args.get("name")
        week = request.args.get("week")

    if not user_name or not week:
        return jsonify({"error": "Missing name or week"}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE name=?", (user_name,))
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

    # מחפש מחליף
    cursor.execute("""
        SELECT a.user_id
        FROM assignments a
        LEFT JOIN availability av ON a.user_id = av.user_id AND a.week = av.week
        WHERE a.week = ? AND (av.available IS NULL OR av.available = 1) AND a.user_id != ?
    """, (week, user_id))
    available_users = cursor.fetchall()
    if available_users:
        new_user_id = available_users[0][0]
        cursor.execute("""
            UPDATE assignments
            SET user_id = ?
            WHERE week = ? AND user_id = ?
        """, (new_user_id, week, user_id))
        db.commit()
        message = f"{user_name} סומן כלא זמין והוחלף על ידי משתמש אחר."
    else:
        message = f"{user_name} סומן כלא זמין, אך לא נמצא מחליף."

    db.close()

    if request.method == "GET":
        return f"<h2>{message}</h2>"

    return jsonify({"message": message})

# --- ROUTES להרשמה ---
@app.route("/register", methods=["GET"])
def register_form():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register_user():
    name = request.form.get("name")
    email = request.form.get("email")

    if not name or not email:
        return "חובה למלא שם ואימייל", 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE name=? OR email=?", (name, email))
    user = cursor.fetchone()
    if user:
        message = "המשתמש כבר רשום."
    else:
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
        db.commit()
        message = "הרשמתך בוצעה בהצלחה!"
    db.close()
    return f"<h3>{message}</h3>"

# --- APScheduler לשליחת התראות שבועיות ---
scheduler = BackgroundScheduler()
scheduler.add_job(send_weekly_notifications, 'cron', day_of_week='thu', hour=13, minute=0)
scheduler.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
