import sys
import os
sys.path.append("C:/Users/44756/OneDrive/Documents/personal_projects/strava/generated-python-strava")
from swagger_client import Configuration, ApiClient, ActivitiesApi
from swagger_client.api.routes_api import RoutesApi
from swagger_client.rest import ApiException
from pprint import pprint
import polyline
import json
from dotenv import load_dotenv
from token_refresh import StravaAuthManager
load_dotenv()
CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
TOKEN_URL = "https://www.strava.com/oauth/token"


class StravaApiManager:
    """
    A manager class for interacting with the Strava API using authenticated requests.

    This class handles:
    - Authentication via StravaAuthManager
    - Configuration of the API client
    - Fetching recent athlete activities
    - Retrieving route data by route ID
    """

    def __init__(self):
        """
        Initializes the StravaApiManager by setting up authentication and API client instances.

        Requires global variables:
        - CLIENT_ID
        - CLIENT_SECRET
        - TOKEN_URL

        Sets up:
        - Access token via StravaAuthManager
        - API client configuration
        - ActivitiesApi and RoutesApi instances
        """
        self.auth_manager = StravaAuthManager(CLIENT_ID, CLIENT_SECRET, TOKEN_URL)
        self.access_token = self.auth_manager.get_valid_access_token()
        self.configuration = Configuration()
        self.configuration.access_token = self.access_token
        self.api_client = ApiClient(self.configuration)
        self.activities_api = ActivitiesApi(self.api_client)
        self.routes_api = RoutesApi(self.api_client)

    def get_recent_activities(self, page=1, per_page=5):
        """
        Retrieves the authenticated user's most recent activities from Strava.
        Args:
            page (int): Page number of results to fetch. Defaults to 1.
            per_page (int): Number of activities to return per page. Defaults to 5.
        Returns:
            list: A list of activity objects from the Strava API.
        Raises:
            ApiException: If the API request fails.
        """
        try:
            response = self.activities_api.get_logged_in_athlete_activities(page=page, per_page=per_page)
            pprint(response)
            return response
        except ApiException as e:
            print(f"Exception when calling ActivitiesApi->get_logged_in_athlete_activities: {e}")

    def get_route_by_id(self, route_id):
        """
        Fetches a route object from Strava by its ID.
        Args:
            route_id (int): The unique ID of the route to retrieve.
        Returns:
            object: A route object from the Strava API.
        Raises:
            ApiException: If the API request fails.
        """
        try:
            route = self.routes_api.get_route_by_id(route_id)
            pprint(route)
            return route
        except ApiException as e:
            print(f"Exception when calling RoutesApi->get_route_by_id: {e}")


if __name__ == "__main__":
    strava_manager = StravaApiManager()
    strava_manager.get_recent_activities()
    
    # Replace with your real route ID
    # route_id = 1234567890
    # strava_manager.get_route_by_id(route_id)

    #auth_manager = StravaAuthManager(CLIENT_ID, CLIENT_SECRET, TOKEN_URL)
    #access_token = auth_manager.get_valid_access_token()


