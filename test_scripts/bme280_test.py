import smbus2
import bme280
import time

port = 1
address = 0x76
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)

# the sample method will take a single reading and return a
# compensated_reading object
while(1):
    data = bme280.sample(bus, address, calibration_params)

    # the compensated_reading class has the following attributes
    print()
    #print(data.timestamp)
    print("Temp (°C): " + str(data.temperature))
    print("Pressure (hPa): " + str(data.pressure))
    print("Hum(% rH):" + str(data.humidity))

    # there is a handy string representation too
    #print(data)
    time.sleep(1)
