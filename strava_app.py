import sys
sys.path.append("C:/Users/44756/OneDrive/Documents/personal_projects/strava/generated-python-strava")
from swagger_client import Configuration, ApiClient, ActivitiesApi
from swagger_client.api.routes_api import RoutesApi
from swagger_client.rest import ApiException
from pprint import pprint
import polyline



with open("strava_token.json", "r") as f:
            tokens = eval(f.read())
access_token = tokens['access_token']


# Configure API client
configuration = Configuration()
configuration.access_token = access_token
api_client = ApiClient(configuration)

# Create API instance
api_instance = ActivitiesApi(api_client)

# Replace with a real route ID
route_id = 1234567890

try:
    # Call the API
    api_response = api_instance.get_logged_in_athlete_activities(page=1, per_page=5)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling RoutesApi->get_route_by_id: %s\n" % e)

