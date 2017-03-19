#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time, os
import json, datetime
import logging
import paho.mqtt.client as mqtt
from libraryCH.device.camera import PICamera
from libraryCH.device.lcd import ILI9341
from libraryCH.device.sensors import DHT

#PIR觸動後，每段錄影的長度(分鐘)
minVideoLength = 3
#PIR觸動後，是否要持續不斷的錄影？若為True, 則countVideos沒有作用
recordNeverStop = False
#PIR觸動後，要錄幾段影片
countVideos = 2
#PIR觸動後，要等幾秒再開始錄影
waitDelaySeconds = 0

#LCD顯示設定------------------------------------
lcd = ILI9341(LCD_size_w=240, LCD_size_h=320, LCD_Rotate=90)

#開機及螢幕保護畫面
screenSaverDelay = 30  #刷卡顯示, 幾秒後回到螢幕保護畫面
lcd.displayImg("rfidbg.jpg")

#MQTT設定---------------------------------------
ChannelPublish = "Door-camera"
MQTTuser = "chtseng"
MQTTpwd = "chtseng"
MQTTaddress = "akai-chen-pc3.sunplusit.com.tw"
MQTTport = 1883
MQTTtimeout = 60

volumeVoice = 2000

#拍照設定--------------------------------------
#儲放相片的主目錄
picturesPath = "/var/www/html/birdhouse/"
#相機旋轉角度
cameraRotate = 0
#拍攝的相片尺寸
photoSize = (1280, 720)
#一次要連拍幾張
numPics = 10
#間隔幾毫秒
picDelay = 0.5 

#---------------------------------------------------------
#You don't have to modify the code below------------------
#---------------------------------------------------------

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

camera = PICamera()
camera.CameraConfig(rotation=cameraRotate)  
camera.cameraResolution(resolution=photoSize)

#DHT Sensor
pinDHT = 4  #GPIO pin
typeDHT = 22
sensorDHT = DHT(type=22, pin=4)

#LCD設定
lcd_LineNow = 0
lcd_lineHeight = 30  #行的高度
lcd_totalLine = 8  # LCD的行數 (320/30=8)
screenSaverNow = False

#上次讀取到TAG的內容和時間
lastUIDRead = ""
lastTimeRead = time.time()

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

#將行數轉為pixels
def lcd_Line2Pixel(lineNum):
    return lcd_lineHeight*lineNum

#LCD移到下一行, 若超過設定則清螢幕並回到第0行
def lcd_nextLine():
    global lcd_LineNow
    lcd_LineNow+=1
    if(lcd_LineNow>(lcd_totalLine-1)):
        lcd.displayClear()
        lcd_LineNow = 0

#LCD顯示刷卡內容
def displayUser(empNo, empName, uid):
    global lcd_LineNow

    st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M')
    if(lcd_LineNow>0): lcd_nextLine()

    lcd.displayText("cfont1.ttf", fontSize=20, text=st, position=(lcd_Line2Pixel(lcd_LineNow), 180), fontColor=(253,244,6) )
    lcd.displayText("cfont1.ttf", fontSize=20, text=empNo, position=(lcd_Line2Pixel(lcd_LineNow), 110) )
    lcd.displayText("cfont1.ttf", fontSize=26, text=empName, position=(lcd_Line2Pixel(lcd_LineNow), 10) )

    lcd_nextLine()
    lcd.displayText("cfont1.ttf", fontSize=22, text=uid, position=(lcd_Line2Pixel(lcd_LineNow), 10), fontColor=(88,88,87) )


def takePictures(saveFolder="others"):
    global picDelay, numPics, picturesPath

    if(os.path.isdir(picturesPath+saveFolder)==False):
        os.makedirs(picturesPath+saveFolder)

    savePath = picturesPath + saveFolder + "/" + str(time.time())
    for i in range(0,numPics):
        camera.takePicture(savePath + "-" + str(i) + ".jpg")
        logger.info("TakePicture " + str(i) + " to " + savePath + "-" + str(i) + ".jpg")
        time.sleep(picDelay)

def on_connect(mosq, obj, rc):
    mqttc.subscribe("Door-camera", 0)
    print("rc: " + str(rc))

def on_message(mosq, obj, msg):
    global message, screenSaverNow
    #print(msg.topic + "/ " + str(msg.qos) + "/ " + str(msg.payload))
    msgReceived = str(msg.payload.decode("utf-8"))
    print ("Received: " + msgReceived)
    logger.info("MQTT received: " + msgReceived)
    lastTimeRead = time.time()

    if(is_json(msgReceived)==True):
        jsonReply = json.loads(msgReceived)
        screenSaverNow = False

        for i in range(0, len(jsonReply)):
            logger.info('EmpNo:'+jsonReply[0]["EmpNo"]+'  EmpCName:'+jsonReply[i]["EmpCName"]+' Uid:'+jsonReply[i]["Uid"])
            displayUser(jsonReply[i]["EmpNo"], jsonReply[i]["EmpCName"], jsonReply[i]["Uid"])
            takePictures(jsonReply[i]["EmpNo"])
    else:
        lcd.displayText("cfont1.ttf", fontSize=24, text=msgReceived, position=(lcd_Line2Pixel(0), 10) )
        logger.info('Unknow ID: ' + msgReceived)

def playVoices():
    dt = list(time.localtime())
    nowHour = dt[3]
    nowMinute = dt[4]

    #mp3Number = str(random.randint(1, 3))

    #if(nowHour<10 and nowHour>=6):
    #    os.system('omxplayer --no-osd voice/gowork' + mp3Number + '.mp3')
    #if(nowHour<22 and ((nowHour==17 and nowMinute>30) or (nowHour>=18)) ):
    #    os.system('omxplayer --no-osd voice/afterwork' + mp3Number + '.mp3')
    os.system('omxplayer --no-osd --vol '+str(volumeVoice) + ' voice/bird1.mp3')

def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))
    logger.info("MQTT subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
    print(string)

def youtubeStream(url, secret):
    urlString = "sudo raspivid -o - -t 0 -vf -hf -fps 30 -b 6000000 | avconv -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -f h264 -i - -vcodec copy -acodec aac -ab 128k -g 50 -strict experimental -f flv rtmp://" + url + "/" + secret
    os.system(urlString)

def MOTION(pinPIR):
    print("found birds!!!")
    #if(camera.busy()==False):
    #    camera.videoRecord(videoPath="/var/www/html/birdhouse/", startDelaySeconds=waitDelaySeconds, Continuous=recordNeverStop, 
    #        ContinusTotalCount=countVideos, videoMinutesLength=minVideoLength)
    youtubeStream(url="rtmp://a.rtmp.youtube.com/live2", secret="ysqc-sx8y-thq9-de7b")

temperature, humandity = sensorDHT.getData()

GPIO.output(pinLED_BLUE, GPIO.HIGH)

#Register----------------------------------------------
GPIO.add_event_detect(pinPIR, GPIO.RISING, callback=MOTION)


'''
mqttc = mqtt.Client()

# Assign event callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

# Connect
mqttc.username_pw_set(MQTTuser, MQTTpwd)
mqttc.connect(MQTTaddress, MQTTport, MQTTtimeout)
'''

i=0
while True:
    #lcd.displayImg("rfidbg.jpg")
    print ("{} PIR:{} Recording:{} ".format( i, GPIO.input(pinPIR), camera.busy()))
        
    #takePictures("birds")    
    time.sleep(1)
    i += 1

# Continue the network loop
#mqttc.loop_forever()
