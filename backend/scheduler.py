import datetime
import random

def generate_weeks(start_date, end_date):
    start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    weeks = []
    current = start
    while current <= end:
        weeks.append(current.strftime("%Y-%m-%d"))
        current += datetime.timedelta(days=7)
    return weeks

def assign_cleaners(names, weeks):
    schedule = {}
    for week in weeks:
        random.shuffle(names)
        num_cleaners = min(max(4, len(names)), 5)
        schedule[week] = names[:num_cleaners]
    return schedule
