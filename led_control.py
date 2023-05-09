
import RPi.GPIO as GPIO
from time import *

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(21, GPIO.OUT)

def led_control_on():
    on = GPIO.output(21, GPIO.HIGH)
    return on

def led_control_off():
    off = GPIO.output(21, GPIO.LOW)
    return off



    
