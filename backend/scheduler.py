import random
from datetime import datetime, timedelta
from collections import defaultdict

def generate_weeks(start_date, end_date):
    weeks = []
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    current = start
    while current <= end:
        weeks.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=7)
    return weeks

def assign_cleaners(names, weeks, min_per_week=4, max_per_week=5):
    schedule = defaultdict(list)
    pool = names.copy()
    random.shuffle(pool)
    index = 0
    for week in weeks:
        count = random.randint(min_per_week, max_per_week)
        for _ in range(count):
            if index >= len(pool):
                random.shuffle(pool)
                index = 0
            schedule[week].append(pool[index])
            index += 1
    return schedule
