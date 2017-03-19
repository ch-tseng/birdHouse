#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time, os
import json, datetime
import logging


#---------------------------------------------------------
#You don't have to modify the code below------------------
#---------------------------------------------------------
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


pinLED_RED = 19
pinLED_GREEN = 26
pinLED_BLUE = 13

GPIO.setup(pinLED_RED ,GPIO.OUT)
GPIO.setup(pinLED_GREEN ,GPIO.OUT)
GPIO.setup(pinLED_BLUE ,GPIO.OUT)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.output(pinLED_GREEN, GPIO.LOW)
GPIO.output(pinLED_BLUE, GPIO.LOW)
GPIO.output(pinLED_RED, GPIO.LOW
)

