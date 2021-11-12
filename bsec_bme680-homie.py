#!/usr/bin/python3
# Import required Python libraries
import paho.mqtt.client as mqtt
import time, ssl, systemd.daemon, subprocess, json
from statistics import median

# set the variables
# MQTT Broker Connection
broker = "FQDN / IP ADDRESS"
port = 8883
mqttclientid = "clientid-bsecbme680-homie"
clientid = "clientid-bsecbme680"
clientname = "Clientname BSEC BME680 Sensor"
nodes="bme680"
username = "mosquitto"
password = "password"
insecure = True
qos = 1
retain_message = True
# Retry to connect to mqtt broker
mqttretry = 5
# how many values should be collected before publishing the median
medianvalues = 10
# True/False led warning (only True if you have an RGB Led connected) 
ledwarning = False
# set red,green and blue pins
redPin = 22
greenPin = 27
bluePin = 17
# At which value CO2 alarm will be fired (x in ppm)
eco2alarm = 1000
# At which value humidity alarm will be fired (x in %)
humidityalarm = 70

# do the stuff
if ledwarning == True:
  import RPi.GPIO as GPIO
  # disable warnings (optional)
  GPIO.setwarnings(False)
  # Select GPIO Mode
  GPIO.setmode(GPIO.BCM)
  # set pins as outputs
  GPIO.setup(redPin,GPIO.OUT)
  GPIO.setup(greenPin,GPIO.OUT)
  GPIO.setup(bluePin,GPIO.OUT)

### Functions
def turnOffled():
  GPIO.output(redPin,GPIO.LOW)
  GPIO.output(greenPin,GPIO.LOW)
  GPIO.output(bluePin,GPIO.LOW)

def whiteled():
  GPIO.output(redPin,GPIO.HIGH)
  GPIO.output(greenPin,GPIO.HIGH)
  GPIO.output(bluePin,GPIO.HIGH)

def blueled():
  GPIO.output(redPin,GPIO.LOW)
  GPIO.output(greenPin,GPIO.LOW)
  GPIO.output(bluePin,GPIO.HIGH)

def redled():
  GPIO.output(redPin,GPIO.HIGH)
  GPIO.output(greenPin,GPIO.LOW)
  GPIO.output(bluePin,GPIO.LOW)

def greenled():
  GPIO.output(redPin,GPIO.LOW)
  GPIO.output(greenPin,GPIO.HIGH)
  GPIO.output(bluePin,GPIO.LOW)

def publish(topic, payload):
  client.publish("homie/" + clientid + "/" + topic,payload,qos,retain_message)

def on_connect(client, userdata, flags, rc):
  print("MQTT Connection established, Returned code=",rc)
  # homie client config
  publish("$state","init")
  publish("$homie","4.0")
  publish("$name",clientname)
  publish("$nodes",nodes)
  # homie node config
  publish(nodes + "/$name","BME680 Sensor")
  publish(nodes + "/$properties","temperature,humidity,gas,pressure,iaqaccuracy,iaq,staticiaq,eco2,bvoce,sensorstate,eco2alarm,humidityalarm")
  publish(nodes + "/temperature/$name","Temperature")
  publish(nodes + "/temperature/$unit","°C")
  publish(nodes + "/temperature/$datatype","float")
  publish(nodes + "/temperature/$settable","false")
  publish(nodes + "/humidity/$name","Humidity")
  publish(nodes + "/humidity/$unit","%")
  publish(nodes + "/humidity/$datatype","float")
  publish(nodes + "/humidity/$settable","false")
  publish(nodes + "/humidityalarm/$name","Humidity Alarm")
  publish(nodes + "/humidityalarm/$datatype","boolean")
  publish(nodes + "/humidityalarm/$settable","false")
  publish(nodes + "/gas/$name","Gas")
  publish(nodes + "/gas/$unit","ohm")
  publish(nodes + "/gas/$datatype","integer")
  publish(nodes + "/gas/$settable","false")
  publish(nodes + "/pressure/$name","Pressure")
  publish(nodes + "/pressure/$unit","hPa")
  publish(nodes + "/pressure/$datatype","float")
  publish(nodes + "/pressure/$settable","false")
  publish(nodes + "/iaqaccuracy/$name","IAQ Accuracy")
  publish(nodes + "/iaqaccuracy/$datatype","integer")
  publish(nodes + "/iaqaccuracy/$settable","false")
  publish(nodes + "/iaq/$name","Indoor Air Quality")
  publish(nodes + "/iaq/$datatype","float")
  publish(nodes + "/iaq/$settable","false")
  publish(nodes + "/staticiaq/$name","Static Indoor Air Quality")
  publish(nodes + "/staticiaq/$datatype","float")
  publish(nodes + "/staticiaq/$settable","false")
  publish(nodes + "/eco2/$name","CO2 equivalent")
  publish(nodes + "/eco2/$unit","ppm")
  publish(nodes + "/eco2/$datatype","float")
  publish(nodes + "/eco2/$settable","false")
  publish(nodes + "/eco2alarm/$name","CO2 Alarm")
  publish(nodes + "/eco2alarm/$datatype","boolean")
  publish(nodes + "/eco2alarm/$settable","false")
  publish(nodes + "/bvoce/$name","Breath VOC equivalent")
  publish(nodes + "/bvoce/$unit","ppm")
  publish(nodes + "/bvoce/$datatype","float")
  publish(nodes + "/bvoce/$settable","false")
  publish(nodes + "/sensorstate/$name","Sensor State")
  publish(nodes + "/sensorstate/$datatype","integer")
  publish(nodes + "/sensorstate/$settable","false")

def on_disconnect(client, userdata, rc):
  print("MQTT Connection disconnected, Returned code=",rc)

# running the Script
if ledwarning == True:
  whiteled()
#MQTT Connection
mqttattempts = 0
while mqttattempts < mqttretry:
  try:
    client=mqtt.Client(mqttclientid)
    client.username_pw_set(username, password)
    client.tls_set(cert_reqs=ssl.CERT_NONE) #no client certificate needed
    client.tls_insecure_set(insecure)
    client.will_set("homie/" + clientid + "/$state","lost",qos,retain_message)
    client.connect(broker, port)
    client.loop_start()
    mqttattempts = mqttretry
  except :
    print("Could not establish MQTT Connection! Try again " + str(mqttretry - mqttattempts) + "x times")
    mqttattempts += 1
    if mqttattempts == mqttretry:
      print("Could not connect to MQTT Broker! exit...")
      exit (0)
    time.sleep(5)

# Tell systemd that our service is ready
systemd.daemon.notify('READY=1')

client.on_connect = on_connect
client.on_disconnect = on_disconnect

# finaly read the c file and publish the output to MQTT
try:
  proc = subprocess.Popen(['./bsec_bme680'], stdout=subprocess.PIPE)

  # create empty list objects
  listTemperature = []
  listHumidity  = []
  listGas = []
  listPressure = []
  listIAQ_Accuracy = []
  listIAQ = []
  listStatic_IAQ = []
  listeCO2 = []
  listbVOCe = []
  listStatus = []

  # now read the c file input
  for line in iter(proc.stdout.readline, ''):
    lineJSON = json.loads(line.decode("utf-8")) # process line-by-line
    lineDict = dict(lineJSON)
    #print(line.decode("utf-8"))
    listTemperature.append(float(lineDict['Temperature']))
    listHumidity.append(float(lineDict['Humidity']))
    listGas.append(int(lineDict['Gas']))
    listPressure.append(float(lineDict['Pressure']))
    listIAQ_Accuracy.append(int(lineDict['IAQ_Accuracy']))
    listIAQ.append(float(lineDict['IAQ']))
    listStatic_IAQ.append(float(lineDict['Static_IAQ']))
    listeCO2.append(float(lineDict['eCO2']))
    listbVOCe.append(float(lineDict['bVOCe']))
    listStatus.append(int(lineDict['Status']))
    #print(listTemperature)
    if len(listIAQ_Accuracy) == medianvalues:
      #generate the median for each value and publish it
      #print(listTemperature)
      #print(median(listTemperature))
      #print(listeCO2)
      #print(median(listeCO2))
      #print(listbVOCe)
      #print(median(listbVOCe))
      publish(nodes + "/temperature","{:.2f}".format(median(listTemperature)))
      publish(nodes + "/humidity","{:.2f}".format(median(listHumidity)))
      publish(nodes + "/gas","{:.0f}".format(median(listGas)))
      publish(nodes + "/pressure","{:.2f}".format(median(listPressure)))
      publish(nodes + "/iaqaccuracy","{:.0f}".format(median(listIAQ_Accuracy)))
      publish(nodes + "/iaq","{:.2f}".format(median(listIAQ)))
      publish(nodes + "/staticiaq","{:.2f}".format(median(listStatic_IAQ)))
      publish(nodes + "/eco2","{:.15f}".format(median(listeCO2)))
      publish(nodes + "/bvoce","{:.25f}".format(median(listbVOCe)))
      publish(nodes + "/sensorstate","{:.0f}".format(median(listStatus)))
      if median(listeCO2) >= eco2alarm and median(listHumidity) >= humidityalarm:
        publish(nodes + "/eco2alarm","true")
        publish(nodes + "/humidityalarm","true")
        if ledwarning == True:
          redled()
      if median(listeCO2) >= eco2alarm and median(listHumidity) <= humidityalarm:
        publish(nodes + "/eco2alarm","true")
        publish(nodes + "/humidityalarm","false")
        if ledwarning == True:
          redled()
      if median(listeCO2) <= eco2alarm and median(listHumidity) >= humidityalarm:
        publish(nodes + "/eco2alarm","false")
        publish(nodes + "/humidityalarm","true")
        if ledwarning == True:
          blueled()
      if median(listeCO2) <= eco2alarm and median(listHumidity) <= humidityalarm:
        publish(nodes + "/eco2alarm","false") 
        publish(nodes + "/humidityalarm","false") 
        if ledwarning == True:
          greenled()
      # homie state ready
      publish("$state","ready")

      #clear lists
      listTemperature.clear()
      listHumidity.clear()
      listGas.clear()
      listPressure.clear()
      listIAQ_Accuracy.clear()
      listIAQ.clear()
      listStatic_IAQ.clear()
      listeCO2.clear()
      listbVOCe.clear()
      listStatus.clear()

except KeyboardInterrupt:
  print("Goodbye!")
  if ledwarning == True:
    turnOffled()
  # At least close MQTT Connection
  publish("$state","disconnected")
  time.sleep(1)
  client.disconnect()
  client.loop_stop()
  exit (0)

# At least close MQTT Connection
print("Script stopped")
publish("$state","disconnected")
time.sleep(1)
if ledwarning == True:
  turnOffled()
client.disconnect()
client.loop_stop()
