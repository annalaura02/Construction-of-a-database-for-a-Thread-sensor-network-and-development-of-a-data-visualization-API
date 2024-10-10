from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QDateTimeEdit, QPushButton, QTextEdit, QLineEdit, QMessageBox
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import Qt, QDateTime, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
import requests
import matplotlib.pyplot as plt
from datetime import datetime
import json
import folium
from folium import Marker, Map, CustomIcon
import io
import sys
from dateutil.relativedelta import relativedelta 




class SensorData():
    def __init__(self, data, fields:set):
        for key, value in data.items():
            setattr(self, key, self.from_serializable(value))
    def __repr__(self) -> str:
        return f"""
        sensor:{self.sensor}, temperature:{self.temperature}, humidity:{self.humidity}, pH:{self.pH}, ir:{self.ir}, 
        vis:{self.vis}, battery:{self.battery}, created_at:{self.created_at}
        """
    def from_serializable(self, item):
        if isinstance(item, str):
            return datetime.strptime(item, "%a, %d %b %Y %H:%M:%S %Z")
        return item

class Plant():
    def __init__(self, row):
        print(row)
        self.id=int(row["id"])
        self.title=str(row["title"])
        self.soil=str(row["soil"])
        self.temp_min=float(row["temp_min"])
        self.temp_max=float(row["temp_max"])
        self.pH_min=float(row["pH_min"])
        self.pH_max=float(row["pH_max"])
        self.lat=float(0)
        self.long=float(0)
    
    def __repr__(self) -> str:
        return f"""
        id:{self.id}, title:{self.title}, soil:{self.soil}, temp_min:{str(self.temp_min)}, temp_max:{str(self.temp_max)}, 
        pH_min:{str(self.pH_min)}, pH_max:{str(self.pH_max)}, lat:{str(self.lat)}, long:{str(self.long)}
        """
    

class Sensor():
    def __init__(self, row):
        print(row)
        self.id=int(row["id"])
        self.lat=float(row["lat"])
        self.long=float(row["long"])
        self.avg_temp=float(0)
        self.avg_pH=float(0)
        
  
    
    def __repr__(self) -> str:
        return f"""
        id:{self.id}, lat:{self.lat}, long:{self.long}, avg_temp:{self.avg_temp}, avg_ph:{self.avg_pH}
        """

class HomePage(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Soil Conditions')
        self.setGeometry(QGuiApplication.primaryScreen().geometry())
        central_widget=QWidget(self)
        main_layout=QVBoxLayout()
        row1_layout=QHBoxLayout()
        row2_layout=QHBoxLayout()
        self.webview=QWebEngineView()
        layout_col1=self.init_col1()
        layout_col2=self.init_col2()
        layout_col3=self.init_col3()

        row1_layout.addLayout(layout_col1)
        row1_layout.addLayout(layout_col2)
        row1_layout.addLayout(layout_col3)
        main_layout.addLayout(row1_layout)
        self.show_map()
        row2_layout.addWidget(self.webview)
        main_layout.addLayout(row2_layout)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def init_col1(self):
        layout_col1=QVBoxLayout()
        layout_col1.setAlignment(Qt.AlignmentFlag.AlignTop)
        label_col1=QLabel('Select Sensors')
        layout_col1.addWidget(label_col1)
        self.checkbox1_col1=QCheckBox('sensor 1')
        self.checkbox1_col1.setChecked(True)
        layout_col1.addWidget(self.checkbox1_col1)
        self.checkbox2_col1=QCheckBox('sensor 2')
        self.checkbox2_col1.setChecked(True)
        layout_col1.addWidget(self.checkbox2_col1)
        self.checkbox3_col1=QCheckBox('sensor 3')
        self.checkbox3_col1.setChecked(True)
        layout_col1.addWidget(self.checkbox3_col1)
        return layout_col1
    
    def init_col2(self):
        layout_col2=QVBoxLayout()
        layout_col2.setAlignment(Qt.AlignmentFlag.AlignTop)
        label_col2=QLabel('Select Data to See')
        layout_col2.addWidget(label_col2)
        self.checkbox1_col2=QCheckBox('temperature')
        self.checkbox1_col2.setChecked(True)
        layout_col2.addWidget(self.checkbox1_col2)
        self.checkbox2_col2=QCheckBox('humidity')
        self.checkbox2_col2.setChecked(True)
        layout_col2.addWidget(self.checkbox2_col2)
        self.checkbox3_col2=QCheckBox('pH')
        self.checkbox3_col2.setChecked(True)
        layout_col2.addWidget(self.checkbox3_col2)
        self.checkbox4_col2=QCheckBox('ir')
        self.checkbox4_col2.setChecked(True)
        layout_col2.addWidget(self.checkbox4_col2)
        self.checkbox5_col2=QCheckBox('vis')
        self.checkbox5_col2.setChecked(True)
        layout_col2.addWidget(self.checkbox5_col2)
        self.checkbox6_col2=QCheckBox('battery')
        self.checkbox6_col2.setChecked(True)
        layout_col2.addWidget(self.checkbox6_col2)
        return layout_col2
    
    def init_col3(self):
        layout_col3=QVBoxLayout()
        layout_col3.setAlignment(Qt.AlignmentFlag.AlignTop)
        label1_col3=QLabel('Select Starting Date')
        layout_col3.addWidget(label1_col3)
        self.dt_start=QDateTimeEdit()
        self.dt_start.setDateTime(QDateTime.currentDateTime().addSecs(-1200))
        layout_col3.addWidget(self.dt_start)
        label2_col3=QLabel('Select Ending Date')
        layout_col3.addWidget(label2_col3)
        self.dt_end=QDateTimeEdit()
        self.dt_end.setDateTime(QDateTime.currentDateTime())
        layout_col3.addWidget(self.dt_end)
        button=QPushButton('Generate Graph')
        button.clicked.connect(self.generate_graph)
        layout_col3.addWidget(button)
        plants_button=QPushButton('View Plants')
        plants_button.setStyleSheet("""
            QPushButton{
                                    background-color:#008080;
                                    color:white;
                                    border-radius:8px;
                                    font-size:16px;
                                    padding:8px;

                                    
            }
            QPushButton:hover{
                                    background-color:#009090;
            }
        """

                                    )
        plants_button.clicked.connect(self.open_plants_window)
        layout_col3.addWidget(plants_button)
        return layout_col3
    
    def open_plants_window(self):
        self.plants_window=PlantsPage()
        self.plants_window.show()

    def generate_graph(self):
        fields=set()
        sensors=set()
        url = "http://127.0.0.1:5000/api/visualize?"
        if self.checkbox1_col1.isChecked():
            url+="sensors=1&"
            sensors.add("1")
        if self.checkbox2_col1.isChecked():
            url+="sensors=2&"
            sensors.add("2")
        if self.checkbox3_col1.isChecked():
            url+="sensors=3&"
            sensors.add("3")
        if self.checkbox1_col2.isChecked():
            url+="fields=temperature&"
            fields.add("temperature")
        if self.checkbox2_col2.isChecked():
            url+="fields=humidity&"
            fields.add("humidity")
        if self.checkbox3_col2.isChecked():
            url+="fields=pH&"
            fields.add("pH")
        if self.checkbox4_col2.isChecked():
            url+="fields=ir&"
            fields.add("ir")
        if self.checkbox5_col2.isChecked():
            url+="fields=vis&"
            fields.add("vis")
        if self.checkbox6_col2.isChecked():
            url+="fields=battery&"
            fields.add("battery")
        url+=f"date_start={self.dt_start.dateTime().toString('yyyy-MM-ddTHH:mm:ss')}&"
        url+=f"date_end={self.dt_end.dateTime().toString('yyyy-MM-ddTHH:mm:ss')}"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload).json()

        res = [SensorData(row, fields) for row in response] 
        sensor1 = [sensor for sensor in res if sensor.sensor==1]
        sensor2 = [sensor for sensor in res if sensor.sensor==2]
        sensor3 = [sensor for sensor in res if sensor.sensor==3]
        datetimes1 = [item.created_at.strftime("%H:%M") for item in sensor1]
        temperatures1 = [item.temperature for item in sensor1]
        datetimes2 = [item.created_at.strftime("%H:%M") for item in sensor2]
        temperatures2 = [item.temperature for item in sensor2]
        datetimes3 = [item.created_at.strftime("%H:%M") for item in sensor3]
        temperatures3 = [item.temperature for item in sensor3]
        humidity1=[item.humidity for item in sensor1]
        humidity2=[item.humidity for item in sensor2]
        humidity3=[item.humidity for item in sensor3]
        pH1=[item.pH for item in sensor1]
        pH2=[item.pH for item in sensor2]
        pH3=[item.pH for item in sensor3]
        ir1=[item.ir for item in sensor1]
        ir2=[item.ir for item in sensor2]
        ir3=[item.ir for item in sensor3]
        vis1=[item.vis for item in sensor1]
        vis2=[item.vis for item in sensor2]
        vis3=[item.vis for item in sensor3]
        battery1=[item.battery for item in sensor1]
        battery2=[item.battery for item in sensor2]
        battery3=[item.battery for item in sensor3]
        
        if "temperature" in fields:
            plt.figure(figsize=(20, 8))
            if "1" in sensors:
                plt.plot(datetimes1, temperatures1, marker="o", linestyle="-", color="g", label="sensor 1")
            if "2" in sensors:
                plt.plot(datetimes2, temperatures2, marker="o", linestyle="-", color="r", label="sensor 2")
            if "3" in sensors:
                plt.plot(datetimes3, temperatures3, marker="o", linestyle="-", color="b", label="sensor 3")
            plt.title("Surrounding temperature")
            plt.xlabel("Time")
            plt.ylabel("Temperature (°C)")
            plt.grid(True)
            plt.legend()
            plt.show()
        
        if "humidity" in fields:
            plt.figure(figsize=(20, 8))
            if "1" in sensors:
                plt.plot(datetimes1, humidity1, marker="o", linestyle="-", color="g", label="sensor 1")
            if "2" in sensors:
                plt.plot(datetimes2, humidity2, marker="o", linestyle="-", color="r", label="sensor 2")
            if "3" in sensors:
                plt.plot(datetimes3, humidity3, marker="o", linestyle="-", color="b", label="sensor 3")
            plt.title("Soil moisture level")
            plt.xlabel("Time")
            plt.ylabel("Volt(V)")
            plt.grid(True)
            plt.legend()
            plt.show()

        if "pH" in fields:
            plt.figure(figsize=(20, 8))
            if "1" in sensors:
                plt.plot(datetimes1, pH1, marker="o", linestyle="-", color="g", label="sensor 1")
            if "2" in sensors:
                plt.plot(datetimes2, pH2, marker="o", linestyle="-", color="r", label="sensor 2")
            if "3" in sensors:
                plt.plot(datetimes3, pH3, marker="o", linestyle="-", color="b", label="sensor 3")
            plt.title("Acidity")
            plt.xlabel("Time")
            plt.ylabel("pH")
            plt.grid(True)
            plt.legend()
            plt.show()
        
        if "ir" in fields:
            plt.figure(figsize=(20, 8))
            if "1" in sensors:
                plt.plot(datetimes1, ir1, marker="o", linestyle="-", color="g", label="sensor 1")
            if "2" in sensors:
                plt.plot(datetimes2, ir2, marker="o", linestyle="-", color="r", label="sensor 2")
            if "3" in sensors:
                plt.plot(datetimes3, ir3, marker="o", linestyle="-", color="b", label="sensor 3")
            plt.title("Infrared Radiation")
            plt.xlabel("Time")
            plt.ylabel("Reflectance(%)")
            plt.grid(True)
            plt.legend()
            plt.show()
        
        if "vis" in fields:
            plt.figure(figsize=(20, 8))
            if "1" in sensors:
                plt.plot(datetimes1, vis1, marker="o", linestyle="-", color="g", label="sensor 1")
            if "2" in sensors:
                plt.plot(datetimes2, vis2, marker="o", linestyle="-", color="r", label="sensor 2")
            if "3" in sensors:
                plt.plot(datetimes3, vis3, marker="o", linestyle="-", color="b", label="sensor 3")
            plt.title("Visible (VIS) spectrum of light")
            plt.xlabel("Time")
            plt.ylabel("VIS(nm)")
            plt.grid(True)
            plt.legend()
            plt.show()

        if "battery" in fields:
            plt.figure(figsize=(20, 8))
            if "1" in sensors:
                plt.plot(datetimes1, battery1, marker="o", linestyle="-", color="g", label="sensor 1")
            if "2" in sensors:
                plt.plot(datetimes2, battery2, marker="o", linestyle="-", color="r", label="sensor 2")
            if "3" in sensors:
                plt.plot(datetimes3, battery3, marker="o", linestyle="-", color="b", label="sensor 3")
            plt.title("Battery Capacity")
            plt.xlabel("Time")
            plt.ylabel("Battery level(%)")
            plt.grid(True)
            plt.legend()
            plt.show()

    def show_map(self):
        payload = {}
        headers = {}
        fields=["sensor_id", "created_at", "temperature", "humidity", "pH", "ir", "vis", "battery"]
        url = "http://127.0.0.1:5000/api/get_last"
        response = requests.request("GET", url, headers=headers, data=payload).json()
        res = [SensorData(row, fields) for row in response] 
        if len(res)>=3:
            sensor1 = [sensor for sensor in res if sensor.sensor==1][0]
            sensor2 = [sensor for sensor in res if sensor.sensor==2][0]
            sensor3 = [sensor for sensor in res if sensor.sensor==3][0]
            data=io.BytesIO()
            mark = folium.Map(location=[41.290079, 13.377327],
                    tiles='cartodbpositron', zoom_start=17)
            custom_icon1 = CustomIcon(icon_image="https://cdn-icons-png.flaticon.com/128/8715/8715781.png", icon_size=(20, 20))
            custom_icon2 = CustomIcon(icon_image="https://cdn-icons-png.flaticon.com/128/8715/8715781.png", icon_size=(20, 20))
            custom_icon3 = CustomIcon(icon_image="https://cdn-icons-png.flaticon.com/128/8715/8715781.png", icon_size=(20, 20))
            Marker([41.290629, 13.375400], popup="sensor 1", icon=custom_icon1, tooltip=f"""
                    sensor: {sensor1.sensor},
                    created_at: {sensor1.created_at.strftime("%m/%d %H:%M")} - 
                    temperature: {sensor1.temperature} -
                    humidity: {sensor1.humidity} -
                    pH: {sensor1.pH} -
                    ir: {sensor1.ir} -
                    vis: {sensor1.vis} -
                    battery: {sensor1.battery}
            """).add_to(mark)
            
            Marker([41.290379, 13.376924], popup="sensor 2", icon=custom_icon2, tooltip=f"""
                    sensor: {sensor2.sensor},
                    created_at: {sensor2.created_at.strftime("%m/%d %H:%M")} - 
                    temperature: {sensor2.temperature} -
                    humidity: {sensor2.humidity} -
                    pH: {sensor2.pH} -
                    ir: {sensor2.ir} -
                    vis: {sensor2.vis} -
                    battery: {sensor2.battery}
            """).add_to(mark)
            Marker([41.290250, 13.376116], popup="sensor 3", icon=custom_icon3, tooltip=f"""
                    sensor: {sensor3.sensor},
                    created_at: {sensor3.created_at.strftime("%m/%d %H:%M")} - 
                    temperature: {sensor3.temperature} -
                    humidity: {sensor3.humidity} -
                    pH: {sensor3.pH} -
                    ir: {sensor3.ir} -
                    vis: {sensor3.vis} -
                    battery: {sensor3.battery}
            """).add_to(mark)
            mark.save(data, close_file=False)
            self.webview = QWebEngineView()
            self.webview.setHtml(data.getvalue().decode())


class PlantsPage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Plants Optimal Position')
        self.setGeometry(QGuiApplication.primaryScreen().geometry())
        main_layout=QVBoxLayout()
        row1_layout=QHBoxLayout()
        row2_layout=QHBoxLayout()
        self.webview=QWebEngineView()
        layout_col1=self.init_col1()
        layout_col2=self.init_col2()
        layout_col3=self.init_col3()

        row1_layout.addLayout(layout_col1)
        row1_layout.addLayout(layout_col2)
        row1_layout.addLayout(layout_col3)

        main_layout.addLayout(row1_layout)
        self.show_map()
        row2_layout.addWidget(self.webview)
        
        main_layout.addLayout(row2_layout)
        self.setLayout(main_layout)
        
    def init_col1(self):
        layout_col1=QVBoxLayout()
        layout_col1.setAlignment(Qt.AlignmentFlag.AlignTop)
        label_col1=QLabel('Title')
        layout_col1.addWidget(label_col1)
        self.title_textfield=QLineEdit()
        layout_col1.addWidget(self.title_textfield)
        label_col1=QLabel('Soil Type')
        layout_col1.addWidget(label_col1)
        self.soil_textfield=QLineEdit()
        layout_col1.addWidget(self.soil_textfield)
        return layout_col1
    
    def init_col2(self):
        layout_col2=QVBoxLayout()
        layout_col2.setAlignment(Qt.AlignmentFlag.AlignTop)
        label_col2=QLabel('Minimum Temperature')
        layout_col2.addWidget(label_col2)
        self.temp_min_textfield=QLineEdit()
        layout_col2.addWidget(self.temp_min_textfield)
        label_col2=QLabel('Maximum Temperature')
        layout_col2.addWidget(label_col2)
        self.temp_max_textfield=QLineEdit()
        layout_col2.addWidget(self.temp_max_textfield)

        add_plant_button=QPushButton('Add Plant')
        add_plant_button.setStyleSheet("""
            QPushButton{
                                    background-color:#008080;
                                    color:white;
                                    border-radius:8px;
                                    font-size:16px;
                                    padding:8px;

                                    
            }
            QPushButton:hover{
                                    background-color:#009090;
            }
        """

                                    )
        add_plant_button.clicked.connect(self.add_plant)
        layout_col2.addWidget(add_plant_button)

        return layout_col2
    
    def init_col3(self):
        layout_col3=QVBoxLayout()
        layout_col3.setAlignment(Qt.AlignmentFlag.AlignTop)
        label_col3=QLabel('Minimum pH')
        layout_col3.addWidget(label_col3)
        self.ph_min_textfield=QLineEdit()
        layout_col3.addWidget(self.ph_min_textfield)
        label_col3=QLabel('Maximum pH')
        layout_col3.addWidget(label_col3)
        self.ph_max_textfield=QLineEdit()
        layout_col3.addWidget(self.ph_max_textfield)
        return layout_col3
    


    def show_map(self):
        mark = folium.Map(location=[41.290079, 13.377327],
                tiles='cartodbpositron', zoom_start=17)
        payload = {}
        headers = {}
        url = "http://127.0.0.1:5000/api/plants"
        response = requests.request("GET", url, headers=headers, data=payload).json()
        res = [Plant(row) for row in response] 
        self.calculate_optimal_position(plants=res, mark=mark)
        data=io.BytesIO()
        
        
        custom_icon1 = CustomIcon(icon_image="https://cdn-icons-png.flaticon.com/128/8715/8715781.png", icon_size=(20, 20))
        custom_icon2 = CustomIcon(icon_image="https://cdn-icons-png.flaticon.com/128/8715/8715781.png", icon_size=(20, 20))
        custom_icon3 = CustomIcon(icon_image="https://cdn-icons-png.flaticon.com/128/8715/8715781.png", icon_size=(20, 20))
        Marker([41.290629, 13.375400], popup="sensor 1", icon=custom_icon1).add_to(mark)
        Marker([41.290379, 13.376924], popup="sensor 2", icon=custom_icon2).add_to(mark)
        Marker([41.290250, 13.376116], popup="sensor 3", icon=custom_icon3).add_to(mark)
        
        
        mark.save(data, close_file=False)
        self.webview = QWebEngineView()
        self.webview.setHtml(data.getvalue().decode())
        data=io.BytesIO()

        #map_path="map.html"

        #self.webview.setUrl(QUrl.fromLocalFile(map_path))

    def calculate_optimal_position(self, plants, mark):
        payload = {}
        headers = {}
        url = "http://127.0.0.1:5000/api/sensors"
        response = requests.request("GET", url, headers=headers, data=payload).json()
        res = [Sensor(row) for row in response] 
        for sensor in res:
            payload = {}
            headers = {}
            current_datetime=datetime.now()
            threemago_datetime=current_datetime - relativedelta(months=3)
            url_s = f"http://127.0.0.1:5000/api/average?sensor={sensor.id}&" 
            url_s+=f"date_start={threemago_datetime.strftime('%Y-%m-%dT%H:%M:%S')}&"
            url_s+=f"date_end={current_datetime.strftime('%Y-%m-%dT%H:%M:%S')}"
            response_s = requests.request("GET", url_s, headers=headers, data=payload).json()
            if len(response_s)>0:
                res_s = [SensorData(row, ["temperature", "pH"]) for row in response_s][0]
                sensor.avg_temp=res_s.temperature
                sensor.avg_pH=res_s.pH
                print(sensor)
        sensor1=res[0]
        sensor2=res[1]
        sensor3=res[2]
        t1=sensor1.avg_temp
        t2=sensor2.avg_temp
        t3=sensor3.avg_temp
        ph1=sensor1.avg_pH
        ph2=sensor2.avg_pH
        ph3=sensor3.avg_pH
        min_temps=[]
        max_temps=[]
        min_phs=[]
        max_phs=[]
        if t1<=t2: 
            min_temps.append(t1)
            max_temps.append(t2)
        else: 
            min_temps.append(t2)
            max_temps.append(t1)
        if t1<=t3: 
            min_temps.append(t1)
            max_temps.append(t3)
        else: 
            min_temps.append(t3)
            max_temps.append(t1)
        if t2<=t3: 
            min_temps.append(t2)
            max_temps.append(t3)
        else: 
            min_temps.append(t3)
            max_temps.append(t2)

        if ph1<=ph2: 
            min_phs.append(ph1)
            max_phs.append(ph2)
        else: 
            min_phs.append(ph2)
            max_phs.append(ph1)
        if ph1<=ph3: 
            min_phs.append(ph1)
            max_phs.append(ph3)
        else: 
            min_phs.append(ph3)
            max_phs.append(ph1)
        if ph2<=ph3: 
            min_phs.append(ph2)
            max_phs.append(ph3)
        else: 
            min_phs.append(ph3)
            max_phs.append(ph2)
        print(min_temps, max_temps, min_phs, max_phs)

        for plant in plants:
            t_min=plant.temp_min
            t_max=plant.temp_max
            ph_min=plant.pH_min
            ph_max=plant.pH_max
            temps_set=set([1,2,3])
            phs_set=set([1,2,3])
            if t1<=t2 and (t_min>t2 or t_max<t1): temps_set.remove(1)
            if t1>=t2 and (t_min>t1 or t_max<t2): temps_set.remove(1)
            if t1<=t3 and (t_min>t3 or t_max<t1): temps_set.remove(2)
            if t1>=t3 and (t_min>t1 or t_max<t3): temps_set.remove(2)
            if t2<=t3 and (t_min>t3 or t_max<t2): temps_set.remove(3)
            if t2>=t3 and (t_min>t2 or t_max<t3): temps_set.remove(3)
            print(temps_set)
            if ph1<=ph2 and (ph_min>ph2 or ph_max<ph1): phs_set.remove(1)
            if ph1>=ph2 and (ph_min>ph1 or ph_max<ph2): phs_set.remove(1)
            if ph1<=ph3 and (ph_min>ph3 or ph_max<ph1): phs_set.remove(2)
            if ph1>=ph3 and (ph_min>ph1 or ph_max<ph3): phs_set.remove(2)
            if ph2<=ph3 and (ph_min>ph3 or ph_max<ph2): phs_set.remove(3)
            if ph2>=ph3 and (ph_min>ph2 or ph_max<ph3): phs_set.remove(3)
            print(phs_set)
            if len(temps_set)==0 or len(phs_set)==0:
                print(f"The plant: {plant.title} can't be placed")
                continue
            print(f"The plant: {plant.title} can be placed")
            best_temps=dict()
            for i in temps_set:
                best_temp=(t_max+t_min)/2

                if best_temp<min_temps[i-1]: best_temp=min_temps[i-1]
                elif best_temp>max_temps[i-1]: best_temp=max_temps[i-1]
                best_temps[i-1]=best_temp
            print(json.dumps(best_temps, indent=2))
            best_phs=dict()
            for i in phs_set:
                best_ph=(ph_max+ph_min)/2

                if best_ph<min_phs[i-1]: best_ph=min_phs[i-1]
                elif best_ph>max_phs[i-1]: best_ph=max_phs[i-1]
                best_phs[i-1]=best_ph
            print(json.dumps(best_phs, indent=2))
    
            avg_coords=self.calc_avg_coords(best_temps, best_phs, t1, t2, t3, ph1, ph2, ph3, sensor1, sensor2, sensor3)
            best_coord=self.calc_best_coord(avg_coords, plant, sensor1, sensor2, sensor3)
            if best_coord!=(0,0):
                custom_icon = CustomIcon(icon_image="https://cdn-icons-png.flaticon.com/128/2303/2303716.png", icon_size=(20, 20))
                Marker([best_coord[0], best_coord[1]], popup=plant.title, icon=custom_icon).add_to(mark)
                
        data=io.BytesIO()
        mark.save(data, close_file=False)
        self.webview = QWebEngineView()
        self.webview.setHtml(data.getvalue().decode())
        
              


    def calc_coords(self, t1, t2, sensor1, sensor2, temp):
        temps_diff=abs(t1-t2)
        lats_diff=abs(sensor1.lat-sensor2.lat)
        longs_diff=abs(sensor1.long-sensor2.long)
        x_lat_delta=((temp-min(t1,t2))*lats_diff)/temps_diff
        x_long_delta=((temp-min(t1,t2))*longs_diff)/temps_diff
        x_lat=min(sensor1.lat, sensor2.lat)+x_lat_delta
        x_long=min(sensor1.long, sensor2.long)+x_long_delta
        return x_lat, x_long

    def calc_avg_coord(self, temp_lat, temp_long, ph_lat, ph_long):
        lat=abs(temp_lat+ph_lat)/2
        long=abs(temp_long+ph_long)/2
        return lat,long
    
    def calc_avg_coords(self, best_temps, best_phs, t1, t2, t3, ph1, ph2, ph3, sensor1, sensor2, sensor3):
        avg_coords=[]
        best_temps_coords=[]
        best_phs_coords=[]
        if 0 in best_temps.keys():
            temp_lat1, temp_long1=self.calc_coords(t1, t2, sensor1, sensor2, best_temps[0])
            best_temps_coords.append((temp_lat1, temp_long1))
        if 1 in best_temps.keys():
            temp_lat2, temp_long2=self.calc_coords(t1, t3, sensor1, sensor3, best_temps[1])
            best_temps_coords.append((temp_lat2, temp_long2))
        if 2 in best_temps.keys():
            temp_lat3, temp_long3=self.calc_coords(t2, t3, sensor2, sensor3, best_temps[2])
            best_temps_coords.append((temp_lat3, temp_long3))
        
        if 0 in best_phs.keys():
            ph_lat1, ph_long1=self.calc_coords(ph1, ph2, sensor1, sensor2, best_phs[0])
            best_phs_coords.append((ph_lat1, ph_long1))
        if 1 in best_phs.keys():
            ph_lat2, ph_long2=self.calc_coords(ph1, ph3, sensor1, sensor3, best_phs[1])
            best_phs_coords.append((ph_lat2, ph_long2))
        if 2 in best_phs.keys():
            ph_lat3, ph_long3=self.calc_coords(ph2, ph3, sensor2, sensor3, best_phs[2])
            best_phs_coords.append((ph_lat3, ph_long3))

        for best_temp_coord in best_temps_coords:
            for best_ph_coord in best_phs_coords:
                avg_lat, avg_long=self.calc_avg_coord(best_temp_coord[0], best_temp_coord[1], best_ph_coord[0], best_ph_coord[1])
                avg_coords.append((avg_lat, avg_long))
        return avg_coords


    def calc_best_coord(self, avg_coords, plant:Plant, sensor1:Sensor, sensor2:Sensor, sensor3:Sensor):
        best_coord=(0,0)
        best_score=float("inf")
        
        for avg_coord in avg_coords:
            t, ph=self.baricentric_interpolation(sensor1, sensor2, sensor3, avg_coord[0], avg_coord[1])
            plant_temp=(plant.temp_max+plant.temp_min)/2
            plant_ph=(plant.pH_max+plant.pH_min)/2
            score=abs(plant_temp-t)+abs(plant_ph-ph)
            if score < best_score: 
                best_score=score
                best_coord=(avg_coord[0], avg_coord[1])
        print("the best coordinate for plant" ,plant.title, "is:", best_coord)
        return best_coord


    def baricentric_interpolation(self, sensor1: Sensor, sensor2: Sensor, sensor3: Sensor, lat, long):
        denom=(sensor2.long-sensor3.long)*(sensor1.lat-sensor3.lat)+(sensor3.lat-sensor2.lat)*(sensor1.long-sensor3.long)
        l1=((sensor2.long-sensor3.long)*(lat-sensor3.lat)+(sensor3.lat-sensor2.lat)*(long-sensor3.long))/denom
        l2=((sensor3.long-sensor1.long)*(lat-sensor3.lat)+(sensor1.lat-sensor3.lat)*(long-sensor3.long))/denom
        l3=1-l1-l2
        t=l1*sensor1.avg_temp+l2*sensor2.avg_temp+l3*sensor3.avg_temp
        ph=l1*sensor1.avg_pH+l2*sensor2.avg_pH+l3*sensor3.avg_pH
        return t, ph

    def add_plant(self):
        title=self.title_textfield.text()
        soil=self.soil_textfield.text()
        temp_min=float(self.temp_min_textfield.text().replace(',', '.'))
        temp_max=float(self.temp_max_textfield.text().replace(',', '.'))
        ph_min=float(self.ph_min_textfield.text().replace(',', '.'))
        ph_max=float(self.ph_max_textfield.text().replace(',', '.'))
        url = "http://127.0.0.1:5000/api/plants"

        payload = json.dumps({
            "title": title,
            "soil": soil,
            "temp_min": temp_min,
            "temp_max": temp_max,
            "pH_min": ph_min,
            "pH_max": ph_max,
            
        })
        headers = {
            'Content-Type': 'application/json'
        }

        requests.request("POST", url, headers=headers, data=payload)
        msg_box=QMessageBox(self)
        msg_box.setText("Plant Added Successfully")
        msg_box.setWindowTitle("Done")
        msg_box.exec()
        self.__init__()

            
        





if __name__=='__main__':
    app=QApplication(sys.argv)
    home_page=HomePage()
    home_page.show()
    app.exec()
