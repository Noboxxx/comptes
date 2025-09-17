import json
import re
from datetime import datetime
import random
import string

def random_id():
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(8))

def print_json(data):
    print(json_dumps(data))

def json_dumps(data):

    def plop(x):
        if hasattr(x, 'get_data'):
            return x.get_data()
        else:
            return str(x)

    s = json.dumps(data, default=plop, ensure_ascii=False, indent=4)
    return s

def get_one_liner_text(text):
    text = text.replace('\n', ' ')
    text = re.sub(' +', ' ', text)
    return text

def get_number_of_days(month, year):
    month = int(month)
    year = int(year)

    first_day = datetime(year, month, 1)

    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)

    days_in_month = next_month - first_day
    return days_in_month.days

def split_date(date):
    day, month, year = date.split('/')

    data = {
        'day': day,
        'month': month,
        'year': year,
    }

    return data