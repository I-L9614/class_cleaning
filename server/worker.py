from apscheduler.schedulers.blocking import BlockingScheduler
from utils import run_lottery
from models import Classes, Students
import smtplib
import os
from email.mime.text import MIMEText

def send_weekly_reminder():
    classes = Classes.find()
    for cls in classes:
        results = run_lottery(str(cls['_id']))
        for week, students in results.items():
            for student in students:
                msg = MIMEText(f"אתה תורן השבוע בכיתה {cls['name']}")
                msg['Subject'] = "תזכורת תורנות"
                msg['From'] = os.environ['MAIL_USER']
                msg['To'] = student['email']
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(os.environ['MAIL_USER'], os.environ['MAIL_PASS'])
                    server.send_message(msg)
scheduler = BlockingScheduler()
scheduler.add_job(send_weekly_reminder, 'cron', day_of_week='thu', hour=13)
scheduler.start()
