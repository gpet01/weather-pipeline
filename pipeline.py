import os
import requests
import pandas as pd
from datetime import datetime
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp-key.json"

OMW_ENDPOINT = "https://api.openweathermap.org/data/2.5/forecast"
API_KEY = os.getenv("API_KEY")
MY_LAT = 40.511478
MY_LON = 21.679102


PROJECT_ID = os.getenv("PROJECT_ID")
DATASET_ID = os.getenv("DATASET_ID")
TABLE_ID = os.getenv("TABLE_ID")
CSV_FILE = os.getenv("CSV_FILE")

def fetch_weather():
    parameters = {
        "lat": MY_LAT,
        "lon": MY_LON,
        "appid": API_KEY,
        "cnt": 8,
        "units": "metric"
    }

    response = requests.get(url=OMW_ENDPOINT, params=parameters)
    response.raise_for_status()
    return response.json()

def build_rows(weather_data):
    rows = []
    for entry in weather_data['list']:
        rows.append({
            "fetched_at": datetime.now().isoformat(),
            "forecast_time": entry["dt_txt"],
            "temp": entry['main']['temp'],
            "humidity": entry['main']['humidity'],
            "wind_speed": entry['wind']['speed'],
            "description": entry['weather'][0]['description'],
        })
    return rows

def get_existing_forecast_times(client, table_ref, candidate_times):
    if not candidate_times:
        return set()
    times_list = ", ".join(f'"{t}"' for t in candidate_times)
    query = f"""
        SELECT DISTINCT forecast_time
        FROM `{table_ref}`
        WHERE forecast_time IN ({times_list})
    """
    try:
        results = client.query(query).result()
        return {row.forecast_time for row in results}
    except Exception:
        return set()

def load_to_bigquery(rows):
    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    candidate_times = [ r["forecast_time"] for r in rows]
    existing_times = get_existing_forecast_times(client, table_ref, candidate_times)

    new_rows = [r for r in rows if r["forecast_time"] not in existing_times]

    if not new_rows:
        print("No new forecast slows to insert, all are already stored.")
        return

    df = pd.DataFrame(new_rows)
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",
        schema=[
            bigquery.SchemaField("fetched_at", "STRING"),
            bigquery.SchemaField("forecast_time", "STRING"),
            bigquery.SchemaField("temp", "FLOAT"),
            bigquery.SchemaField("humidity", "INTEGER"),
            bigquery.SchemaField("wind_speed", "FLOAT"),
            bigquery.SchemaField("description", "STRING"),
        ],
    )

    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()
    print(f"Loaded {len(df)} rows into {table_ref}")

def main():
    weather_data = fetch_weather()
    rows = build_rows(weather_data)
    load_to_bigquery(rows)

if __name__ == "__main__":
    main()