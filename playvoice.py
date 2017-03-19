#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time, os
import json, datetime
import logging
from libraryCH.device.sensors import DHT

volumeVoice = 2000

#---------------------------------------------------------
#You don't have to modify the code below------------------
#---------------------------------------------------------
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


pinLED_RED = 19
pinLED_GREEN = 26
pinLED_BLUE = 13

pinPIR = 6

GPIO.setup(pinLED_RED ,GPIO.OUT)
GPIO.setup(pinLED_GREEN ,GPIO.OUT)
GPIO.setup(pinLED_BLUE ,GPIO.OUT)
GPIO.setup(pinPIR ,GPIO.IN)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

#DHT Sensor
pinDHT = 4  #GPIO pin
typeDHT = 22
sensorDHT = DHT(type=22, pin=4)

#logging記錄
logger = logging.getLogger('msg')
hdlr = logging.FileHandler('/home/pi/birdHouse/msg.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

#判斷是否為JSON格式
def is_json(myjson):
    try:
        json_object = json.loads(myjson)

    except ValueError:
        return False

    return True

def playVoices():
    dt = list(time.localtime())
    nowHour = dt[3]
    nowMinute = dt[4]

    #mp3Number = str(random.randint(1, 3))

    #if(nowHour<10 and nowHour>=6):
    #    os.system('omxplayer --no-osd voice/gowork' + mp3Number + '.mp3')
    #if(nowHour<22 and ((nowHour==17 and nowMinute>30) or (nowHour>=18)) ):
    #    os.system('omxplayer --no-osd voice/afterwork' + mp3Number + '.mp3')
    if(nowHour<17 and nowHour>4):
        os.system('omxplayer --no-osd --vol '+str(volumeVoice) + ' voice/sparrow.mp3')

def MOTION(pinPIR):
    print("found birds!!!")
    #if(camera.busy()==False):
    #    camera.videoRecord(videoPath="/var/www/html/birdhouse/", startDelaySeconds=waitDelaySeconds, Continuous=recordNeverStop, 
    #        ContinusTotalCount=countVideos, videoMinutesLength=minVideoLength)
    #youtubeStream(url="rtmp://a.rtmp.youtube.com/live2", secret="ysqc-sx8y-thq9-de7b")

temperature, humandity = sensorDHT.getData()

#GPIO.output(pinLED_GREEN, GPIO.HIGH)
#GPIO.output(pinLED_BLUE, GPIO.HIGH)
#GPIO.output(pinLED_RED, GPIO.HIGH)

#Register----------------------------------------------
GPIO.add_event_detect(pinPIR, GPIO.RISING, callback=MOTION)


playVoices()
i=0
while True:
    print ("{} PIR:{} ".format( i, GPIO.input(pinPIR)))
    playVoices()

    time.sleep(15)
    i += 1

