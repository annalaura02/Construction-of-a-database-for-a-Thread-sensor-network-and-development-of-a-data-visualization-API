from Sensor1 import app as sensorapp
from Server import app as serverapp
from multiprocessing import Process

def run_server():
    serverapp.run(port=5000, debug=False, use_reloader=False)

def run_sensor():
    sensorapp.run(port=5001, debug=False, use_reloader=False)


if __name__=="__main__":
    p1=Process(target=run_server)
    p2=Process(target=run_sensor)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    