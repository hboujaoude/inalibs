##This is the final version of the Pi supporting the following devices
## Display (DSI and I2C-1) , 3x INA sensors (I2C), and sends data to AZURE IOT HUB. 
## TO BE ADDED LATER: temp,  wireless weight scale using websockets, and relay control.

import time
import RPi.GPIO as GPIO
import asyncio
import board
import adafruit_ina260
import adafruit_ina261
import adafruit_ina264
import json
import numpy as np
import requests
import adafruit_bme680

idnum = 125468


url = "https://prod-06.canadacentral.logic.azure.com:443/workflows/56867d0b932a4a89af41a3e6389ca0f5/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=9py_MibmyhkECZCjCff3DaVuADqjzSBkJ_37_FfCSlQ"





i2c = board.I2C()
ina260 = adafruit_ina260.INA260(i2c)
ina261 = adafruit_ina261.INA261(i2c)
ina264 = adafruit_ina264.INA264(i2c)

bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug=False)

bme680.sea_level_pressure = 1013.25
temperature_offset = -5


coeff = 1000
danger = ina260.alert_limit


async def main():



    while True:


        if danger:
            print("DANGER VOLTAGE EXCEEDING LIMIT! REDUCE VOLTAGE NOW!")
        
    #bike
        temp = bme680.temperature + temperature_offset
        hum = bme680.relative_humidity
        press = bme680.pressure
        voc = bme680.gas


        
        
        mot_vol = ina260.voltage
        if mot_vol <= 0:
            mot_amp = 0
            mot_wat = 0
        else:        
            mot_amp = ina260.current/10
       
            mot_wat = mot_amp*mot_vol
    # batt_id = ina260._raw_voltage

    #total output
        rel_amp = 8.125
        rel_vol = ina261.voltage
        rel_wat = rel_vol*rel_amp

     #  batt
        batt_vol = ina264.voltage
        batt_wat = ina264.power/10
        batt_amp = ina264.current/10

        

        print("\nTemperature: %0.1f C" % (bme680.temperature + temperature_offset))
        print("Gas: %d ohm" % bme680.gas)
        print("Humidity: %0.1f %%" % bme680.relative_humidity)
        print("Pressure: %0.3f hPa" % bme680.pressure)
        print("Altitude = %0.2f meters" % bme680.altitude)


        
        print("STATUS: ",ina260.alert_limit )
        print(
            "||| Bike ||| Current: %.2f A Voltage: %.2f V Power:%.2f W"
            % (mot_amp, mot_vol, mot_wat)
        )
        print("----------------------------------------------------------------------")
        print(
            "||| Battery ||| Current: %.2f A Voltage: %.2f V Power:%.2f W"
            % (batt_amp,batt_vol, batt_wat)
        )
        print("----------------------------------------------------------------------")

        print("======================================================================")
        print(
            "||| TOTAL POWER OUTPUT ||| Current: %.2f A Voltage: %.2f V Power:%.2f W"
            % (rel_amp, rel_vol, rel_wat)
        )
        print(" ")
        print(" ")

        
        if mot_vol > 0:
            requests.post(url, json= {'id':idnum,'batt_amp': batt_amp, 'batt_vol': batt_vol, 'batt_wat': batt_wat,'mot_amp': mot_amp, 'mot_vol': mot_vol, 'mot_wat': mot_wat,'rel_amp': rel_amp, 'rel_vol': rel_vol, 'rel_wat': rel_wat, 'temp': temp, 'hum': hum, 'voc': voc, 'press':press } )


        time.sleep(3)






if __name__ == "__main__":
    asyncio.run(main())