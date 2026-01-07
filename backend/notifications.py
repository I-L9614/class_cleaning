import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database import get_db
import os
from datetime import datetime

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
APP_BASE_URL = "http://localhost:5000"

def send_weekly_notifications():
    db = get_db()
    cur = db.cursor()
    today = datetime.today().strftime("%Y-%m-%d")

    cur.execute("""
        SELECT u.name, u.email, a.week_start, s.name as class_name
        FROM assignments a
        JOIN students u ON a.student_id = u.id
        JOIN classes s ON u.class_id = s.id
        WHERE a.week_start=?
    """, (today,))
    rows = cur.fetchall()
    db.close()

    if not rows:
        return

    for name, email, week, class_name in rows:
        if not email:
            continue

        unavailable_link = f"{APP_BASE_URL}/unavailable?name={name}&week={week}"
        html_content = f"""
        <html>
        <body>
            <p>שלום {name},</p>
            <p>אתה תורן ניקיון לשבוע {week} בכיתה {class_name}.</p>
            <p>אם אינך יכול השבוע, לחץ על הכפתור למטה:</p>
            <p>
                <a href="{unavailable_link}" style="
                    display:inline-block;
                    padding:10px 20px;
                    font-size:16px;
                    color:white;
                    background-color:#dc3545;
                    text-decoration:none;
                    border-radius:5px;
                ">לא יכול השבוע</a>
            </p>
        </body>
        </html>
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"תורנות ניקיון לשבוע {week}"
        msg["From"] = SMTP_USER
        msg["To"] = email
        msg.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
            print(f"Sent notification to {name} ({email})")
        except Exception as e:
            print(f"Failed to send to {name}: {e}")
