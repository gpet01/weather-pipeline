import requests
import os
import csv
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

OMW_ENDPOINT = "https://api.openweathermap.org/data/2.5/forecast"
API_KEY = os.getenv("API_KEY")
MY_LAT = 40.511478
MY_LON = 21.679102
CSV_FILE = "weather_log.csv"


parameters = {
    "lat": MY_LAT,
    "lon": MY_LON,
    "appid": API_KEY,
    "cnt": 4,
    "units": "metric"
}

response = requests.get(url=OMW_ENDPOINT, params=parameters)
response.raise_for_status()
weather_data = response.json()

rows = []
for entry in weather_data['list']:
    rows.append({
        "fetched_at": datetime.now().isoformat(),
        "forecast_time": entry["dt_txt"],
        "temp": entry['main']['temp'] ,
        "humidity": entry['main']['humidity'],
        "wind_speed": entry['wind']['speed'],
        "description": entry['weather'][0]['description'],
    })

file_exists = os.path.isfile(CSV_FILE)
with open(CSV_FILE, "a", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    if not file_exists:
        writer.writeheader()
    writer.writerows(rows)
print(f"Saved {len(rows)} forecast rows to {CSV_FILE}")