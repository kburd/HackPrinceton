import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
import picamera
import requests
import json
import serial
import time
import picamera.array
import cv2
import numpy as np
import matplotlib.pyplot as pt
import RPi.GPIO as GPIO

#JReynoldsUD
#FarSightWalker1

##Auto correct
ser = serial.Serial("/dev/ttyACM1",9600,timeout = 1)
camera = picamera.PiCamera()
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)
GPIO.setup(27, GPIO.OUT, initial=GPIO.LOW)

def getGPSLocation():
    send_url = 'http://freegeoip.net/json'
    r = requests.get(send_url)
    j = json.loads(r.text)
    lat = j['latitude']
    lon = j['longitude']

    link = "https://www.google.com/maps/?q="+str(lat)+","+str(lon)
    
    return link

def emailAlert(alertType):

    emailList = ["kburd@udel.edu", "vvazir@udel.edu", "jkr@udel.edu"]

    for toaddr in emailList:
    
        fromaddr = "farsightsafety@gmail.com"
         
        msg = MIMEMultipart()
         
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "Safety Alert!"

        if(alertType == "F"):
            insert = "We have detected a potential fall."
        elif(alertType == "W"):
            insert = "We have detected that they may be in distress."
        elif(alertType == "P"):
            insert = "We do not currently detect them with the walk."

        body = "The FarSight Walker has detected a potential issue with your Loved One, Kaleb M Burd. " + insert + " There last known GPS Location and the last picture taken are listed below. Feel free to reach out to us for more information\n\n" + getGPSLocation() 
        msg.attach(MIMEText(body, 'plain'))
         
        filename = "image.jpg"
        takeImage(filename)
        attachment = open(filename, "rb")
         
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
         
        msg.attach(part)
         
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(fromaddr, "SafetySightFar")
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()

def killLazers():
    
    GPIO.output(27, GPIO.LOW)

def startLazers():

    GPIO.output(27, GPIO.HIGH)

def personFinder():

    startLazers()
    
    with picamera.array.PiRGBArray(camera) as stream:
        
        camera.capture(stream, format='bgr')
        image = stream.array
        
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        lower_red = np.array([150,150,70])
        upper_red = np.array([255,255,255])
        
        mask = cv2.inRange(hsv, lower_red, upper_red)

    killLazers()

    height = len(image)
    width = len(image[0])

    leftR=-1
    leftC=-1

    rightR=-1
    rightC=-1
    for row in range(750,1000):
        for col in range(500,1250):
            pixel = mask[row][col]
            if (pixel):
                if (col<750):
                    if (rightR==-1 or rightC==-1):
                        rightR=row
                        rightC=col
                    else:
                        if (np.abs(rightR-row)>5 and row>rightR):
                            rightR=row
                        if (np.abs(rightC-col)>5 and col>rightC):
                            rightC=col
                else:
                    if (leftR==-1 or leftC==-1):
                        leftR=row
                        leftC=col
                    else:
                        if (np.abs(leftR-row)>10 and row>leftR):
                            leftR=row
                        if (np.abs(leftC-col)>10 and col>leftC):
                            leftC=col
    
    if (rightC !=-1 and rightR !=1) or( leftC!=-1 and leftR!=-1):
        return 1
    else:
        return 0

def takeImage(filename):
    camera.capture(filename)

def readSerial():
    while ser.in_waiting:
        read = ser.read()
        return read

def readSwitch():
    return GPIO.input(17)
    
def main():
    while True:
        x= readSerial()
        if (x is not None and readSwitch() == 1):
            print(x)
            if(x == "F"):
                emailAlert(x)
            elif(x == "W"):
                emailAlert(x)
            elif(x == "P"):
                personFound = personFinder()
                if(personFound == 0):
                    emailAlert(x)
            print("Done")

main()
    
