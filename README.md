# bsec_bme680-homie
Here you can find a complete small application, which uses the [Bosch Sensortec Environmental Cluster](https://www.bosch-sensortec.com/software-tools/software/bsec/) (BSEC) to read out the data from the BME680 Sensor and publish it to a MQTT Broker. The MQTT publishing is homie MQTT conventional, so you could use it as an IOT Device for your SmartHome. All you need is to download the [BSEC Library](https://www.bosch-sensortec.com/software-tools/software/bsec/) from the Bosch homepage, and this git repository. 

I reused the stuff of the follwoing git repositories, to make that thing here working:
* https://github.com/alexh-name/bsec_bme680_linux
* https://github.com/rstoermer/bsec_bme680_python

Big thanks to these two guys!

# Installation
so for installation just clone that repository, for example to `/opt`
```bash
cd /opt
git clone https://github.com/alaub81/bsec_bme680-homie.git
cd bsec_bme680-homie
```
now you need to download the [BSEC Library](https://www.bosch-sensortec.com/software-tools/software/bsec/) to `./src`. You have to register for the download. Then unzip it:
```bash
cd src
unzip bsec_1-4-8-0_generic_release.zip
```
## compiling the C application
now we have everything we need on our system and can configure the C application, so we can compile it. First of all we should configure the `make.config`:
```c
# Use right Version of downloaded bsec Library
BSEC_DIR='./src/BSEC_1.4.8.0_Generic_Release'

# which Version
VERSION='normal_version'

# which architecture you like to use
# Other architectures can be found in BSEC_DIR/algo/${VERSION}/bin/.
# that one runs under raspberry pi zero
ARCH="${VERSION}/bin/RaspberryPi/PiThree_ArmV6"

# which config you like to use
# Other configs are:
# generic_18v_300s_28d
# generic_18v_300s_4d
# generic_18v_3s_28d
# generic_18v_3s_4d
# generic_33v_300s_28d
# generic_33v_300s_4d
# generic_33v_3s_28d
# generic_33v_3s_4d
CONFIG='generic_33v_3s_4d'

# where is the config dir?
CONFIG_DIR='.'
```
The config in the repository works on a Raspberry Pi zero w, so just have a look on the `BSEC_DIR` if you have downloaded a newer Version of the BSEC library. If you are using it on another platform, just have a look at `ARCH`. If you are done with that configuration, there is a possibility to adjust your temperature value of the sensor, directly in the `bsec_bme680.c`:
```c
#define temp_offset (0.5f)
```
Just change the value `(0.5f)` to whatever you need. Or just keep it as it is.

Now we could compile the application:
```bash
cd /opt/bsec_bme680-homie
./make.sh
```
now we could give it a first try:
```bash
chmod +x bsec_bme680
./bsec_bme680
```
you should see something like that:
```
bsec_iaq.state empty
{"IAQ_Accuracy": "0","IAQ":"25.00","Temperature": "19.01","Humidity": "54.96","Pressure": "988.73","Gas": "14918","Status": "0","Static_IAQ": "25.00","eCO2": "500.000000000000000","bVOCe": "0.4999999403953552246093750"}
{"IAQ_Accuracy": "0","IAQ":"25.00","Temperature": "18.95","Humidity": "55.09","Pressure": "988.73","Gas": "17290","Status": "0","Static_IAQ": "25.00","eCO2": "500.000000000000000","bVOCe": "0.4999999403953552246093750"}
{"IAQ_Accuracy": "0","IAQ":"25.00","Temperature": "19.00","Humidity": "54.78","Pressure": "988.69","Gas": "19586","Status": "0","Static_IAQ": "25.00","eCO2": "500.000000000000000","bVOCe": "0.4999999403953552246093750"}

# Configuration
so now we can configure our Python Script. Just edit at the top the variables, to connect to the MQTT Broker:
```python3
# set the variables
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
# Retry to connect to mqtt broker
mqttretry = 5
```
## Systemd Service
after that you can copy the systemd service file, edit it if you have to change something, like perhaps the script's working path and just bring the app to life:
```bash
cp bsec_bme680-homie.service /etc/systemd/system/
systemctl daemon-reload
systemctl start bsec_bme680-homie.service
systemctl enable bsec_bme680-homie.service
systemctl enable bsec_bme680-homie.service
```
now check your MQTT Broker if there are new published topics from the device.

# Sensor Output
The Sensor, or better the BSEC library have the following outputs:
* Temperature (°C)
* Humidity (%)
* Gas (ohm)
* Pressure (hPa)
* IAQ accuracy - Accuracy of the IAQ score from 0 (low) to 3 (high)
* IAQ (Indoor Air Quality)
* Static IAQ
* eCO2 (ppm)
* bVOCe (ppm)
* Sensor State - Return value of the BSEC library
All this data will be published to the MQTT Broker and you could use it wherever you want.

# More Informations
Here you can find more informations about that little project. Goal was to get a nice little device for checking the room environment.
Sorry ... it's german ...
* https://www.laub-home.de/wiki/Raspberry_Pi_zero_w_zur_Raumluft_und_Luftqualitätsüberwachung

# Troubleshooting
`bsec_bme680` just quits without a message

Your `bsec_iaq.state file might be corrupt or incompatible after an update of the BSEC library. Try (re)moving it.
