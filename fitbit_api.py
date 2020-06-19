from oauthlib.oauth2 import BackendApplicationClient
from oauthlib.oauth2.rfc6749.errors import (InsecureTransportError,
                                            TokenExpiredError)
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
from pathlib import Path
from datetime import datetime
import json
import sys
import logging
import os
from browser_wrapper import BrowserWrapper
from IPython import embed

class FitbitApi:
    def __init__(self, account_email, account_password, client_id, client_secret):
        if "@" not in account_email:
            raise ValueError(account_email + ' does not look like an email')
        self.account_email = account_email
        self.client_id = client_id
        self.client_secret = client_secret

        self.scope = ["activity", "heartrate", "location", "nutrition", "profile", "settings", "sleep", "social", "weight"]
        self.redirect_uri = 'https://127.0.0.1:8080/'

        self.token_url = 'https://api.fitbit.com/oauth2/token'
        self.auth_url = 'https://www.fitbit.com/oauth2/authorize'
        self.url = 'https://api.fitbit.com/1'

        # For some dumb reason, Fitbit's api requires you use basic auth headers when fetching a token.
        self.auth = HTTPBasicAuth(self.client_id, self.client_secret)

        self.token_file = Path("tokens/%s.json" % account_email)
        if self.token_file.is_file():
            logging.debug("Loading existing token")
            self.load_token()
            self.load_api()
        else:
            self.api = OAuth2Session(client_id=self.client_id, redirect_uri=self.redirect_uri, scope=self.scope, state=account_email)
            authorization_url, state = self.api.authorization_url(self.auth_url)

            # Using geckobrowser to automate the OAuth dance
            browser = BrowserWrapper()
            logging.info(f"Logging in as {account_email}")
            authorization_response = browser.authorize(authorization_url, account_email, account_password)

            self.token = self.api.fetch_token(token_url=self.token_url, auth=self.auth, authorization_response=authorization_response)
            self.dump_token()

    def load_api(self):
        self.api = OAuth2Session(client_id=self.client_id, token=self.token, scope=self.scope)

    def load_token(self):
        with open(self.token_file) as json_file:
            self.token = json.load(json_file)

    def dump_token(self):
        with open(self.token_file, 'w') as outfile:
            json.dump(self.token, outfile)

    def access_token(self):
        return self.token['access_token']

    def refresh_token(self):
        return self.token['refresh_token']

    def do_refresh_token(self):
        try:
            self.token = self.api.refresh_token(self.token_url, refresh_token=self.refresh_token(), auth=self.auth)
            self.dump_token()
        except:
            logging.exception(f'Error refreshing token for {self.account_email}')
            sys.exit(1)

    def date_string(self, date):
        if isinstance(date, datetime):
            return date.date().isoformat()
        elif isinstance(date, date):
            return date.isoformat()
        else:
            return date

    # A list of all the urls can be found in api.py of the python-fitbit module

    def sleep_goal(self):
        return self.get('/user/-/sleep/goal.json')

    def sleep(self, date):
        return self.get(f'/user/-/sleep/date/{self.date_string(date)}.json')

    def day_activities(self, date):
        return self.intraday_time_series('activities', date)

    def activities(self, date):
        return self.get(f'/user/-/activities/list.json?beforeDate={self.date_string(date)}&offset=0&limit=20&sort=desc')

    def steps(self, date):
        return self.intraday_time_series('activities/tracker/steps', date)

    def inter_steps(self, date1, date2):
        return self.get(f'activities/tracker/steps/date/{self.date_string(date1)}/{self.date_string(date2)}')

    def hrv(self, date):
        return self.intraday_time_series('activities/tracker/heart', date)

    def inter_heartrate(self, date1, date2=None):
        if date2 is None:
            date2 = date1
        results = self.get(f'/user/-/activities/heart/date/{self.date_string(date1)}/{self.date_string(date2)}.json')
        summary = []
        for x in results['activities-heart']:
            heartRate = None
            value = x['value']
            if 'restingHeartRate' in value:
                heartRate = value['restingHeartRate']
            summary.append([x['dateTime'], heartRate])
        return summary

    def intraday_time_series(self, resource, date, detail_level='1min', start_time=None, end_time=None):
        url = f"/user/-/{resource}/date/{self.date_string(date)}/1d/{detail_level}"
        # Check that the time range is valid
        time_test = lambda t: not (t is None or isinstance(t, str) and not t)
        time_map = list(map(time_test, [start_time, end_time]))
        if not all(time_map) and any(time_map):
            raise TypeError('You must provide both the end and start time or neither')

        if all(time_map):
            url = url + '/time'
            for time in [start_time, end_time]:
                time_str = time
                if not isinstance(time_str, str):
                    time_str = time.strftime('%H:%M')
                url = url + ('/%s' % (time_str))

        url = url + '.json'

        return self.get(url)

    def user(self):
        return self.get(f'/user/-/profile.json')

    def get(self, path):
        # It would sure be nice to use requests-oauthlib's automatic token refresh callbacks!
        # But that doesn't work because Fitbit requires auth. So we need to catch TokenExpiredError
        # and bounce if needed
        retries = 0
        while retries < 2:
            try:
                r = self.api.get(self.url + path)
                if r.ok:
                    return r.json()
                else:
                    logging.error(f'Fitbit API error fetching {self.url + path}: {repr(r.text)}')
                    sys.exit(1)
            except TokenExpiredError as e:
                retries = retries + 1
                logging.warning(f"Token expiration, trying #{retries}", sys.exc_info()[0])
                self.do_refresh_token()
                self.load_api()
        logging.error("Token refresh failed!", sys.exc_info()[0])
        sys.exit(1)
