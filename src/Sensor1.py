from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
import requests
import json
from datetime import datetime
import random





app = Flask(__name__)

async def post_data(sensor_id:int):
    url = "http://127.0.0.1:5000/api/soil_data"

    payload = json.dumps({
        "sensor_id": sensor_id,
        "temperature": random.uniform(-15.0,45.0),
        "humidity": random.randint(0,1023),
        "pH": random.uniform(0.0,14.0),
        "ir": random.randint(0,100),
        "vis": random.uniform(400.0,700.0),
        "battery": random.randint(0,100),
        "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    headers = {
        'Content-Type': 'application/json'
    }

    requests.request("POST", url, headers=headers, data=payload)


def scheduled_task(sensor_id:int):
    asyncio.run(post_data(sensor_id))


def start_sensor(sensor_id:int):
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_task, "interval", minutes=2, args=[sensor_id])
    scheduler.start()
    return 

@app.before_request

def init_scheduler():
    start_sensor(sensor_id=1)
    start_sensor(sensor_id=2)
    start_sensor(sensor_id=3)

@app.route("/api/sensor/start")

def home():
    return "sensor started"



if __name__=="__main__":
    app.run(debug=True, port=5001)