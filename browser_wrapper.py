from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import WebDriverException

from urllib.parse import quote
from urllib.parse import urlparse

import time

class BrowserWrapper:
    """
    This is a slightly evil way to automate OAuth, using headless Firefox.
    Note that this currently requires geckodriver to be in the path (see README)
    """
    def __init__(self):
        options = Options()
        options.headless = True
        options.add_argument('-headless')
        self.driver = Firefox(executable_path='geckodriver', options=options)

    def authorize(self, url, email):
        driver = self.driver
        wait = WebDriverWait(driver, timeout=10)
        driver.get(url)
        
        # Login with account and password
        wait.until(expected.visibility_of_element_located((By.CSS_SELECTOR, '#email-input input'))).send_keys(email)
        wait.until(expected.visibility_of_element_located((By.CSS_SELECTOR, '#password-input input'))).send_keys(password + Keys.ENTER)

        driver.save_screenshot('screen_allow.png')

        wait.until(expected.visibility_of_element_located((By.CSS_SELECTOR, '#selectAllScope'))).click()

        try:
            wait.until(expected.visibility_of_element_located((By.CSS_SELECTOR, '#allow-button'))).click()
        except WebDriverException as e:
            # We got redirected to localhost:8080, which should throw an exception.
            # Now we have to just pass back the path we got sent to, which the
            # fitbit API will use to finalize the token. Yay?
            auth_url = driver.current_url
            print(auth_url)
            return auth_url

        driver.save_screenshot('screen_end.png')
        raise Exception("No OAuth code found, please see screen_end.png")

