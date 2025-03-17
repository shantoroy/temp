from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
import threading

# Splunk credentials
SPLUNK_URL = "https://your-splunk-url.com"
USERNAME = "your-username"
PASSWORD = "your-password"

# List of 15 Splunk queries
SPLUNK_QUERIES = [
    "index=main | stats count",
    "index=security | top host",
    "index=web_logs | stats avg(response_time)",
    # Add more queries (Total 15)
]

# Create a folder for screenshots
SCREENSHOT_DIR = "splunk_screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def run_query(query, query_num):
    """Function to open a browser window, log in, run a Splunk query, and take a screenshot"""
    options = webdriver.EdgeOptions()
    options.add_argument("--start-maximized")  # Maximize window

    driver = webdriver.Edge(options=options)  # Start Edge WebDriver
    driver.get(SPLUNK_URL)

    # Login to Splunk
    time.sleep(3)  # Wait for page to load
    driver.find_element(By.ID, "username").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "login-button").click()

    time.sleep(5)  # Wait for login to complete

    # Navigate to the Splunk search bar
    driver.get(f"{SPLUNK_URL}/en-US/app/search/search")

    time.sleep(5)  # Wait for search page to load

    # Find the search box and input query
    search_box = driver.find_element(By.XPATH, "//textarea[@class='search-bar']")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    time.sleep(10)  # Wait for results to load

    # Take screenshot
    screenshot_path = os.path.join(SCREENSHOT_DIR, f"splunk_query_{query_num}.png")
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved: {screenshot_path}")

    # Close browser
    driver.quit()


# Run all queries in parallel using threads
threads = []
for i, query in enumerate(SPLUNK_QUERIES):
    t = threading.Thread(target=run_query, args=(query, i + 1))
    t.start()
    threads.append(t)

# Wait for all threads to complete
for t in threads:
    t.join()

print("All queries executed and screenshots saved.")
