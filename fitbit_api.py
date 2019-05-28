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

class FitbitApi:
    def __init__(self, account_email, client_id, client_secret):
        if "@" not in account_email:
            raise ValueError(account_email + ' does not look like an email')
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
            self.api = OAuth2Session(client_id=self.client_id, redirect_uri=self.redirect_uri, scope=self.scope)
            authorization_url, state = self.api.authorization_url(self.auth_url)

            print('Please go to %s and authorize access.' % authorization_url)
            authorization_response = input('Enter the full callback URL: ')

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
        self.token = self.api.refresh_token(self.token_url, refresh_token=self.refresh_token(), auth=self.auth)
        self.dump_token()

    def sleep(self):
        return self.get('/user/-/sleep/goal.json')

    def date_string(self, date):
        if isinstance(date, datetime):
            return date.date().isoformat()
        elif isinstance(date, date):
            return date.isoformat()
        else:
            return date

    def day_activities(self, date):
        return self.get(f'/user/-/activities/date/{self.date_string(date)}.json')

    def activities(self, date):
        return self.get(f'/user/-/activities/list.json?beforeDate={self.date_string(date)}&offset=0&limit=20&sort=desc')

    def hrv(self, date):
        return self.get(f'/user/-/activities/heart/date/{self.date_string(date)}/1d/1sec.json')

    def get(self, path):
        # It would sure be nice to use requests-oauthlib's automatic token refresh callbacks!
        # But that doesn't work because Fitbit requires auth. So we need to catch TokenExpiredError
        # and bounce if needed
        try:
            r = self.api.get(self.url + path)
            if r.ok:
                return r.json()
            else:
                logging.error(f"Fitbit API error fetching {self.url + path}: {repr(r.text)}")
        except TokenExpiredError as e:
            logging.error("Unexpected error:", sys.exc_info()[0])
            self.do_refresh_token()
            self.load_api()
        return self.api.get(self.url + path).json()


