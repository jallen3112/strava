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

load_dotenv()
CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
TOKEN_URL = "https://www.strava.com/oauth/token"
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")

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
        self.activities = self.get_recent_activities()
        self.polyline_list = self.extract_polylines_list()

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

    def get_recent_activities(self, page: int = 1, per_page: int = 40) -> pd.DataFrame:
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




    def plot_polyline(self, map_filename='single_route_map.html'):
        # Decode the polyline into (lat, lon) tuples
        coords = polyline.decode(self.polyline_list[0])

        # Center map on first coordinate
        m = folium.Map(location=coords[0], zoom_start=14)

        # Add line to map
        folium.PolyLine(coords, color="blue", weight=5, opacity=0.7).add_to(m)

        # Save to HTML file
        m.save(map_filename)
        print(f"Map saved to {map_filename}")

    def extract_polylines_list(self):
        df = self.activities
        polyline_list = df['map_summary_polyline'].dropna().tolist()
        return polyline_list


    def plot_multiple_routes(self, output_html='routes_map.html', output_image='routes_map.png', mapbox_style='satellite-streets'):
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
        for i, encoded in enumerate(self.polyline_list):
            try:
                coords = polyline.decode(encoded)
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

    def plot_single_routes(self, output_html='routes_map.html', output_image='single_routes_map.png', mapbox_style='satellite-streets'):
        
        with open('bennevis.gpx', 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)

        coords =[]
        for route in gpx.routes:
            for point in route.points:
                coords.append((point.latitude, point.longitude))

        encoded = polyline.encode(coords)
        
        df = pd.DataFrame(coords, columns=["lat", "lon"])
        df["route_id"] = "Ben Nevis Route"
        px.set_mapbox_access_token(MAPBOX_TOKEN)
        # Plot on Mapbox
        fig = px.line_mapbox(
            df,
            lat="lat",
            lon="lon",
            color="route_id",
            zoom=13,
            height=600,
            mapbox_style=mapbox_style,  # good for elevation/terrain
        )

        fig.update_layout(
            mapbox=dict(
                center={"lat": df["lat"].mean(), "lon": df["lon"].mean()},
                pitch=80, bearing=55
            ),
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            showlegend=False,
        )

        # Export
        fig.write_html(output_html)
        fig.write_image(output_image)
        print(f"Map saved to {output_html} and image saved to {output_image}")

    def extract_polylines_list(self):
        df = self.activities
        polyline_list = df['map_summary_polyline'].dropna().tolist()
        return polyline_list

    def plot_single_routes3d(self, output_html='3dsat_routes_map.html', mapbox_token=MAPBOX_TOKEN):
        with open('bennevis.gpx', 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)

        coords = []
        for route in gpx.routes:
            for point in route.points:
                coords.append((point.latitude, point.longitude))

        if not coords:
            raise ValueError("No route points found.")

        # Format for JavaScript
        coordinates_js = [[lon, lat] for lat, lon in coords]  # [lon, lat] for GeoJSON

        # HTML with Mapbox GL JS
        html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <title>3D Ben Nevis Terrain</title>
        <meta name="viewport" content="initial-scale=1,maximum-scale=1,user-scalable=no" />
        <script src="https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.js"></script>
        <link href="https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.css" rel="stylesheet" />
        <style>
            body {{ margin:0; padding:0; }}
            #map {{ position:absolute; top:0; bottom:0; width:100%; }}
        </style>
    </head>
    <body>
    <div id="map"></div>
    <script>
        mapboxgl.accessToken = '{mapbox_token}';
        const map = new mapboxgl.Map({{
            container: 'map',
            style: 'mapbox://styles/mapbox/satellite-streets-v12',
            center: [{coordinates_js[0][0]}, {coordinates_js[0][1]}],
            zoom: 13,
            pitch: 60,
            bearing: 55,
            antialias: true
        }});

        map.on('load', () => {{
            map.addSource('mapbox-dem', {{
                "type": "raster-dem",
                "url": "mapbox://mapbox.terrain-rgb",
                "tileSize": 512,
                "maxzoom": 14
            }});

            map.setTerrain({{ "source": "mapbox-dem", "exaggeration": 1.6 }});

            map.addLayer({{
                "id": "route",
                "type": "line",
                "source": {{
                    "type": "geojson",
                    "data": {{
                        "type": "Feature",
                        "geometry": {{
                            "type": "LineString",
                            "coordinates": {coordinates_js}
                        }}
                    }}
                }},
                "layout": {{
                    "line-join": "round",
                    "line-cap": "round"
                }},
                "paint": {{
                    "line-color": "#ff6f61",
                    "line-width": 4
                }}
            }});
        }});
    </script>
    </body>
    </html>
    """

        with open(output_html, 'w') as f:
            f.write(html_content)

        print(f"✅ 3D terrain map with route written to: {output_html}")

if __name__ == "__main__":
    strava_manager = StravaApiManager()
    strava_manager.plot_single_routes3d()
    
    #auth_manager = StravaAuthManager(CLIENT_ID, CLIENT_SECRET, TOKEN_URL)
    #access_token = auth_manager.get_valid_access_token()





