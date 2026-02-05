import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry
import json
import ipinfo
import webview
import os
from dotenv import load_dotenv, dotenv_values
from datetime import datetime

now = datetime.now()

if now.hour < 12:
    greeting = "Good Morning"
elif 12 <= now.hour < 18:
    greeting = "Good Afternoon"
else:
    greeting = "Good Evening"

load_dotenv()
print("env code:" + os.getenv("IPINFO_TOKEN"))

# ipinfo
handler = ipinfo.getHandler(access_token=os.getenv("IPINFO_TOKEN")) # Add ipinfo token here
details = handler.getDetails()

longitude = details.longitude
latitude = details.latitude

# Test location details
print(f"Detected location: {details.city}, {details.region}, {details.country}")


# Test coordinates for Florida, USA
florida_latitude = 27.9944024
florida_longitude = -81.7602544

# Test coordinates for Ottawa, Canada
ottawa_latitude = 45.4215
ottawa_longitude = -75.6990

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude":  {latitude},
	"longitude": {longitude},
	"hourly": "temperature_2m",
	"current": ["temperature_2m", "apparent_temperature", "weather_code"]
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation: {response.Elevation()} m asl")
print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# Get current weather
current = response.Current()
current_temp = round(current.Variables(0).Value())
feels_like = round(current.Variables(1).Value())
weather_code = int(current.Variables(2).Value())

# Map weather codes to Lucide icons
def get_weather_icon(code):
    if code == 0:
        return "sun"  # Clear sky
    elif code in [1, 2]:
        return "cloud-sun"  # Partly cloudy
    elif code == 3:
        return "cloud"  # Overcast
    elif code in [45, 48]:
        return "cloud-fog"  # Fog
    elif code in [51, 53, 55, 56, 57]:
        return "cloud-drizzle"  # Drizzle
    elif code in [61, 63, 65, 66, 67]:
        return "cloud-rain"  # Rain
    elif code in [71, 73, 75, 77]:
        return "snowflake"  # Snow
    elif code in [80, 81, 82]:
        return "cloud-rain-wind"  # Rain showers
    elif code in [85, 86]:
        return "cloud-snow"  # Snow showers
    elif code in [95, 96, 99]:
        return "cloud-lightning"  # Thunderstorm
    else:
        return "cloudy"  # Default

weather_icon = get_weather_icon(weather_code)

# Process hourly data. The order of variables needs to be the same as requested | Note: only temperature_2m is requested here, rest is for testing purposes
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

hourly_data["temperature_2m"] = hourly_temperature_2m

hourly_dataframe = pd.DataFrame(data = hourly_data)
#print("\nHourly data\n", hourly_dataframe)

# Create HTML content with weather data
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Better Weather</title>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
       * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
       }}
       html, body {{
            width: 100%;
            height: 100%;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            overflow: hidden;
            background: transparent;
       }}
       .container{{
            background:#1a1a1a;
            width: 100%;
            height: 100%;
            border-radius: 10px;
            display: grid;
            grid-template-columns: auto 1fr auto;
            gap: 2px;
            text-align: center;
            color: white;
            padding: 10px 15px;
       }}
       .greeting {{
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 0;
            opacity: 0.95;
       }}
       .temperature {{
            font-size: 48px;
            font-weight: 700;
            line-height: 1;
            margin: 0;
            display: flex;
            align-items: center;
            justify-content: center;
       }}
       .feels-like {{
            font-size: 14px;
            font-weight: 400;
            opacity: 0.9;
       }}
    </style>
</head>
<body>
    <div class="container">
        <div class="greeting">{greeting}<br><i data-lucide="{weather_icon}" style="width: 20px; height: 20px;"></i></div>
        <div class="temperature">{current_temp}°C</div>
        <div class="feels-like">Feels like {feels_like}°C</div>
    </div>
    <script>lucide.createIcons();</script>
</body>
</html>
"""

# Create and start the GUI window
webview.create_window('Better Weather', html=html_content, width=300, height=150, frameless=True, on_top=True)
webview.start()