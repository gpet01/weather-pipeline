import os
from flask import Flask, jsonify, render_template
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp-key.json"

app = Flask(__name__)

PROJECT_ID = os.getenv("PROJECT_ID")
DATASET_ID = os.getenv("DATASET_ID")
TABLE_ID = os.getenv("TABLE_ID")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/weather-data")
def weather_data():
    client = bigquery.Client(project=PROJECT_ID)
    query = f"""
        SELECT fetched_at, forecast_time, temp, humidity, wind_speed, description
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        ORDER BY fetched_at ASC
    """
    results = client.query(query).result()

    data = {
        "labels": [],
        "temp": [],
        "humidity": [],
        "wind_speed": []
    }
    for row in results:
        data["labels"].append(row.forecast_time)
        data["temp"].append(row.temp)
        data["humidity"].append(row.humidity)
        data["wind_speed"].append(row.wind_speed)

    return jsonify(data)

if __name__ == "__main__":
    app.run(
        debug=True,
        port=5001
    )