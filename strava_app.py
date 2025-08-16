import os
import sys
from dotenv import load_dotenv
sys.path.append("C:/Users/44756/OneDrive/Documents/personal_projects/strava/generated-python-strava")
from swagger_client import Configuration
from authentication import StravaAuthManager
from api_manager import StravaApiManager
from polyline_mapper import MapGenerator



load_dotenv()
CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
TOKEN_URL = "https://www.strava.com/oauth/token"
ACTIVITY_NAME = 'Morning Park Run'
OUTPUT_FILENAME = 'test_file.html'
OUTPUT_FILE_TITLE = ACTIVITY_NAME.replace(' ', '_')

if __name__ == "__main__":
    #Generate new refresh token if expired and configure the api manager
    auth_manager = StravaAuthManager(CLIENT_ID, CLIENT_SECRET, TOKEN_URL)
    access_token = auth_manager.get_valid_access_token()
    configuration = Configuration()
    configuration.access_token = access_token

    #Retreive desired activites json and extract into activity class
    strava_manager = StravaApiManager(configuration)
    activities = strava_manager.get_activity_by_name(ACTIVITY_NAME)

    #Generate 3d map with polyline
    map_generator = MapGenerator(activities)
    map_generator.plot_single_route3d(OUTPUT_FILENAME, OUTPUT_FILE_TITLE)
    







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