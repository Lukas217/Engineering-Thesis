import w1thermsensor

def ds_temp():

    sensor = w1thermsensor.W1ThermSensor()   
    ds_temp = sensor.get_temperature()
    return ds_temp

