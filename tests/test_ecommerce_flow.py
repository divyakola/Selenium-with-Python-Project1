from uuid import uuid4
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def wait_for(driver, locator, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located(locator)
    )

def click_when_ready(driver, locator, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable(locator)
    ).click()

def test_complete_customer_journey(driver, base_url):
    """End-to-end test: signup -> signin -> search -> cart -> checkout -> logout."""
    email = f"qa_{uuid4().hex[:10]}@example.test"
    password = "TestPass123!"
    customer_name = "Selenium Test Customer"

    # 1. Sign up
    driver.get(f"{base_url}/signup")
    wait_for(driver, (By.ID, "name")).send_keys(customer_name)
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password)
    click_when_ready(driver, (By.ID, "signup-submit"))
    wait_for(driver, (By.ID, "signin-form"))
    assert "signin" in driver.current_url

    # 2. Sign in
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password)
    click_when_ready(driver, (By.ID, "signin-submit"))
    wait_for(driver, (By.ID, "product-list"))
    assert "Products" in driver.find_element(By.TAG_NAME, "h1").text
    assert customer_name in driver.find_element(By.ID, "welcome-user").text

    # 3. Search for a product
    search = driver.find_element(By.ID, "search")
    search.send_keys("Python")
    click_when_ready(driver, (By.ID, "search-submit"))
    product_name = wait_for(driver, (By.CSS_SELECTOR, ".product-name")).text
    assert "Python" in product_name

    # 4. Add product to cart
    click_when_ready(driver, (By.CSS_SELECTOR, ".add-to-cart"))
    click_when_ready(driver, (By.ID, "cart-link"))
    wait_for(driver, (By.ID, "cart-table"))
    assert product_name in driver.find_element(By.CSS_SELECTOR, ".cart-product-name").text
    assert driver.find_element(By.CSS_SELECTOR, ".cart-quantity").text == "1"

    # 5. Checkout with test-only shipping information
    click_when_ready(driver, (By.ID, "checkout-link"))
    wait_for(driver, (By.ID, "checkout-form"))
    driver.find_element(By.ID, "full_name").send_keys(customer_name)
    driver.find_element(By.ID, "address").send_keys("123 Test Street")
    driver.find_element(By.ID, "city").send_keys("Hyderabad")
    driver.find_element(By.ID, "postal_code").send_keys("500001")
    click_when_ready(driver, (By.ID, "place-order"))

    confirmation = wait_for(driver, (By.ID, "order-confirmation"))
    assert "Order placed successfully" in confirmation.text
    order_id = driver.find_element(By.ID, "order-id").text
    assert order_id

    # Verify cart is cleared after order, then logout.
    driver.get(f"{base_url}/cart")
    wait_for(driver, (By.ID, "empty-cart"))
    click_when_ready(driver, (By.ID, "logout-button"))
    wait_for(driver, (By.ID, "signin-form"))
    assert "signin" in driver.current_url
    assert driver.find_elements(By.ID, "welcome-user") == []

def test_signin_rejects_wrong_password(driver, base_url):
    """Negative test: an unknown account / wrong password should not authenticate."""
    driver.get(f"{base_url}/signin")
    driver.find_element(By.ID, "email").send_keys("unknown@example.test")
    driver.find_element(By.ID, "password").send_keys("WrongPass123")
    click_when_ready(driver, (By.ID, "signin-submit"))
    assert "Invalid email or password." in wait_for(
        driver, (By.CSS_SELECTOR, ".flash.error")
    ).text
