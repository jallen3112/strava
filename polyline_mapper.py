import sys
import os
import polyline
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
import gpxpy
from jinja2 import Environment, FileSystemLoader
from api_manager import StravaActivity

sys.path.append("C:/Users/44756/OneDrive/Documents/personal_projects/strava/generated-python-strava")

load_dotenv()

MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")


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
