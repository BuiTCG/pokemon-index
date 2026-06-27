"""A python script to be downloaded to a local computer to login to Snkrdunk to get the session information, which will be sent to the server to maintain the log in session."""

import os
import subprocess
import sys

from playwright.sync_api import sync_playwright

SERVER_IP = '1.36.226.51'
SERVER_USER = 'cym'
SERVER_PROD_DIR = '~/Projects/pokemon-index/prod/config/'
LOGIN_URL = 'https://snkrdunk.com/en/login'
SUCCESS_SELECTOR = '.my-account-avatar'


def generate_and_push_token(dir='prod'):
    os.makedirs('config', exist_ok=True)
    local_state_file = os.path.join('config', 'state.json')

    print('Launching browser for manual login...')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto(LOGIN_URL)

        print('Waiting for manual login completion.')

        page.pause()

        context.storage_state(path=local_state_file)
        print(f'Token safely saved to {local_state_file}.')

        browser.close()

    print('Pushing token to the production server via SCP...')

    scp_command = [
        'scp',
        local_state_file,
        f'{SERVER_USER}@{SERVER_IP}:{SERVER_PROD_DIR.replace('prod', dir)}'
    ]

    try:
        subprocess.run(scp_command, check=True)
        print('Success. The production server token has been updated.')
    except subprocess.CalledProcessError as e:
        print(f'SCP transfer failed. Check SSH configuration. Error: {e}')
        sys.exit(1)


    print('Sending remote command to restart the server pipeline...')
    ssh_command = [
        'ssh',
        f'{SERVER_USER}@{SERVER_IP}',
        f'cd ~/Projects/pokemon-index/{dir} && ~/miniconda3/envs/py314/bin/python -m src.indexing'
    ]

    try:
        subprocess.run(ssh_command, check=True)
        print('Pipeline successfully restarted on the server.')
    except Exception as e:
        print(f'Failed to restart pipeline remotely: {e}')
        sys.exit(1)


if __name__ == '__main__':
    dir = 'dev'
    generate_and_push_token(dir=dir)