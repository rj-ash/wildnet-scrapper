# scrapper.py

import json
import os
import time
import re
from datetime import datetime, timedelta
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

COOKIES_FILE = "cookies.json"

def cookies_valid():
    if not os.path.exists(COOKIES_FILE):
        return False
    with open(COOKIES_FILE, "r") as f:
        cookies = json.load(f)
    expirations = [c['expiry'] for c in cookies if 'expiry' in c]
    if not expirations:
        return False
    now_ts = int(time.time())
    return min(expirations) > now_ts

def load_cookies(driver):
    with open(COOKIES_FILE, "r") as f:
        cookies = json.load(f)
    driver.get("https://x.com/")
    for cookie in cookies:
        driver.add_cookie(cookie)

def save_cookies(driver):
    cookies = driver.get_cookies()
    with open(COOKIES_FILE, "w") as f:
        json.dump(cookies, f, indent=2)

def cookies_changed(old, new):
    old_map = {(c['name'], c.get('domain', ''), c.get('path', '')): (c['value'], c.get('expiry')) for c in old}
    new_map = {(c['name'], c.get('domain', ''), c.get('path', '')): (c['value'], c.get('expiry')) for c in new}
    return old_map != new_map

def twitter_scraper(email, username_or_phone, password, search_keyword):
    usernames, tweets, times, exact_times = [], [], [], []

    TWITTER_URL = "https://x.com/home"
    LOGIN_URL = "https://x.com/login"
    SEARCH_BOX_XPATH = '//form[@aria-label="Search" and @role="search"]//input'
    LATEST_TAB_XPATH = '//div[@role="presentation" and .//span[text()="Latest"]]/a'
    TIME_XPATH = '//div[./a and .//time[@datetime]]'
    USERNAME_XPATH = '//div[@data-testid="User-Name"]/div[1]'
    TWEET_XPATH = '//div[@data-testid="tweetText"]'

    EMAIL_INPUT_XPATH = '//label//input'
    NEXT_BUTTON_XPATH = '//button[.//span[contains(text(), "Next")]]'
    USERNAME_INPUT_XPATH = '//label//input'
    PASSWORD_INPUT_XPATH = '//div[./div[./div[./span[contains(text(), "Password")]]]]//input'
    LOGIN_BUTTON_XPATH = '//button[@data-testid="LoginForm_Login_Button"]'

    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 60)

    if cookies_valid():
        with open(COOKIES_FILE, "r") as f:
            old_cookies = json.load(f)
        driver.get("https://x.com/")
        load_cookies(driver)
        driver.get(TWITTER_URL)
        wait.until(EC.url_to_be(TWITTER_URL))
        fresh_cookies = driver.get_cookies()
        if cookies_changed(old_cookies, fresh_cookies):
            save_cookies(driver)
    else:
        driver.get(LOGIN_URL)
        email_input = wait.until(EC.presence_of_element_located((By.XPATH, EMAIL_INPUT_XPATH)))
        email_input.send_keys(email)
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, NEXT_BUTTON_XPATH)))
        next_button.click()

        try:
            username_input = wait.until(EC.presence_of_element_located((By.XPATH, USERNAME_INPUT_XPATH)))
            username_input.send_keys(username_or_phone)
            next_button2 = wait.until(EC.element_to_be_clickable((By.XPATH, NEXT_BUTTON_XPATH)))
            next_button2.click()
        except:
            pass

        password_input = wait.until(EC.presence_of_element_located((By.XPATH, PASSWORD_INPUT_XPATH)))
        password_input.send_keys(password)
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, LOGIN_BUTTON_XPATH)))
        login_button.click()
        wait.until(EC.url_to_be(TWITTER_URL))
        save_cookies(driver)

    # ---- SEARCH ----
    search_box = wait.until(EC.presence_of_element_located((By.XPATH, SEARCH_BOX_XPATH)))
    search_box.click()
    search_box.send_keys(search_keyword)
    search_box.send_keys(Keys.RETURN)

    latest_tab = wait.until(EC.element_to_be_clickable((By.XPATH, LATEST_TAB_XPATH)))
    latest_tab.click()

    keep_scrolling = True
    last_height = driver.execute_script("return document.body.scrollHeight")

    while keep_scrolling:
        time_elements = driver.find_elements(By.XPATH, TIME_XPATH)
        for time_element in time_elements:
            timestamp_text = time_element.text.strip()
            if re.match(r"^\d+[smh]$", timestamp_text):
                username_element = time_element.find_element(By.XPATH, ".//ancestor::article//" + USERNAME_XPATH[2:])
                username = username_element.text.strip()
                try:
                    tweet_element = time_element.find_element(By.XPATH, ".//ancestor::article//" + TWEET_XPATH[2:])
                    tweet = tweet_element.text.strip()
                except:
                    tweet = ""
                usernames.append(username)
                tweets.append(tweet)
                times.append(timestamp_text)
                # Calculate exact time
                amount = int(re.findall(r"\d+", timestamp_text)[0])
                unit = re.findall(r"[smh]", timestamp_text)[0]

                delta = timedelta()
                if unit == "s":
                    delta = timedelta(seconds=amount)
                elif unit == "m":
                    delta = timedelta(minutes=amount)
                elif unit == "h":
                    delta = timedelta(hours=amount)

                tweet_time = datetime.utcnow() - delta
                exact_times.append(tweet_time.strftime("%Y-%m-%d %H:%M:%S UTC"))
            else:
                keep_scrolling = False
                break
        if keep_scrolling:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    driver.quit()
    df = pd.DataFrame({
        "username": usernames,
        "tweet": tweets,
        "time": times,
        "time_of_tweet": exact_times  # New column
    })
    return df