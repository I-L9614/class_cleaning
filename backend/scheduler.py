import datetime
import random

def generate_weeks(start_date, end_date):
    start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    weeks = []
    current = start
    while current <= end:
        monday = current - datetime.timedelta(days=current.weekday())
        weeks.append(monday.strftime("%Y-%m-%d"))
        current += datetime.timedelta(days=7)
    return weeks

def assign_cleaners(users, weeks):
    schedule = {}
    for week in weeks:
        random.shuffle(users)
        num_cleaners = min(5, max(4, len(users)))
        schedule[week] = users[:num_cleaners]
    return schedule
