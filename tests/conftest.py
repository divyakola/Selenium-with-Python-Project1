import os
import pytest
from selenium import webdriver

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    # Set HEADLESS=1 to run without opening a visible browser.
    if os.getenv("HEADLESS") == "1":
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--disable-notifications")
    browser = webdriver.Chrome(options=options)
    browser.implicitly_wait(0)
    yield browser
    browser.quit()

@pytest.fixture
def base_url():
    return BASE_URL
