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

##Auto correct
ser = serial.Serial("/dev/ttyACM0",9600,timeout = 1)
camera = picamera.PiCamera()

def getGPSLocation():
    send_url = 'http://freegeoip.net/json'
    r = requests.get(send_url)
    j = json.loads(r.text)
    lat = j['latitude']
    lon = j['longitude']
    return lat,lon

def emailAlert():
    fromaddr = "farsightsafety@gmail.com"
    toaddr = "kburd@udel.edu"
     
    msg = MIMEMultipart()
     
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Safety Alert!"

    lat,lon = getGPSLocation() 
    body = "The Far Sight Walker has detected a potential issue with your Loved One, Kaleb M Burd. There last known GPS Coordinates are:\nLatitude: %f\nLongitude: %f\nBelow is the last picture taken. Feel free to reach out to us for more information"%(lat,lon)
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

def personFinder():
    
    with picamera.array.PiRGBArray(camera) as stream:
        
        camera.capture(stream, format='bgr')
        image = stream.array
        
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        lower_red = np.array([150,150,70])
        upper_red = np.array([255,255,255])
        
        mask = cv2.inRange(hsv, lower_red, upper_red)

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
    
def main():
    previousCall = None
    while True:
        x= readSerial()
        if (x is not None): # and x != previousCall):
            print(x)
            if(x == "F"):
                emailAlert()
            elif(x == "W"):
                emailAlert()
            elif(x == "P"):
                personFound = personFinder()
                if(personFound == 0):
                    emailAlert()
            print("Done")
        previousCall = x

main()
    
