import streamlit as st
from src_bck import twitter_scraper
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
APP_USER = os.getenv("APP_USER")
APP_PASS = os.getenv("APP_PASS")

st.set_page_config(page_title="X Scraper", layout="wide")

# Reset session on refresh
if "page_loaded_once" not in st.session_state:
    st.session_state.clear()
    st.session_state.page_loaded_once = True

# App auth
if "app_authenticated" not in st.session_state:
    st.session_state.app_authenticated = False

if not st.session_state.app_authenticated:
    st.sidebar.title("🕵️‍♂️ X/Twitter Scraper")
    st.sidebar.markdown("🔒 **Secure App Login**")
    st.sidebar.info("Your credentials are safe!\nManaged locally.")
    
    st.title("🔐 App Authentication")
    st.subheader("Welcome to the Private Scraper Dashboard")
    st.markdown("""
    Please log in with your **Admin Username and Password**  
    to unlock the Twitter/X scraping tool.
    """)
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == APP_USER and pw == APP_PASS:
            st.session_state.app_authenticated = True
            st.success("✅ Login successful")
            st.rerun()
        else:
            st.error("❌ Invalid credentials")
    st.stop()

# Twitter Auth
if "page" not in st.session_state:
    st.session_state.page = "auth"

if st.session_state.page == "auth":
    st.sidebar.title("🕵️‍♂️ X/Twitter Scraper")
    st.sidebar.markdown("✅ **App Login Successful!**")
    st.sidebar.markdown("🔑 **Step 2: Twitter Credentials**")
    st.sidebar.info("We don’t store your Twitter credentials.\nThey’re used securely for session scraping only.")

    st.title("🔒 Twitter/X Login")
    st.subheader("Authenticate your Twitter Account")
    st.markdown("""
    Enter your **Twitter/X email**, **username/phone**, and **password**  
    to let the scraper fetch posts in real-time.
    """)
    email = st.text_input("Twitter Email")
    username_or_phone = st.text_input("Twitter Username/Phone")
    password = st.text_input("Twitter Password", type="password")
    if st.button("Continue"):
        st.session_state.email = email
        st.session_state.username_or_phone = username_or_phone
        st.session_state.password = password
        st.session_state.page = "dashboard"
        st.rerun()

elif st.session_state.page == "dashboard":
    st.sidebar.title("🕵️‍♂️ X/Twitter Scraper")
    st.sidebar.markdown("✅ **Logged in as:**")
    st.sidebar.code(st.session_state.username_or_phone)
    st.sidebar.markdown("🔎 **Search & Scrape**")
    st.sidebar.info("Enter a keyword to fetch **Latest Tweets**.\nResults include username, tweet, relative time, and exact UTC timestamp.")

    st.title("📊 X/Twitter Scraper Dashboard")
    st.subheader("Live Tweet Search & Results")
    st.markdown("""
    Use the **search box** below to find tweets about your topic.  
    Click **Search** to scrape all posts from the last 24 hours.
    """)

    search_keyword = st.text_input("Search Keyword", "")
    if st.button("Search"):
        with st.spinner("Scraping tweets..."):
            df = twitter_scraper(
                st.session_state.email,
                st.session_state.username_or_phone,
                st.session_state.password,
                search_keyword
            )
            st.session_state.df = df

    if "df" in st.session_state:
        df = st.session_state.df
        st.success(f"✅ {len(df)} posts found!")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download CSV",
            csv,
            "tweets.csv",
            "text/csv"
        )