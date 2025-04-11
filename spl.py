#!/usr/bin/env python3
import time
import yaml
import argparse
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SplunkDashboardScreenshotter:
    def __init__(self, config_path):
        """Initialize with configuration from YAML file."""
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        self.setup_driver()
        self.screenshot_dir = self.config.get('screenshot_dir', 'screenshots')
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # Default wait times (in seconds)
        self.page_load_wait = self.config.get('page_load_wait', 30)
        self.panel_load_wait = self.config.get('panel_load_wait', 10)
        self.scroll_pause_time = self.config.get('scroll_pause_time', 1)
    
    def setup_driver(self):
        """Set up the WebDriver based on configuration."""
        browser = self.config.get('browser', 'chrome').lower()
        
        if browser == 'chrome':
            options = webdriver.ChromeOptions()
            if self.config.get('headless', False):
                options.add_argument('--headless')
            options.add_argument('--window-size=1920,1080')
            self.driver = webdriver.Chrome(options=options)
        elif browser == 'firefox':
            options = webdriver.FirefoxOptions()
            if self.config.get('headless', False):
                options.add_argument('--headless')
            self.driver = webdriver.Firefox(options=options)
        else:
            raise ValueError(f"Unsupported browser: {browser}")
        
        self.driver.maximize_window()
    
    def login(self):
        """Log in to Splunk."""
        logger.info("Logging in to Splunk...")
        
        self.driver.get(self.config['splunk_url'])
        
        try:
            # Wait for login form
            username_field = WebDriverWait(self.driver, self.page_load_wait).until(
                EC.presence_of_element_located((By.ID, 'username'))
            )
            
            username_field.send_keys(self.config['username'])
            self.driver.find_element(By.ID, 'password').send_keys(self.config['password'])
            self.driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
            
            # Wait for successful login
            WebDriverWait(self.driver, self.page_load_wait).until(
                EC.presence_of_element_located((By.ID, 'dashboard-body'))
            )
            logger.info("Successfully logged in")
            
        except TimeoutException:
            logger.error("Failed to log in to Splunk")
            self.driver.quit()
            raise
    
    def navigate_to_dashboard(self, dashboard_url):
        """Navigate to the specified dashboard."""
        logger.info(f"Navigating to dashboard: {dashboard_url}")
        self.driver.get(dashboard_url)
        
        try:
            # Wait for dashboard to load
            WebDriverWait(self.driver, self.page_load_wait).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.dashboard-body'))
            )
            
            # Wait for panels to load
            self.wait_for_panels_to_load()
            
            logger.info("Dashboard loaded successfully")
            
        except TimeoutException:
            logger.error("Failed to load dashboard")
            raise
    
    def wait_for_panels_to_load(self):
        """Wait for dashboard panels to load completely."""
        logger.info("Waiting for dashboard panels to load...")
        
        try:
            # Wait for all panel content to be visible
            WebDriverWait(self.driver, self.panel_load_wait).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.dashboard-panel'))
            )
            
            # Wait for loading indicators to disappear
            WebDriverWait(self.driver, self.panel_load_wait).until_not(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.dashboard-panel .loading'))
            )
            
            # Additional wait for visualizations to render
            time.sleep(self.config.get('visualization_render_wait', 2))
            
            logger.info("All panels loaded")
            
        except TimeoutException:
            logger.warning("Timeout waiting for panels to load completely")
    
    def scroll_and_screenshot(self):
        """Scroll through the dashboard and take screenshots."""
        logger.info("Starting scroll and screenshot process")
        
        # Get initial scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        # Take initial screenshot
        self.take_screenshot("top")
        
        # Scroll down page, taking screenshots at each scroll position
        scroll_position = 1
        while True:
            # Scroll down
            self.driver.execute_script("window.scrollBy(0, window.innerHeight);")
            
            # Wait for page to load new content
            time.sleep(self.scroll_pause_time)
            
            # Wait for any dynamic content to load after scrolling
            self.wait_for_panels_to_load()
            
            # Take screenshot
            self.take_screenshot(f"position_{scroll_position}")
            scroll_position += 1
            
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            current_position = self.driver.execute_script("return window.pageYOffset + window.innerHeight")
            
            # If we've reached the bottom of the page, break
            if current_position >= new_height:
                break
            
            last_height = new_height
        
        logger.info(f"Completed scrolling and taking screenshots. Total screens: {scroll_position}")
    
    def take_screenshot(self, name_suffix):
        """Take a screenshot and save it with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dashboard_name = self.config.get('dashboard_name', 'dashboard').replace(' ', '_')
        filename = f"{dashboard_name}_{name_suffix}_{timestamp}.png"
        filepath = os.path.join(self.screenshot_dir, filename)
        
        self.driver.save_screenshot(filepath)
        logger.info(f"Screenshot saved: {filepath}")
    
    def run(self):
        """Execute the full workflow."""
        try:
            self.login()
            
            for dashboard in self.config['dashboards']:
                self.navigate_to_dashboard(dashboard['url'])
                if dashboard.get('name'):
                    self.config['dashboard_name'] = dashboard['name']
                self.scroll_and_screenshot()
                
        finally:
            logger.info("Closing WebDriver")
            self.driver.quit()


def main():
    parser = argparse.ArgumentParser(description='Tool to scroll through Splunk dashboards and take screenshots')
    parser.add_argument('--config', '-c', required=True, help='Path to YAML configuration file')
    args = parser.parse_args()
    
    try:
        screenshotter = SplunkDashboardScreenshotter(args.config)
        screenshotter.run()
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()
