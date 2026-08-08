from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import sqlite3

app = FastAPI()

DB_FILE = "price_history.db"


def get_latest_prices():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Har product ki sabse recent price nikaalo
    cursor.execute("""
        SELECT product_name, product_url, price_gbp, checked_at
        FROM price_history
        WHERE id IN (
            SELECT MAX(id) FROM price_history GROUP BY product_url
        )
    """)
    rows = cursor.fetchall()
    conn.close()

    products = []
    for name, url, price, checked_at in rows:
        products.append({
            "name": name,
            "url": url,
            "price": price,
            "checked_at": checked_at
        })
    return products


# Ye "endpoint" hai — jab browser /api/prices pe request bheje, ye data wapis deta hai
@app.get("/api/prices")
def api_prices():
    return get_latest_prices()


# Ye endpoint dashboard (homepage) dikhata hai
@app.get("/", response_class=HTMLResponse)
def dashboard():
    with open("dashboard.html", "r", encoding="utf-8") as f:
        return f.read()