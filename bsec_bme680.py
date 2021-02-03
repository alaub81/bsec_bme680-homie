#!/usr/bin/python3
import subprocess
import paho.mqtt.publish as publish
import json
from statistics import median

#Open C File
proc = subprocess.Popen(['./bsec_bme680'], stdout=subprocess.PIPE)

# 2021-01-31 16:56:59,[IAQ (0)]: 247.37,[T degC]: 21.95,[H %rH]: 42.05,[P hPa]: 989.68,[G Ohms]: 3591,[S]: 0,[eCO2 ppm]: 1370.145141601562500,[bVOCe ppm]: 2.7185881137847900390625000
# {"IAQ_Accuracy": "0","IAQ":"247.46","Temperature": "21.45","Humidity": "51.95","Pressure": "991.93","Gas": "35788","Status": "0","Static_IAQ": "137.06","eCO2": "1370.616333007812500","bVOCe": "2.7205247879028320312500000"}
listIAQ_Accuracy = []
listPressure = []
listGas = []
listTemperature = []
listIAQ = []
listHumidity  = []
listStatus = []
listStatic_IAQ = []
listeCO2 = []
listbVOCe = []

for line in iter(proc.stdout.readline, ''):
#    print(line.decode("utf-8"))
    lineJSON = json.loads(line.decode("utf-8")) # process line-by-line
    lineDict = dict(lineJSON)

    listIAQ_Accuracy.append(int(lineDict['IAQ_Accuracy']))
    listPressure.append(float(lineDict['Pressure']))
    listGas.append(int(lineDict['Gas']))
    listTemperature.append(float(lineDict['Temperature']))
    listIAQ.append(float(lineDict['IAQ']))
    listHumidity.append(float(lineDict['Humidity']))
    listStatus.append(int(lineDict['Status']))
    listStatic_IAQ.append(float(lineDict['Static_IAQ']))
    listeCO2.append(float(lineDict['eCO2']))
    listbVOCe.append(float(lineDict['bVOCe']))

    if len(listIAQ_Accuracy) == 10:
        #generate the median for each value
        IAQ_Accuracy = median(listIAQ_Accuracy)
        Pressure = median(listPressure)
        Gas = median(listGas)
        Temperature = median(listTemperature)
        IAQ = median(listIAQ)
        Humidity = median(listHumidity)
        Status = median(listStatus)
        Static_IAQ = median(listStatic_IAQ)
        eCO2 = median(listeCO2)
        bVOCe = median(listbVOCe)

        #clear lists
        listIAQ_Accuracy.clear()
        listPressure.clear()
        listGas.clear()
        listTemperature.clear()
        listIAQ.clear()
        listHumidity.clear()
        listStatus.clear()
        listStatic_IAQ.clear()
        listeCO2.clear()
        listbVOCe.clear()

        #Temperature Offset
        #Temperature = Temperature + 2

        #payload = {"IAQ_Accuracy": IAQ_Accuracy,"IAQ": round(IAQ, 1),"Temperature": round(Temperature, 1),"Humidity": round(Humidity, 1),"Pressure": round(Pressure, 1),"Gas": Gas,"Status": Status}
        #publish.single("bme680_wohnzimmer", json.dumps(payload), hostname="localhost")
        #print(payload)
        print("Temperature: ",Temperature)
        print("Humidity: ",Humidity)
        print("Pressure: ",Pressure)
        print("Gas: ",Gas)
        print("IAQ: ",IAQ)
        print("IAQ_Accuracy: ",IAQ_Accuracy)
        print("Static_IAQ: ",Static_IAQ)
        print("eCO2: ",eCO2)
        print("bVOCe: ",bVOCe)
        print("Status: ",Status)
