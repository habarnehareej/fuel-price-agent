from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os

load_dotenv()

LOGIN_URL = "https://fuelbreak.axxispetro.com/Login.aspx"

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=["--start-maximized"]
    )

    context = browser.new_context(viewport=None)
    page = context.new_page()

    page.goto(LOGIN_URL)

    page.fill('input[type="text"]', USERNAME)
    page.fill('input[type="password"]', PASSWORD)

    print("Solve CAPTCHA and click Log In.")
    input("After reaching Home page, press Enter...")

    context.storage_state(path="auth_state.json")

    print("✅ Login session saved successfully!")

    browser.close()
