import os
import requests
import time
import json
from dotenv import load_dotenv

class StravaAuthManager:
    def __init__(self, client_id, client_secret, token_url, token_file="strava_token.json"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.token_file = token_file
        self.tokens = self._load_tokens()

    def _load_tokens(self):
        '''Retreives tokens from local json file'''
        try:
            with open(self.token_file, "r") as f:
                return eval(f.read())
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_tokens(self, tokens):
        with open(self.token_file, "w") as f:
            json.dump(tokens, f)
        self.tokens = tokens

    def _is_token_expired(self):
        expires_at = self.tokens.get("expires_at", 0)
        return time.time() > expires_at

    def refresh_access_token(self):
        print(self.tokens.get('refresh_token'))
        response = requests.post(self.token_url, data={
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self.tokens.get('refresh_token'),
        })

        if response.status_code != 200:
            raise Exception(f"Token refresh failed: {response.text}")

        tokens = response.json()
        self._save_tokens(tokens)

        return tokens['access_token']

    def get_valid_access_token(self):
        if not self.tokens or self._is_token_expired():
            return self.refresh_access_token()
        return self.tokens['access_token']

# Example usage
if __name__ == "__main__":
    load_dotenv()
    CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
    CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
    TOKEN_URL = "https://www.strava.com/oauth/token"

    auth_manager = StravaAuthManager(CLIENT_ID, CLIENT_SECRET, TOKEN_URL)
    access_token = auth_manager.get_valid_access_token()
    print("Valid Access Token:", access_token)

