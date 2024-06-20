#!/usr/bin/python

import time
#import Sensors.ICM20948 as ICM20948 #Gyroscope/Acceleration/Magnetometer
import Sensors.BME280 as BME280  #Atmospheric Pressure/Temperature and humidity
import Sensors.LTR390 as LTR390 #UV
import Sensors.TSL2591 as TSL2591  #LIGHT
import Sensors.SGP40 as SGP40
from Sensors.DFRobot_Ozone import *
import RPi.GPIO as GPIO

import math

import json

import paho.mqtt.publish as publish

import subprocess
import re

DEBUG = False

mqtt_topic = "sensors_data"
mqtt_host = "localhost"

flame_sensor_pin = 24

bme280 = BME280.BME280()
bme280.get_calib_param()
light = TSL2591.TSL2591()
uv = LTR390.LTR390()
sgp = SGP40.SGP40()
#icm20948 = ICM20948.ICM20948()

if GPIO.getmode() == -1:
    GPIO.setmode(GPIO.BOARD)
elif GPIO.getmode() == 11:
    flame_sensor_pin = 24
elif GPIO.getmode() == 10:
    flame_sensor_pin = 18

GPIO.setup(flame_sensor_pin, GPIO.IN)



COLLECT_NUMBER   = 20              # collect number, the collection range is 1-100
IIC_MODE         = 0x01            # default use IIC1

ozone = DFRobot_Ozone_IIC(IIC_MODE ,OZONE_ADDRESS_3)
ozone.set_mode(MEASURE_MODE_AUTOMATIC)

if DEBUG:
    print("TSL2591 Light I2C address:0X29")
    print("LTR390 UV I2C address:0X53")
    print("SGP40 VOC I2C address:0X59")
    #print("icm20948 9-DOF I2C address:0X68")
    print("bme280 T&H I2C address:0X76")
    print("Ozone address:0X73")
    print("Flame Sensor:GPIO24")
    
current_temp = 0
fans = ["fan1", "fan2", "fan3"]

with open("fanTestStatus.bin", "w") as f:
  f.write("0") 

def getPluggedDevices():
    # Execute the command with sudo (replace password prompt handling if needed)
  process = subprocess.Popen(["sudo", "python3", "-m", "liquidctl", "-v", "list"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  output, error = process.communicate()

  # Check for errors
  if error:
      print(f"Error retrieving device info: {error.decode()}")
      return []

  # Decode output and search for serial numbers
  output_str = output.decode()
  serial_numbers = []
  for match in re.finditer(r"Serial number: (.*)", output_str, re.MULTILINE):
      serial_numbers.append(match.group(1))

  # Return the list of serial numbers (or empty list if none found)
  return serial_numbers
    

try:
    while True:
        
        bme = []
        bme = bme280.readData()
        pressure = round(bme[0], 2) 
        temp = round(bme[1], 2) 
        hum = round(bme[2], 2)
        
        lux = round(light.Lux(), 2)
        
        UVS = uv.UVS()
        
        gas = round(sgp.measureRaw(temp, hum), 2)
        voc_index = (gas / 65535) * 100
        
        #icm = []
        #icm = icm20948.getdata()
        
        ozone_concentration = ozone.get_ozone_data(COLLECT_NUMBER)
        # Ozone concentration is PPB -> 0.01ppm (10ppb)
        ozone_concentration_ppm = ozone_concentration / 1000.0 # to ppm
        
        flame_sensor = GPIO.input(flame_sensor_pin)
        
        if DEBUG:
            print("==================================================")
            print("pressure : %7.2f hPa" %pressure)
            print("temp : %-6.2f ℃" %temp)
            print("hum : %6.2f ％" %hum)
            print("lux : %d " %lux)
            print("uv : %d " %UVS)
            print("gas : %6.2f VOC" %voc_index)
            print("ozone : %6.3f ppm" %ozone_concentration_ppm)
            print("flame : %d" %flame_sensor) 
        
        """
        0-50: Excellent air quality - Very low levels of pollutants, suitable for indoor environments like homes and offices.
        50-100: Good air quality - Generally clean air with minimal pollutants. Suitable for most indoor environments.
        100-200: Moderate air quality - Slightly elevated levels of pollutants. May be due to various sources like cleaning chemicals, cooking, or outdoor pollutants.
        200-300: Poor air quality - Elevated levels of pollutants. Could be due to a significant presence of indoor sources or external pollution.
        300 and above: Very poor air quality - High levels of pollutants. Considerable presence of pollutants, possibly from activities such as smoking or heavy use of cleaning chemicals.
        """
        
        #print("Roll = %.2f , Pitch = %.2f , Yaw = %.2f" %(icm[0],icm[1],icm[2]))
        #print("Acceleration: X = %d, Y = %d, Z = %d" %(icm[3],icm[4],icm[5]))
        #print("Gyroscope:     X = %d , Y = %d , Z = %d" %(icm[6],icm[7],icm[8]))
        #print("Magnetic:      X = %d , Y = %d , Z = %d" %(icm[9],icm[10],icm[11]))
        
        temp = round(temp, 3)
        hum = round(hum, 3)
        voc_index = round(voc_index, 3)
        pressure = round(pressure, 3)
        ozone_concentration_ppm = round(ozone_concentration_ppm, 3)
        
        data = {
            "temp": temp,
            "hum": hum,
            "gas": voc_index,
            "press": pressure,
            "uv": UVS,
            "lux": lux,
            "flame": flame_sensor,
            "ozone":ozone_concentration_ppm
        }
        
        json_data = json.dumps(data)
        publish.single(mqtt_topic, json_data, hostname=mqtt_host)
        
        #------------ settings processing --------------
        with open("fanTestStatus.bin") as f:
            fanTestStatus = f.read()
            if (fanTestStatus == "1"):
                time.sleep(1)
                continue
        
        if ((current_temp+1.0) > temp or (current_temp-1.0) < temp):
            
            current_temp = temp
            
            pluggedDevices = getPluggedDevices()
            
            
            
            if pluggedDevices:
                #print("NZXT Device Serial Numbers:")
                for i, serial in enumerate(pluggedDevices):
                    #print(f"  Device {i+1}: {serial}")
                    
                    # Open the JSON file
                    with open("fancontrol"+serial+".json") as f:
                        data = json.load(f)
                    try:
                        for fan in fans:

                            # Get fan1 temp and speed data
                            fan1_temp = [float(t) for t in data["fanSettings"][serial][fan]["temp"]]
                            fan1_speed = [float(s) for s in data["fanSettings"][serial][fan]["speed"]]

                            # Find indices of closest temperatures (lower and upper)
                            index_temp = 0
                            if current_temp > fan1_temp[0]:
                                for i in range(len(fan1_temp)):
                                    if (current_temp > fan1_temp[i] and current_temp < fan1_temp[i+1]):
                                        index_temp = i+1
                                        break
                            
                            # Check for exact match
                            if (index_temp == 0):
                                calculated_speed = fan1_speed[0]
                            elif (index_temp == len(fan1_temp)):
                                calculated_speed = fan1_speed[-1]
                            else:
                                if ((fan1_temp[index_temp-1] == fan1_temp[index_temp])):
                                    calculated_speed = fan1_speed[index_temp]
                                else:

                                    weight = ( fan1_speed[index_temp] - fan1_speed[index_temp-1] ) / (fan1_temp[index_temp] - fan1_temp[index_temp-1])
                                    
                                    # Interpolate speed based on weight
                                    calculated_speed = weight * ( current_temp - fan1_temp[index_temp-1] ) + fan1_speed[index_temp-1]
                                    
                            # Print the calculated speed
                            #print(f"Calculated fan speed for {current_temp}°C: {calculated_speed:.2f}%")
                            
                            # set calculated speed

                            command = ["sudo", "python", "-m", "liquidctl", "--serial", serial, "set", fan, "speed", str(round(calculated_speed))]

                            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            output, error = process.communicate()

                            if output:
                                print(output.decode())
                            if error:
                                print("Error:", error.decode())
                    except:
                        print("No serial number found")
            else:
                print("No NZXT devices found.")                    
                            
                        
        time.sleep(1)

except KeyboardInterrupt:
    exit()




