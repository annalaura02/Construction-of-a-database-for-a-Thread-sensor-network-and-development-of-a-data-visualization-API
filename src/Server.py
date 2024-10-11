from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import json


app = Flask(__name__)


class SensorData():
    def __init__(self, row, fields:set):
        print(row)
        index=0
        if "sensor_id" in fields:
            self.sensor=int(row[index])
            index+=1
        else:
            self.sensor = None
        if "created_at" in fields:
            self.created_at=datetime.strptime(str(row[index]), '%Y-%m-%d %H:%M:%S')
            index+=1
        else:
            self.created_at = None
        if "temperature" in fields:
            self.temperature=float(row[index])
            index+=1
        else:
            self.temperature = None
        if "humidity" in fields:
            self.humidity=int(row[index])
            index+=1
        else:
            self.humidity = None
        if "pH" in fields:
            self.pH=float(row[index])
            index+=1
        else:
            self.pH=None
        if "ir" in fields:
            self.ir=float(row[index])
            index+=1
        else:
            self.ir = None
        if "vis" in fields:
            self.vis=int(row[index])
            index+=1
        else:
            self.vis = None
        if "battery" in fields:
            self.battery=int(row[index])
            index+=1
        else:
            self.battery = None
    
    def __repr__(self) -> str:
        return f"""
        sensor:{str(self.sensor)}, temperature:{str(self.temperature)}, humidity:{str(self.humidity)}, pH:{str(self.pH)}, 
        ir:{str(self.ir)}, vis:{self.vis}, battery:{str(self.battery)}, created_at:{str(self.created_at)}
        """
    


class Plant():
    def __init__(self, row):
        print(row)
        self.id=int(row[0])
        self.title=str(row[1])
        self.soil=str(row[2])
        self.temp_min=float(row[3])
        self.temp_max=float(row[4])
        self.pH_min=float(row[5])
        self.pH_max=float(row[6])
  
    
    def __repr__(self) -> str:
        return f"""
        id:{self.id}, title:{self.title}, soil:{self.soil}, temp_min:{str(self.temp_min)}, temp_max:{str(self.temp_max)}, 
        pH_min:{str(self.pH_min)}, pH_max:{str(self.pH_max)}
        """
    

class Sensor():
    def __init__(self, row):
        print(row)
        self.id=int(row[0])
        self.lat=float(row[1])
        self.long=float(row[2])
        
  
    
    def __repr__(self) -> str:
        return f"""
        id:{self.id}, lat:{self.lat}, long:{self.long}
        """
    


@app.route("/api/soil_data", methods=["POST"])
def add_data():
    new_data=request.get_json()
    conn_ok, connection = check_conn()
    if conn_ok:
        if insert_data(connection, new_data):
            return jsonify({"status": "OK"}), 201
        else:
            return jsonify({"error" : "error during insertion"}), 500
        
    else:
        return jsonify({"error" : "error during connection"}), 500



@app.route("/api/test_conn", methods=["GET"])

def test_conn():
    try: 
        connection = mysql.connector.connect(
            host = "127.0.0.1",
            database = "tesi",
            user = "root",
            password = "MySQLpassw02@"
        )
        if connection.is_connected():
            return jsonify({"status": "OK"}), 200
        else:
            return jsonify({"status": "NO"}), 200
    except Error as e:
        return jsonify({"error": e.msg})

def check_conn():
    try: 
        connection = mysql.connector.connect(
            host = "127.0.0.1",
            database = "tesi",
            user = "root",
            password = "MySQLpassw02@"
        )
        if connection.is_connected():
            return True, connection
        else:
            return False, None
    except Error as e:
        return False, None


def insert_data(connection, new_data):
    try:
        cursor=connection.cursor()
        query = f"INSERT INTO soil_data (sensor_id, temperature, humidity, pH, ir, vis, battery, created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
        values=(new_data['sensor_id'],new_data['temperature'],new_data['humidity'],new_data['pH'],new_data['ir'],new_data['vis'],new_data['battery'], new_data['created_at'])
        cursor.execute(query,values)
        connection.commit()
        return True
    except Exception as e:
        print(e)
        return False
        

@app.route('/api/visualize', methods=['GET'])

def visualize():
    sensors=request.args.getlist('sensors')
    fields=request.args.getlist('fields')
    date_start_str=request.args.get('date_start')
    date_end_str=request.args.get('date_end')
    try:
        date_start=datetime.fromisoformat(date_start_str)
        date_end=datetime.fromisoformat(date_end_str)
        sensors_list=list(sensors)
        fields_list=list(fields)
        fields_list.insert(0, "sensor_id")
        fields_list.insert(1, "created_at")
        print(sensors_list)
        
        conn_ok, connection = check_conn()
        if conn_ok:
            sensors_list = ", ".join(str(sensor) for sensor in sensors_list) 
            fields_list = ", ".join(fields_list)

            cursor=connection.cursor()
            query = f"""
            SELECT {fields_list}
            FROM soil_data 
            WHERE sensor_id IN ({sensors_list})
            AND created_at BETWEEN %s AND %s
            """
            values = (date_start, date_end)
            print(query)
            cursor.execute(query, values)
            results = cursor.fetchall()
            connection.commit()
            return [SensorData(row, fields_list).__dict__ for row in results], 200


    except Exception as e:
        print(e)
        return jsonify({"error": e.msg}), 500
    

@app.route('/api/average', methods=['GET'])

def get_avg():
    sensor=request.args.get('sensor')
    date_start_str=request.args.get('date_start')
    date_end_str=request.args.get('date_end')
    try:
        date_start=datetime.fromisoformat(date_start_str)
        date_end=datetime.fromisoformat(date_end_str)
        conn_ok, connection = check_conn()
        if conn_ok:

            cursor=connection.cursor()
            query = f"""
            SELECT AVG(temperature), AVG(pH)
            FROM soil_data 
            WHERE sensor_id={int(sensor)}
            AND created_at BETWEEN %s AND %s
            """
            values = (date_start, date_end)
            print(query)
            cursor.execute(query, values)
            results = cursor.fetchall()
            connection.commit()
            return [SensorData(row, ["temperature", "pH"]).__dict__ for row in results], 200


    except Exception as e:
        print(e)
        return jsonify({"error": e.msg}), 500
    



@app.route('/api/get_last', methods=['GET'])

def get_last():
    try:
        conn_ok, connection = check_conn()
        if conn_ok:
            cursor=connection.cursor()
            query = f"""
            SELECT sensor_id, created_at, temperature, humidity, pH, ir, vis, battery
            FROM soil_data AS t1
            WHERE created_at = (
                SELECT MAX(t2.created_at)
                FROM soil_data AS t2 
                WHERE t2.sensor_id = t1.sensor_id
            ) 
            AND sensor_id IN (1, 2, 3)
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            connection.commit()
            fields_list=["sensor_id", "created_at", "temperature", "humidity", "pH", "ir", "vis", "battery"]
            return [SensorData(row, fields_list).__dict__ for row in results], 200


    except Exception as e:
        print(e)
        return jsonify({"error": e.msg}), 500
        


@app.route('/api/plants', methods=['GET'])
def get_plants():
    try:
        conn_ok, connection = check_conn()
        if conn_ok:
            cursor=connection.cursor()
            query = f"""
            SELECT *
            FROM plants 
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            connection.commit()
            
            return [Plant(row).__dict__ for row in results], 200


    except Exception as e:
        print(e)
        return jsonify({"error": e.msg}), 500


@app.route('/api/sensors', methods=['GET'])
def get_sensors():
    try:
        conn_ok, connection = check_conn()
        if conn_ok:
            cursor=connection.cursor()
            query = f"""
            SELECT *
            FROM sensors 
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            connection.commit()
            
            return [Sensor(row).__dict__ for row in results], 200


    except Exception as e:
        print(e)
        return jsonify({"error": e.msg}), 500


@app.route('/api/plants', methods=['POST'])
def add_plant():
    try:
        conn_ok, connection = check_conn()
        if conn_ok:
            new_data=request.get_json()
            cursor=connection.cursor()
            query = f"INSERT INTO plants (title, soil, temp_min, temp_max, pH_min, pH_max) VALUES (%s,%s,%s,%s,%s,%s)"
            
            values=(new_data['title'],new_data['soil'],new_data['temp_min'],new_data['temp_max'],new_data['pH_min'],new_data['pH_max'])
            cursor.execute(query,values)
            connection.commit()
            
            return jsonify({"status": "OK"}), 201


    except Exception as e:
        print(e)
        return jsonify({"error": e.msg}), 500

if __name__=="__main__":
    app.run(debug=True, port=5000)


