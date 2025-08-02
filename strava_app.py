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
import pandas as pd
from datetime import datetime
import folium
import polyline
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


    def flatten_activities(self, activities: list['SummaryActivity']) -> pd.DataFrame:
        """
        Flattens a list of Strava SummaryActivity objects into a pandas DataFrame.

        Args:
            activities (List): A list of SummaryActivity objects returned by the Strava API.

        Returns:
            pd.DataFrame: A DataFrame with one row per activity, with key fields extracted.
        """
        flattened = []

        for activity in activities:
            flat = {
                'achievement_count': activity.achievement_count,
                'athlete_id': getattr(activity.athlete, 'id', None),
                'athlete_count': activity.athlete_count,
                'average_speed': activity.average_speed,
                'average_watts': activity.average_watts,
                'comment_count': activity.comment_count,
                'commute': activity.commute,
                'device_watts': activity.device_watts,
                'distance': activity.distance,
                'elapsed_time': activity.elapsed_time,
                'elev_high': activity.elev_high,
                'elev_low': activity.elev_low,
                'end_lat': activity.end_latlng[0] if activity.end_latlng else None,
                'end_lng': activity.end_latlng[1] if activity.end_latlng else None,
                'external_id': activity.external_id,
                'flagged': activity.flagged,
                'gear_id': activity.gear_id,
                'has_kudoed': activity.has_kudoed,
                'hide_from_home': activity.hide_from_home,
                'kilojoules': activity.kilojoules,
                'kudos_count': activity.kudos_count,
                'manual': activity.manual,
                'map_id': getattr(activity.map, 'id', None),
                'map_polyline': getattr(activity.map, 'polyline', None),
                'map_summary_polyline': getattr(activity.map, 'summary_polyline', None),
                'max_speed': activity.max_speed,
                'max_watts': activity.max_watts,
                'moving_time': activity.moving_time,
                'name': activity.name,
                'photo_count': activity.photo_count,
                'private': activity.private,
                'sport_type': activity.sport_type,
                'start_date': activity.start_date.isoformat() if isinstance(activity.start_date, datetime) else activity.start_date,
                'start_date_local': activity.start_date_local.isoformat() if isinstance(activity.start_date_local, datetime) else activity.start_date_local,
                'start_lat': activity.start_latlng[0] if activity.start_latlng else None,
                'start_lng': activity.start_latlng[1] if activity.start_latlng else None,
                'timezone': activity.timezone,
                'total_elevation_gain': activity.total_elevation_gain,
                'total_photo_count': activity.total_photo_count,
                'trainer': activity.trainer,
                'type': activity.type,
                'upload_id': activity.upload_id,
                'upload_id_str': activity.upload_id_str,
                'weighted_average_watts': activity.weighted_average_watts,
                'workout_type': activity.workout_type,
            }

            flattened.append(flat)

        return pd.DataFrame(flattened)

    def get_recent_activities(self, page: int = 1, per_page: int = 10) -> pd.DataFrame:
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
            activities = self.activities_api.get_logged_in_athlete_activities(page=page, per_page=per_page)
            df = self.flatten_activities(activities)
            print(df)
            return df
        except ApiException as e:
            print(f"Exception when calling ActivitiesApi->get_logged_in_athlete_activities: {e}")




    def plot_polyline(self, map_filename='route_map.html'):
        # Decode the polyline into (lat, lon) tuples
        coords = polyline.decode('azg~H~f_@@a@IQAI?g@Dm@Ek@KSECWDUAWDKAGA]Se@FIDOCEGcAGOIQ@IEMAMEKASIQCKI[A]MOOMGUCWSG?kAo@i@c@G@Y[YSa@s@M?KC}AkAKAy@_@SUOGOSIGIS?KBYDK?o@BMDE@s@Tu@Ay@D{@CMIGE_@w@a@[_@GCWYe@_@OSI?_@OSSIAEIMA[KOOGMABBFNJTHJHNBBHDDh@XLNNFh@f@F@JNRJF?`@^NFNPLHGG[_@WOCIQMCI[K]_@IAGGICCG[O[MOe@EFQBACYOKMAIE@JTPHD?FJZFXLHJPJr@p@\\VDBPTD@@A^XD?b@\\HBHLAKEAEEa@UMSOG]YGAMUYMYIKOOMc@KWYi@YOOPRLBDCJLpAbA^JRTDAl@f@FJF@DFHBNLPDPTOMAESIEGi@a@GAGGIEGIKCOSMAU[WMSSC?AGBCCAC@OIG@SI_@SEGABJFXVR\\@HHNLJh@RPXVPl@XBDRNHJHBpA`AATENBXCXENQXALKNEL?RM|@CDG\\A\\BHHRb@b@j@X')

        # Center map on first coordinate
        m = folium.Map(location=coords[0], zoom_start=14)

        # Add line to map
        folium.PolyLine(coords, color="blue", weight=5, opacity=0.7).add_to(m)

        # Save to HTML file
        m.save(map_filename)
        print(f"Map saved to {map_filename}")



if __name__ == "__main__":
    strava_manager = StravaApiManager()
    df = strava_manager.get_recent_activities()
    # df.to_csv('strava_activities.csv')
    strava_manager.plot_polyline()
    
    #auth_manager = StravaAuthManager(CLIENT_ID, CLIENT_SECRET, TOKEN_URL)
    #access_token = auth_manager.get_valid_access_token()


