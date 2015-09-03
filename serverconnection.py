# import the necessary packages
from pyimagesearch.coverdescriptor import CoverDescriptor
from pyimagesearch.covermatcher import CoverMatcher
from picamera.array import PiRGBArray
from picamera import PiCamera
from musicplayer import MusicPlayer
import musicplayer
import argparse
import glob
import csv
import cv2
import os
import time
import socket

class ServerConnection:

    def convert_to_bytes(self,no):
        result = bytearray()
        result.append(no & 255)
        for i in range(3):
            no = no >> 8
            result.append(no & 255)
        return result          
                

    def search(self, imageArray):
        filename = "query.png"
        cv2.imwrite(filename,imageArray)
        #imgBuffer = cv2.imencode(".png",imageArray)
        s = socket.socket()
        host = "192.168.1.141"
        port = 60002        
        s.connect((host, port))
        print("connected")

        if os.path.exists(filename):
            length = os.path.getsize(filename)
            s.send(self.convert_to_bytes(length)) # has to be 4 bytes
            with open(filename, 'rb') as infile:
               d = infile.read(1024)           
               while d:
                   s.send(d)
                   d = infile.read(1024)
                
     
        uriBytes = s.recv(1024)
        uriString = uriBytes.decode("utf8");
        return uriString


 






