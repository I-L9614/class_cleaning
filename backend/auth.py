from flask import request, flash, redirect, render_template
from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:5000")

# ----------------------------
# התחברות מנהל
# ----------------------------
def login_admin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT password_hash FROM admins WHERE email=?", (email,))
        row = cur.fetchone()
        db.close()

        if row and check_password_hash(row["password_hash"], password):
            flash("התחברת בהצלחה כמנהל")
            return redirect("/admin")
        else:
            flash("אימייל או סיסמא לא נכונים")
            return redirect("/login")

    return render_template("login.html")

# ----------------------------
# הזמנת מנהל חדש
# ----------------------------
def invite_admin():
    if request.method == "POST":
        email = request.form["email"]

        db = get_db()
        cur = db.cursor()
        # הכנס למערכת עם סיסמא ריקה
        cur.execute("INSERT INTO admins (email, password_hash) VALUES (?, ?)", (email, ""))
        db.commit()
        db.close()

        # שליחת מייל עם לינק לבחירת סיסמא
        link = f"{APP_BASE_URL}/set_password?email={email}"
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "הגדרת סיסמא ראשונית למנהל"
        msg["From"] = SMTP_USER
        msg["To"] = email

        html_content = f"""
        <html>
        <body>
            <p>שלום,</p>
            <p>לחץ על הקישור למטה כדי להגדיר את הסיסמא הראשונית שלך כמנהל:</p>
            <p><a href="{link}">בחר סיסמא</a></p>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
            flash("מייל הזמנה נשלח בהצלחה!")
        except Exception as e:
            flash(f"שגיאה בשליחת המייל: {e}")

        return redirect("/login")

    return render_template("invite_admin.html")

# ----------------------------
# הגדרת סיסמא ראשונית
# ----------------------------
def set_password():
    email = request.args.get("email")
    if request.method == "POST":
        password = request.form["password"]
        password_hash = generate_password_hash(password)

        db = get_db()
        cur = db.cursor()
        cur.execute("UPDATE admins SET password_hash=? WHERE email=?", (password_hash, email))
        db.commit()
        db.close()

        flash("הסיסמא הוגדרה בהצלחה! כעת אתה יכול להתחבר.")
        return redirect("/login")

    return render_template("set_password.html", email=email)
