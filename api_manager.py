import sys
from datetime import datetime

sys.path.append("C:/Users/44756/OneDrive/Documents/personal_projects/strava/generated-python-strava")

from swagger_client import ApiClient, ActivitiesApi
from swagger_client.rest import ApiException

class StravaActivity:

    '''Represents a Strava activity with detailed metrics and attributes.'''
    
    def __init__(self, activity: list['SummaryActivity']):
        '''
        Initializes a StravaActivity object from a SummaryActivity instance.

        Args:
            activity (SummaryActivity): A Strava SummaryActivity object from which
                to extract all relevant metrics and attributes.
        '''
       
        self.achievement_count = activity.achievement_count
        self.athlete_id = getattr(activity.athlete, 'id', None)
        self.athlete_count = activity.athlete_count
        self.average_speed = activity.average_speed
        self.average_watts = activity.average_watts
        self.comment_count = activity.comment_count
        self.commute = activity.commute
        self.device_watts = activity.device_watts
        self.distance = activity.distance
        self.elapsed_time = activity.elapsed_time
        self.elev_high = activity.elev_high
        self.elev_low = activity.elev_low
        self.end_lat = activity.end_latlng[0] if activity.end_latlng else None
        self.end_lng = activity.end_latlng[1] if activity.end_latlng else None
        self.external_id = activity.external_id
        self.flagged = activity.flagged
        self.gear_id = activity.gear_id
        self.has_kudoed = activity.has_kudoed
        self.hide_from_home = activity.hide_from_home
        self.kilojoules = activity.kilojoules
        self.kudos_count = activity.kudos_count
        self.manual = activity.manual
        self.map_id = getattr(activity.map, 'id', None)
        self.map_polyline = getattr(activity.map, 'polyline', None)
        self.map_summary_polyline = getattr(activity.map, 'summary_polyline', None)
        self.max_speed = activity.max_speed
        self.max_watts = activity.max_watts
        self.moving_time = activity.moving_time
        self.name = activity.name
        self.photo_count = activity.photo_count
        self.private = activity.private
        self.sport_type = activity.sport_type
        self.start_date = activity.start_date.isoformat() if isinstance(activity.start_date, datetime) else activity.start_date
        self.start_date_local = activity.start_date_local.isoformat() if isinstance(activity.start_date_local, datetime) else activity.start_date_local
        self.start_lat = activity.start_latlng[0] if activity.start_latlng else None
        self.start_lng = activity.start_latlng[1] if activity.start_latlng else None
        self.timezone = activity.timezone
        self.total_elevation_gain = activity.total_elevation_gain
        self.total_photo_count = activity.total_photo_count
        self.trainer = activity.trainer
        self.type = activity.type
        self.upload_id = activity.upload_id
        self.upload_id_str = activity.upload_id_str
        self.weighted_average_watts = activity.weighted_average_watts
        self.workout_type = activity.workout_type

        


class StravaApiManager:
    """
    A manager class for interacting with the Strava API using authenticated requests.

    This class handles:
    - Authentication via StravaAuthManager
    - Configuration of the API client
    - Fetching recent athlete activities
    - Retrieving route data by route ID
    """

    def __init__(self, configuration):
        """
        Initializes the StravaApiManager by setting up API client instances.

        Sets up:
        - ActivitiesApi and RoutesApi instances
        """
        self.configuration = configuration
        self.api_client = ApiClient(self.configuration)
        self.activities_api = ActivitiesApi(self.api_client)
        



    def get_recent_activities(self, page: int = 1, per_page: int = 40) -> list[StravaActivity]:
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
        extracted_activities = []
        try:
            activity_list = self.activities_api.get_logged_in_athlete_activities(page=page, per_page=per_page)
        except ApiException as e:
            print(f"Exception when calling ActivitiesApi->get_logged_in_athlete_activities: {e}")

        for activity in activity_list:
            extracted_activities.append(StravaActivity(activity))

        return extracted_activities


    def get_activity_by_name(self, target_name, per_page=50):
        """
        Search for an activity by name across all Strava history.
        Stops when no more activities are returned.
        """
        page = 1
        while True:
            activities = self.activities_api.get_logged_in_athlete_activities(page=page, per_page=per_page)

            if not activities:  # No more activities returned
                break

            for activity in activities:
                if activity.name == target_name:
                    print(f"Found target activity:'{target_name}'")
                    return [StravaActivity(activity)]

            page += 1

        print(f"Activity '{target_name}' not found.")