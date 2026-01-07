import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database import get_db
import datetime
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.environ.get("SMTP_USER")  # שמור את המייל כ-ENV
SMTP_PASS = os.environ.get("SMTP_PASS")  # שמור את הסיסמה כ-ENV

APP_BASE_URL = "https://class-cleaning.onrender.com"

def send_weekly_notifications():
    db = get_db()
    cursor = db.cursor()
    today = datetime.date.today()
    week_start = (today - datetime.timedelta(days=today.weekday())).strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT u.name, u.email, a.week
        FROM assignments a
        JOIN users u ON a.user_id = u.id
        WHERE a.week = ?
    """, (week_start,))
    rows = cursor.fetchall()
    db.close()

    if not rows:
        return

    for name, email, week in rows:
        if not email:
            continue

        unavailable_link = f"{APP_BASE_URL}/unavailable?name={name}&week={week}"
        register_link = f"{APP_BASE_URL}/register"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"תורנות ניקיון לשבוע {week}"
        msg["From"] = SMTP_USER
        msg["To"] = email

        html_content = f"""
        <html>
        <body>
            <p>שלום {name},</p>
            <p>אתה תורן לניקיון הכיתה השבוע ({week}).</p>
            <p>אם אינך זמין השבוע, לחץ על הכפתור למטה:</p>
            <p>
                <a href="{unavailable_link}" style="
                    display:inline-block;
                    padding:10px 20px;
                    font-size:16px;
                    color:white;
                    background-color:#007bff;
                    text-decoration:none;
                    border-radius:5px;
                ">לא זמין השבוע</a>
            </p>
            <p>אם עדיין לא רשמת את עצמך, לחץ כאן להרשמה:</p>
            <p>
                <a href="{register_link}" style="
                    display:inline-block;
                    padding:10px 20px;
                    font-size:16px;
                    color:white;
                    background-color:#28a745;
                    text-decoration:none;
                    border-radius:5px;
                ">הרשם לתורנות</a>
            </p>
            <p>תודה!</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
            print(f"Sent notification to {name} ({email})")
        except Exception as e:
            print(f"Failed to send to {name}: {e}")
