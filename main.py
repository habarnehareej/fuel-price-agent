from playwright.sync_api import sync_playwright
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
load_dotenv()

QUOTE_URL = "https://fuelbreak.axxispetro.com/QuoteList.aspx"

def extract_prices(text):
    for line in text.splitlines():
        if "Price:" in line:
            numbers = re.findall(r"\d+\.\d+", line)
            if len(numbers) >= 3:
                return {"87": numbers[0], "91": numbers[2]}
    return {"87": "Not found", "91": "Not found"}

def open_quote(page, index):
    view_buttons = page.locator("input[src='images/Look.gif']")
    print("View buttons found:", view_buttons.count())

    view_buttons.nth(index).click()
    page.wait_for_url("**/ViewQuote.aspx", timeout=10000)
    page.wait_for_timeout(2000)

    return page.inner_text("body")

def send_email(today_prices, yesterday_prices, sell_87, sell_91):
    sender_email = os.getenv("EMAIL")
    app_password = os.getenv("APP_PASSWORD")
    receiver_email = "receiver_email"

    subject = "Daily Fuel Price Report for Yucaipa"

    diff_87 = round(float(today_prices["87"]) - float(yesterday_prices["87"]), 4)
    diff_91 = round(float(today_prices["91"]) - float(yesterday_prices["91"]), 4)

    body = f"""
    <html>
    <body style="font-family: Arial; color:#222;">
        <h2>Daily Fuel Price Report</h2>

        <table border="1" cellpadding="10" cellspacing="0" style="border-collapse: collapse;">
            <tr style="background-color:#f2f2f2;">
                <th>Product</th>
                <th>Today</th>
                <th>Yesterday</th>
                <th>Change</th>
                <th>Selling Price</th>
            </tr>
            <tr>
                <td>87RE10</td>
                <td>{today_prices["87"]}</td>
                <td>{yesterday_prices["87"]}</td>
                <td>{diff_87}</td>
                <td>{sell_87}</td>
            </tr>
            <tr>
                <td>91RE10</td>
                <td>{today_prices["91"]}</td>
                <td>{yesterday_prices["91"]}</td>
                <td>{diff_91}</td>
                <td>{sell_91}</td>
            </tr>
        </table>

        <br>
        <b>Status:</b> {"Prices Increased 📈" if diff_91 > 0 else "Prices Decreased 📉"}
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.send_message(msg)

    print("✅ Email sent!")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=["--start-maximized"])
    context = browser.new_context(storage_state="auth_state.json", viewport=None)
    page = context.new_page()

    page.goto(QUOTE_URL)
    page.wait_for_timeout(3000)

    if "Login.aspx" in page.url:
        print("❌ Session expired. Run save_login.py again.")
        browser.close()
        exit()

    today_text = open_quote(page, 0)
    today_prices = extract_prices(today_text)

    page.go_back()
    page.wait_for_timeout(2000)

    yesterday_text = open_quote(page, 1)
    yesterday_prices = extract_prices(yesterday_text)

    print("\n===== TODAY =====")
    print("87RE10:", today_prices["87"])
    print("91RE10:", today_prices["91"])

    print("\n===== YESTERDAY =====")
    print("87RE10:", yesterday_prices["87"])
    print("91RE10:", yesterday_prices["91"])

    sell_87 = input("our price 87: ")
    sell_91 = input("our price 91: ")

    send_email(today_prices, yesterday_prices, sell_87, sell_91)

    browser.close()
