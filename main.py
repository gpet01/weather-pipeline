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
    try:
        client = bigquery.Client(project=PROJECT_ID)
        query = f"""
            SELECT fetched_at, forecast_time, temp, humidity, wind_speed, description
            FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
            WHERE CAST(forecast_time AS DATETIME) >= CURRENT_DATETIME()
            ORDER BY forecast_time ASC
            LIMIT 8
        """
        results = list(client.query(query).result())
    except Exception as e:
        print(f"BigQuery query failed: {e}")
        return jsonify({"error": "Failed to fetch weather data"}), 500

    data = {
        "labels": [],
        "temp": [],
        "humidity": [],
        "wind_speed": [],
    }
    for row in results:
        data["labels"].append(row.forecast_time)
        data["temp"].append(row.temp)
        data["humidity"].append(row.humidity)
        data["wind_speed"].append(row.wind_speed)

    # The nearest upcoming slot doubles as "current conditions" for the hero section.
    if results:
        current = results[0]
        data["current"] = {
            "temp": current.temp,
            "humidity": current.humidity,
            "wind_speed": current.wind_speed,
            "description": current.description,
            "forecast_time": current.forecast_time,
        }
    else:
        data["current"] = None

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True, port=5001)