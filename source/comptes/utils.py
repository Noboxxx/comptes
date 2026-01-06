import json
import re
from datetime import datetime
import random
import string

from PySide6.QtGui import *
from PySide6.QtCore import *

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

def json_dump(data, file):
    s = json_dumps(data)

    with open(file, 'w', encoding='utf-8') as f:
        f.write(s)

def json_load(file):
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data

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

def create_category_icon(text, color, radius):
    pixmap = create_category_pixmap(text, color, radius)

    icon = QIcon()
    icon.addPixmap(pixmap, QIcon.Mode.Normal, QIcon.State.On)
    return icon

def create_category_pixmap(text, color, radius):
    size = radius * 2

    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))

    painter = QPainter(pixmap)
    painter.setRenderHints(
        QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing | QPainter.SmoothPixmapTransform)

    painter.setBrush(QColor(*color))
    painter.setPen(Qt.PenStyle.NoPen)
    margin = max(2, size // 20)
    circle_rect = QRectF(margin, margin, size - margin * 2, size - margin * 2)
    painter.drawEllipse(circle_rect)

    font = QFont()
    font.setPixelSize(int(size * 0.6))
    painter.setFont(font)

    painter.setPen(QColor('white'))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
    painter.end()

    return pixmap