import os
import requests
import time
import json
from dotenv import load_dotenv

class StravaAuthManager:
    """
    Handles OAuth token management for the Strava API.

    This class manages:
    - Loading and saving access/refresh tokens
    - Refreshing expired tokens
    - Returning a valid access token for authenticated API requests
    """

    def __init__(self, client_id: int, client_secret: str, token_url: str, token_file: str ="strava_token.json"):
        """
        Initializes the authentication manager with credentials and token file location.

        Args:
            client_id (str): Strava API client ID.
            client_secret (str): Strava API client secret.
            token_url (str): The URL endpoint for requesting/refreshing tokens.
            token_file (str): Path to the JSON file storing tokens. Defaults to 'strava_token.json'.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.token_file = token_file
        self.tokens = self._load_tokens()

    def _load_tokens(self) -> dict[str]:
        """
        Loads tokens from the local token file.

        Returns:
            dict: Token dictionary containing at least access_token and refresh_token.
        """
        try:
            with open(self.token_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_tokens(self, tokens) -> dict[str]:
        """
        Saves the token dictionary to the local token file.

        Args:
            tokens (dict): Token dictionary to save.
        """
        with open(self.token_file, "w") as f:
            json.dump(tokens, f)
        self.tokens = tokens

    def _is_token_expired(self) -> bool:
        """
        Checks whether the current access token is expired.

        Returns:
            bool: True if token is expired, False otherwise.
        """
        expires_at = self.tokens.get("expires_at", 0)
        return time.time() > expires_at

    def _refresh_access_token(self) -> str:
        """
        Refreshes the access token using the stored refresh token.

        Returns:
            str: A new valid access token.

        Raises:
            Exception: If the token refresh request fails.
        """
        print(f"Refreshed Access Token: {self.tokens.get('refresh_token')}")
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

    def get_valid_access_token(self) -> str:
        """
        Returns a valid access token, refreshing it if necessary.git 

        Returns:
            str: A valid (refreshed or current) access token.
        """
        if not self.tokens or self._is_token_expired():
            return self._refresh_access_token()
        return self.tokens['access_token']
