Price Tracker Pro

A small, working price-monitoring tool that checks a product's price, remembers past prices, and sends an email alert whenever the price drops.

What This Project Does
Fetches the current price of tracked products from a website
Stores every price check in a local database (price_history.db) — this builds a price history over time
Compares the newest price against the last recorded price
Sends an email alert automatically if the price has dropped

This mirrors how real-world tools like deal-tracking sites and e-commerce price monitors work, just on a smaller scale.

How It Works (Simple Explanation)

Think of it like a small robot with a notebook:

Every time it runs, it visits the product page and reads the price
It writes that price down in its notebook (the database), with a timestamp
It looks back at the last price it wrote down and compares
If the new price is lower, it emails you the good news
Tech Stack
Python — core language
Requests — fetches web pages
BeautifulSoup — extracts price data from HTML
SQLite — stores price history locally (no external database needed)
smtplib + Gmail App Password — sends real email alerts
python-dotenv — keeps email credentials out of the codebase (.env file, never committed to Git)
Project Structure
price-tracker-pro/
├── main.py              # main script
├── .env                 # email credentials (NOT committed to Git)
├── .gitignore
├── README.md
├── price_history.db     # SQLite database (auto-created)
└── cache/               # cached HTML pages (auto-created)
How to Run
Install dependencies:
   py -m pip install requests beautifulsoup4 python-dotenv
Create a .env file in the project folder with:
   EMAIL_ADDRESS=your_email@gmail.com
   EMAIL_APP_PASSWORD=your16digitapppassword
   ALERT_RECIPIENT=your_email@gmail.com

(Use a Gmail App Password, not your real password — generate one under Google Account → Security → 2-Step Verification → App Passwords)

Run the script:
   py main.py
Every time it runs, it checks each tracked product and prints one of:
NEW — first time this product has been checked
NO CHANGE — price is the same as last check
PRICE UP — price increased
PRICE DROP — price decreased, and an email alert is sent
Adding Products to Track

Edit the TRACKED_PRODUCTS list in main.py:

python
TRACKED_PRODUCTS = [
    {"name": "Product Name", "url": "https://example.com/product-page"},
]
Privacy & Security Notes
Email credentials live only in .env, which is excluded from Git via .gitignore — they are never pushed to GitHub
A Gmail App Password is used instead of the real account password — it only grants limited access (sending mail) and can be revoked anytime from Google Account settings without changing the main password
No personal or sensitive data is scraped — only public product/price information
Target & Ethics

This project currently points at a public scraping practice sandbox for testing. Before pointing this at any real store, check that site's robots.txt and Terms of Service, and prefer an official API if one is available.

Known Limitations / Next Steps
Currently runs manually — could be automated with a scheduler (e.g. Windows Task Scheduler or the Python schedule library) to check prices daily
Only tracks a hardcoded list of products — could be extended to read products from a config file or simple UI
Single retry/error handling is basic — a production version would add proper retry logic and structured logging