import os
import sys
import requests
from playwright.sync_api import sync_playwright

# --- CONFIGURATION ---
TARGET_URL = os.environ.get("TARGET_URL")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")


def notify_discord(message):
    """Send a Discord webhook notification if WEBHOOK_URL is configured."""
    if not WEBHOOK_URL:
        print("::warning:: No Webhook URL set. Skipping notification.")
        return

    data = {
        "content": f"🚨 **Availability Found!**\n{message}\n[Click here to book]({TARGET_URL})"
    }
    try:
        requests.post(WEBHOOK_URL, json=data)
    except Exception as e:
        print(f"Failed to send webhook: {e}")


def check_availability():
    """Launch Playwright, look for enabled calendar buttons, and alert if found."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        print(f"Checking: {TARGET_URL}...")

        try:
            page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)

            # Calendly and similar sites render calendar cells as buttons inside tables.
            page.wait_for_selector("table", timeout=20000)

            no_times_msg = page.locator("text=No times in").count()
            available_buttons = page.locator("table button:not([disabled])")
            count = available_buttons.count()

            print(f"Status: Found {count} active buttons. 'No times' msg count: {no_times_msg}")

            if count > 0:
                first_date = (
                    available_buttons.first.get_attribute("aria-label")
                    or available_buttons.first.inner_text()
                )
                notify_discord(f"Found {count} available day(s)! First available: {first_date}")
            elif no_times_msg > 0:
                print("Confirmed 'No times' message is present. No slots.")
            else:
                print("No active slots found on current view.")

        except Exception as e:
            print(f"::error:: Script failed: {e}")
            sys.exit(1)
        finally:
            browser.close()


if __name__ == "__main__":
    if not TARGET_URL:
        print("Error: TARGET_URL environment variable is missing.")
        sys.exit(1)
    check_availability()
