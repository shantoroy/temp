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

    # Navigate to Splunk search page
    driver.get(f"{SPLUNK_URL}/en-US/app/search/search")

    time.sleep(5)  # Wait for search page to load

    # Use JavaScript to set the query in the search bar
    search_bar_selector = "textarea[class='search-bar']"
    search_button_selector = "button[class*='search-btn']"  # Update this if needed

    driver.execute_script(f"document.querySelector('{search_bar_selector}').value = `{query}`;")
    time.sleep(2)  # Allow time for UI update

    # Click the search button
    search_button = driver.find_element(By.CSS_SELECTOR, search_button_selector)
    search_button.click()

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
