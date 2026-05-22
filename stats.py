import csv
import matplotlib.pyplot as plt
import io
import base64
from collections import Counter

LOG_FILE = "requests_log.csv"

def generate_category_chart():
    counter = Counter()
    try:
        with open(LOG_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cat = row.get("category", "other")
                counter[cat] += 1
    except:
        pass

    if not counter:
        return None

    labels = list(counter.keys())
    values = list(counter.values())

    plt.figure(figsize=(6,4))
    plt.bar(labels, values, color='skyblue')
    plt.title("Обращения по категориям")
    plt.xlabel("Категория")
    plt.ylabel("Количество")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return img_base64

def generate_priority_chart():
    counter = Counter()
    try:
        with open(LOG_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pri = row.get("priority", "low")
                counter[pri] += 1
    except:
        pass

    if not counter:
        return None

    labels = list(counter.keys())
    values = list(counter.values())

    plt.figure(figsize=(5,4))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.title("Обращения по приоритетам")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return img_base64