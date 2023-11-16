#!/usr/bin/python

import time
#import Sensors.ICM20948 as ICM20948 #Gyroscope/Acceleration/Magnetometer
import Sensors.BME280 as BME280  #Atmospheric Pressure/Temperature and humidity
import Sensors.LTR390 as LTR390 #UV
import Sensors.TSL2591 as TSL2591  #LIGHT
import Sensors.SGP40 as SGP40
import math


bme280 = BME280.BME280()
bme280.get_calib_param()
light = TSL2591.TSL2591()
uv = LTR390.LTR390()
sgp = SGP40.SGP40()
#icm20948 = ICM20948.ICM20948()

print("TSL2591 Light I2C address:0X29")
print("LTR390 UV I2C address:0X53")
print("SGP40 VOC I2C address:0X59")
#print("icm20948 9-DOF I2C address:0X68")
print("bme280 T&H I2C address:0X76")

try:
    while True:
        time.sleep(1)
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
        
        print("==================================================")
        print("pressure : %7.2f hPa" %pressure)
        print("temp : %-6.2f ℃" %temp)
        print("hum : %6.2f ％" %hum)
        print("lux : %d " %lux)
        print("uv : %d " %UVS)
        print("gas : %6.2f VOC" %voc_index)
        
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


except KeyboardInterrupt:
    exit()



