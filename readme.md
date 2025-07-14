
# X/Twitter Scraper

A simple, secure Streamlit app to scrape latest tweets by keyword — using Selenium & smart cookie-based login.

⸻

## How it works
	• Step 1: Admin login (credentials from .env)
	• Step 2: Enter your Twitter/X login (email, username/phone, password)
	• Step 3: Search for any keyword → scraper gets all tweets within last 24h
	• Smart Cookies: Saves your session to cookies.json → skips login next time if still valid.

⸻

## What you get
	•	Username
	•	Tweet text
	•	Relative time (5m, 2h)
	•	Exact UTC time (2025-07-14 12:30:00 UTC)
	•	Download results as CSV

⸻

## Tech Stack
	•	Python, Selenium, Streamlit, pandas, python-dotenv
	•	Uses cookies to minimize repeat logins

⸻

## Run it

pip install -r requirements.txt

# Add your .env file:
# APP_USER=myuser
# APP_PASS=mypass

streamlit run app.py

