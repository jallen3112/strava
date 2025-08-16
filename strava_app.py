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
import polyline
import plotly.express as px
import pandas as pd
import gpxpy
from jinja2 import Environment, FileSystemLoader
import json

load_dotenv()
CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
TOKEN_URL = "https://www.strava.com/oauth/token"
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")



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



class MapGenerator:

    def __init__(self, activities: list[StravaActivity]):
        self.activities = activities


    def plot_multiple_routes_2d(self, output_html='routes_map.html', output_image='routes_map.png', mapbox_style='satellite-streets'):
        """
        Plot multiple encoded polylines on a single interactive map and export as HTML and PNG.

        Parameters:
        - polylines: list of encoded polyline strings
        - output_html: filename to save interactive HTML map (default 'routes_map.html')
        - output_image: filename to save static PNG image (requires kaleido)
        - mapbox_style: map style for background (default 'open-street-map')
        """
        # Collect decoded coordinates into one DataFrame with route ID
        
        all_coords = []
        for i, activity in enumerate(self.activities):
            try:
                coords = polyline.decode(activity.map_summary_polyline)
                df = pd.DataFrame(coords, columns=['lat', 'lon'])
                df['route_id'] = f'Route {i+1}'
                all_coords.append(df)
            except Exception as e:
                print(f"Failed to decode polyline {i}: {e}")

        # Combine all routes
        if not all_coords:
            raise ValueError("No valid polylines to plot.")

        df_all = pd.concat(all_coords, ignore_index=True)
        px.set_mapbox_access_token(MAPBOX_TOKEN)
        # Plot
        fig = px.line_mapbox(
            df_all,
            lat="lat",
            lon="lon",
            color="route_id",
            zoom=11.5,
            mapbox_style=mapbox_style,
            height=600,
            title=None
        )

        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, mapbox={ "pitch": 60, "bearing": 0}, showlegend=False, mapbox_center= {"lat": df_all['lat'].median(), "lon": df_all['lon'].median()})


        # Export
        fig.write_html(output_html)
        fig.write_image(output_image)
        print(f"Map saved to {output_html} and image saved to {output_image}")


    def plot_single_route3d(self, output_filename:str, map_title: str, mapbox_token=MAPBOX_TOKEN, custom_route=False):
        '''Generate a 3D interactive map (HTML file) of a Strava activity route or a custom GPX route using Mapbox GL JS.'''
    
        if custom_route:
            with open(custom_route, 'r') as gpx_file:
                gpx = gpxpy.parse(gpx_file)

            coordinates_js = []
            for route in gpx.routes:
                for point in route.points:
                    coordinates_js.append([point.longitude, point.latitude])

            if not coordinates_js:
                raise ValueError("No route points found.")
            
        else:
            for activity in self.activities:
                try:
                    coords = polyline.decode(activity.map_summary_polyline)
                    coordinates_js = [[lon, lat] for lat, lon in coords]

               
                except Exception as e:
                    print(f"Failed to decode polyline : {e}")
            
         
        
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('3d_map.html')

        lons, lats = zip(*coordinates_js)
        centre = [sum(lons)/len(lons), sum(lats)/len(lats)]
   
      
       

        html = template.render(
            map_title=map_title,
            mapbox_token=mapbox_token,
            centre=centre,
            coordinates_js=coordinates_js)
        
        folder_name = "Map_outputs"

 
        os.makedirs(folder_name, exist_ok=True)

        file_path = os.path.join(folder_name, output_filename)

        with open(file_path, 'w') as f:
            f.write(html)




if __name__ == "__main__":
    strava_manager = StravaApiManager()
    activities = strava_manager.get_activity_by_name('Morning Park Run')
    map_generator = MapGenerator(activities)
    map_generator.plot_single_route3d('test_file.html', 'test')
    







#     <!-- from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from PIL import Image
# import time

# def capture_map_screenshot(html_file, output_image='map_snapshot.png', width=1280, height=800):
#     options = Options()
#     options.headless = True
#     options.add_argument(f"--window-size={width},{height}")

#     driver = webdriver.Chrome(options=options)  # Use Firefox() if using geckodriver
#     driver.get("file://" + html_file)

#     time.sleep(5)  # wait for the map and tiles to fully load

#     screenshot = driver.get_screenshot_as_png()
#     driver.quit()

#     with open(output_image, 'wb') as f:
#         f.write(screenshot)

#     print(f"Saved snapshot to {output_image}") -->