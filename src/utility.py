import os
import sys
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from logger import logger


load_dotenv()


def get_config_path():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_dir = os.path.join(root_dir, 'config')
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, 'state.json')


def send_alert_email():
    logger.info('Initiating email alert sequence...')

    sender_email = os.getenv('ALERT_EMAIL_SENDER')
    sender_password = os.getenv('ALERT_EMAIL_PASSWORD')
    receiver_email = os.getenv('ALERT_EMAIL_RECEIVER')

    if not all([sender_email, sender_password, receiver_email]):
        logger.error('Email credentials missing in .env. Cannot send alert.')
        return

    msg = MIMEText(
        'The Snkrdunk authentication token (state.json) is missing or expired. '
        'Please run the local token generator on your laptop to push a fresh '
        'token via SCP.'
    )
    msg['Subject'] = 'CRITICAL: Pokemon Index Auth Failed'
    msg['From'] = str(sender_email)
    msg['To'] = str(receiver_email)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(str(sender_email), str(sender_password))
            server.send_message(msg)
        logger.info('Alert email sent successfully.')
    except smtplib.SMTPException as e:
        logger.error(f'SMTP error occurred while sending email: {e}')
    except Exception as e:
        logger.error(f'Unexpected error while sending email: {e}')


def ensure_log_in(playwright):
    state_file = get_config_path()

    if not os.path.exists(state_file):
        logger.error(f'state.json not found at {state_file}.')
        send_alert_email()
        sys.exit('Pipeline halted due to missing authentication token.')

    logger.info('Token found. Launching browser to actively verify session validity...')

    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        storage_state=state_file,
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )

    # Open a temporary page just to verify the session
    verify_page = context.new_page()

    try:
        verify_page.goto('https://snkrdunk.com/en/')

        # Look for a login link (if we are logged out, this will be visible)
        needs_login = verify_page.locator("a[href*='login']").is_visible()

        if needs_login:
            logger.error('Session expired. The website is requesting a login.')
            browser.close()
            os.remove(state_file)
            send_alert_email()
            sys.exit('Pipeline halted due to expired authentication token.')

        logger.info('Session validation passed. You are good to go.')

        # Close the verification tab to keep the context clean for the scraper
        verify_page.close()

        return browser, context

    except Exception as e:
        logger.error(f'Error occurred during session verification: {e}')
        browser.close()
        sys.exit('Pipeline halted due to unexpected browser error.')

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    ensure_log_in(p)

