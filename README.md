# Python + Selenium E-Commerce QA Automation Project

A self-contained demo e-commerce web application and Selenium + Pytest automation suite.

## Workflow automated
1. Sign up
2. Sign in
3. Search for a product
4. Add the product to the cart
5. Checkout using test-only shipping details
6. Verify order confirmation
7. Log out

This is a local demo application. It does not connect to a payment provider and does not charge money.

## Requirements
- Python 3.10+
- Google Chrome installed
- Internet access the first time Selenium Manager needs to obtain a compatible driver (depending on your environment)

## Setup (Windows PowerShell)
```powershell
cd python_selenium_ecommerce_project
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Start the demo website
Open Terminal 1:
```powershell
python app.py
```
The website runs at http://127.0.0.1:5000.

Keep this terminal open while tests run.

## Run Selenium tests
Open Terminal 2 in the same project folder and activate the environment:
```powershell
.\.venv\Scripts\Activate.ps1
pytest -v
```

The tests use a fresh browser session per test and create unique test accounts. Chrome should open and close automatically.

## Run one test
```powershell
pytest -v tests/test_ecommerce_flow.py::test_complete_customer_journey
```

## Project structure
```text
python_selenium_ecommerce_project/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   ├── base.html
│   ├── signup.html
│   ├── signin.html
│   ├── products.html
│   ├── cart.html
│   ├── checkout.html
│   └── confirmation.html
└── tests/
    ├── conftest.py
    └── test_ecommerce_flow.py
```

## QA notes
- The app stores demo users, carts, and orders in memory. Restarting `app.py` clears them.
- Product search matches product names and categories.
- Checkout is simulated; no real payment or order fulfilment occurs.
- Selectors use stable IDs and data attributes to make the test suite easier to maintain.
- Explicit waits are used rather than fixed sleeps.
- For a real company project, use a test environment, approved test accounts, secure secret handling, and a payment sandbox.
