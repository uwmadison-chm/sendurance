from selenium.webdriver import Firefox, FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.options import Log
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import WebDriverException, TimeoutException
import logging

from urllib.parse import quote
from urllib.parse import urlparse

import time
import os.path
import tempfile
import sys

class BrowserWrapper:
    """
    This is a slightly evil way to automate OAuth, using headless Firefox.
    Note that this requires geckodriver to be in the path or current directory (see README)
    """
    def __init__(self, debug=False):
        options = Options()
        options.headless = True
        self.debug = debug

        geckodriver = './geckodriver'
        if not os.path.exists('./geckodriver'):
            geckodriver = 'geckodriver'
        self.driver = Firefox(executable_path=geckodriver, options=options, service_args=["--marionette-port", "2828", "-vv"])
        self.driver.delete_all_cookies()

    def authorize(self, url, email, password):
        driver = self.driver
        wait = WebDriverWait(driver, timeout=15)
        try:
            logging.info(f"Attempting to authorize at url {url}")
            driver.get(url)
        except WebDriverException as e:
            # If we got redirected to localhost:8080 already, then fitbit thinks we are authenticated
            # We can't just take that because it might be the last user logged in -- somehow??
            auth_url = driver.current_url
            if auth_url.startswith("https://127.0.0.1"):
                logging.warning("Fitbit API thinks we are authenticated, ignoring")
                logging.fatal(f"Instead of getting a login screen, we are redirected to {auth_url}")
                sys.exit()
                # TODO: log out somehow
            else:
                if self.debug:
                    driver.save_screenshot('screen_error.png')
                logging.exception("Unexpected error on load, see screen_error.png")
                sys.exit(1)
        
        # On guero, seems we need to be more patient
        time.sleep(12)

        try:
            # Login with account and password
            if self.debug:
                driver.save_screenshot('screen_start.png')
            wait.until(expected.visibility_of_element_located((By.CSS_SELECTOR, '#email-input input'))).send_keys(email)
            wait.until(expected.visibility_of_element_located((By.CSS_SELECTOR, '#password-input input'))).send_keys(password + Keys.ENTER)

            if self.debug:
                driver.save_screenshot(f'screen_login_{email}.png')

            time.sleep(8)

            wait.until(expected.visibility_of_element_located((By.CSS_SELECTOR, '#selectAllScope'))).click()

        except TimeoutException as e:
            # Timeout means we got sent to the authorization URL, to our localhost that doesn't exist
            auth_url = driver.current_url
            logging.info(f"Got auth_url after timeout {auth_url}")
            driver.save_screenshot('screen_auth_timeout.png')
            return auth_url

        except WebDriverException as e:
            driver.save_screenshot('screen_error.png')
            logging.exception("Unexpected error when logging in, see screen_error.png")
            sys.exit(1)

        try:
            wait.until(expected.visibility_of_element_located((By.CSS_SELECTOR, '#allow-button'))).click()
        except WebDriverException as e:
            # We got redirected to localhost:8080, which should throw an exception.
            # Now we have to just pass back the path we got sent to, which the
            # fitbit API will use to finalize the token. Yay?
            auth_url = driver.current_url
            print(f"Got auth_url after exception {auth_url}")
            driver.save_screenshot('screen_auth_exception.png')
            return auth_url

        driver.save_screenshot('screen_end.png')
        raise Exception("No OAuth code found, please see screen_end.png")

