import requests
import os
import re
import json
import sqlite3
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

USER_AGENT = "PriceTrackerPro/1.0 (+https://github.com/lhub2856-bit/price-tracker-pro)"
CACHE_DIR = "cache"
DB_FILE = "price_history.db"

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
ALERT_RECIPIENT = os.getenv("ALERT_RECIPIENT")

# Products to track (in a real project, this list could come from a config file)
TRACKED_PRODUCTS = [
    {
        "name": "A Light in the Attic",
        "url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    },
    {
        "name": "Soumission",
        "url": "https://books.toscrape.com/catalogue/soumission_998/index.html"
    },
]


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            product_url TEXT,
            price_gbp REAL,
            checked_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def fetch_page(url, cache_path):
    os.makedirs(CACHE_DIR, exist_ok=True)
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code != 200:
        print(f"FAILED - status={response.status_code} url={url}")
        return None

    html = response.text
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(html)
    return html


def extract_price(html):
    soup = BeautifulSoup(html, "html.parser")
    price_text = soup.select_one("p.price_color").get_text(strip=True)
    match = re.search(r"[\d.]+", price_text)
    return float(match.group()) if match else None


def get_last_price(product_url):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT price_gbp FROM price_history
        WHERE product_url = ?
        ORDER BY checked_at DESC LIMIT 1
    """, (product_url,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def save_price(product_name, product_url, price):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO price_history (product_name, product_url, price_gbp, checked_at)
        VALUES (?, ?, ?, ?)
    """, (product_name, product_url, price, datetime.now(timezone.utc).isoformat()))
    conn.commit()
    conn.close()


def send_email_alert(product_name, old_price, new_price, product_url):
    subject = f"Price Drop Alert: {product_name}"
    body = f"""Good news!

{product_name} dropped in price.

Old price: £{old_price}
New price: £{new_price}
Link: {product_url}
"""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = ALERT_RECIPIENT

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
            server.send_message(msg)
        print(f"EMAIL SENT - {product_name}")
    except Exception as e:
        print(f"EMAIL FAILED - {e}")


def check_product(product):
    cache_path = os.path.join(CACHE_DIR, f"{product['name'].replace(' ', '_')}.html")
    html = fetch_page(product["url"], cache_path)

    if html is None:
        return

    current_price = extract_price(html)
    last_price = get_last_price(product["url"])

    save_price(product["name"], product["url"], current_price)

    if last_price is None:
        print(f"NEW - {product['name']}: £{current_price} (first check)")
    elif current_price < last_price:
        print(f"PRICE DROP - {product['name']}: £{last_price} -> £{current_price}")
        send_email_alert(product["name"], last_price, current_price, product["url"])
    elif current_price > last_price:
        print(f"PRICE UP - {product['name']}: £{last_price} -> £{current_price}")
    else:
        print(f"NO CHANGE - {product['name']}: £{current_price}")


if __name__ == "__main__":
    init_db()
    for product in TRACKED_PRODUCTS:
        check_product(product)