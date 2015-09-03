# import the necessary packages
from pyimagesearch.tempimage import TempImage
from picamera.array import PiRGBArray
from picamera import PiCamera
from serverconnection import ServerConnection
from musicplayer import MusicPlayer
import argparse
import warnings
import datetime
import imutils
import json
import time
import cv2

# filter warnings, load the configuration and initialize the Dropbox
warnings.filterwarnings("ignore")
conf = json.load(open("conf.json"))


# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = tuple(conf["resolution"])
camera.framerate = conf["fps"]
camera.exposure_mode = "off"
camera.shutter_speed = 12000
camera.awb_mode = 'auto'
camera.iso = 600
camera.contrast = 50

rawCapture = PiRGBArray(camera, size=tuple(conf["resolution"]))

mp = MusicPlayer()
mp.connect()

currentUrl = ""

server = ServerConnection()

# allow the camera to warmup, then initialize the average frame, last
# uploaded timestamp, and frame motion counter
print("[INFO] warming up...")
time.sleep(conf["camera_warmup_time"])

#bg = cv2.imread("query.png")
#bg = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)
#bg = cv2.GaussianBlur(imutils.resize(bg, width=320), (21, 21), 0)
bg = None
lastUploaded = datetime.datetime.now()
motionCounter = 0
currentCountourArea = 0
pingCounter = 0

# capture frames from the camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # grab the raw NumPy array representing the image and initialize
        # the timestamp and occupied/unoccupied text
        fullsizeFrame = f.array
        cv2.circle(fullsizeFrame,(450,570),760,(255,255,255),500,cv2.LINE_AA)
        timestamp = datetime.datetime.now()
        text = "No object"

        # resize the frame, convert it to grayscale, and blur it
        fullsizeGray = cv2.cvtColor(fullsizeFrame, cv2.COLOR_BGR2GRAY)
        resizedGray = imutils.resize(fullsizeGray, width=500)                          
        gray = cv2.GaussianBlur(resizedGray, (21, 21), 0)

        # if the average frame is None, initialize it
        if bg is None:
                print("[INFO] starting background model...")
                #avg = gray.copy().astype("float")
                bg = gray.copy().astype("float")
                rawCapture.truncate(0)
                continue

        # accumulate the weighted average between the current frame and
        # previous frames, then compute the difference between the current
        # frame and running average
        # cv2.accumulateWeighted(gray, avg, 0.5)
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(bg))
      
        # threshold the delta image, dilate the thresholded image to fill
        # in holes, then find contours on thresholded image
        thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255,
                cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        (_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)

        crop_img = None

           
        # loop over the contours
        for c in cnts:
                                
                # if the contour is too small, ignore it
                if cv2.contourArea(c) < conf["min_area"]:
                      continue

                # compute the bounding box for the contour, draw it on the frame,
                # and update the text
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(resizedGray, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            
                text = "Possible object"
                
                #if cv2.contourArea(c) == currentCountourArea:
                #        text = "No new object"
                #        continue
                
                currentCountourArea = cv2.contourArea(c)   
                crop_img = fullsizeGray[y*2:y*2+h*2, x*2:x*2+w*2]                
                #crom_img = imutils.resize(crop_img, width=500)

        # draw the text and timestamp on the frame
        ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
        cv2.putText(resizedGray, "Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
  

        print(text)
        if text == "Possible object":
                print("Searching for matching audio!")
                url = server.search(crop_img)
                print(url)
                cv2.putText(resizedGray, "Response: {}".format(url), (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                if url != "nothingfound" and url != currentUrl:                        
                        mp.play(url)
                        currentUrl = url

        if text == "No object":
                mp.stop()
                currentUrl = ""
                   
               
        pingCounter += 1
        if pingCounter > 20:
                mp.ping()
                pingCounter = 0
      

        # check to see if the room is occupied
        if text == "Motion":
                motionCounter += 1                

                

        # check to see if the frames should be displayed to screen
        #if conf["show_video"]:
                # display the security feed
                #if(crop_img != None):
                #cv2.imshow("Security Feed", crop_img)
                #cv2.imshow("Diff", frameDelta)
                #cv2.imshow("Thresh", thresh)
                
                #key = cv2.waitKey(1) & 0xFF

                # if the `q` key is pressed, break from the lop
                #if key == ord("q"):
                #        break

        # clear the stream in preparation for the next frame

        rawCapture.truncate(0)
