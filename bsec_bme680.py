#!/usr/bin/python3
import subprocess
import json
from statistics import median

#Open C File
proc = subprocess.Popen(['./bsec_bme680'], stdout=subprocess.PIPE)

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
