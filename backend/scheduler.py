from apscheduler.schedulers.background import BackgroundScheduler
from notifications import send_weekly_notifications
from database import get_db

def start_scheduler():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT value FROM settings WHERE key='notify_hour'")
    notify_hour = int(cur.fetchone()["value"])
    cur.execute("SELECT value FROM settings WHERE key='notify_minute'")
    notify_minute = int(cur.fetchone()["value"])
    db.close()

    scheduler = BackgroundScheduler()
    scheduler.add_job(send_weekly_notifications, 'cron', day_of_week='thu', hour=notify_hour, minute=notify_minute)
    scheduler.start()
    print("Scheduler started")
