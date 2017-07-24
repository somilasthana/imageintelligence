# coding: utf-8



import os
from urlparse import urlparse # For Parsing Image URLs
import urllib2 # For pulling Images
from flask import Flask,render_template, request,json, g
from PIL import Image
import cStringIO
import random 
import datetime
from model import *
from errorhandling import * 
from processing import *
app = Flask(__name__)



@app.route('/')
@app.route('/home')

def hello():
    return 'Welcome to Image Processing Service'



class RequestResponseInfo:
    
    def __init__(self):
       
        requestformat = { "images" : [ "http://example.com/image1.jpg", "http://example.com/image2.jpg", "http://badurl.com/image3.jpg"] }
        
        responseformat =  { "results": [ { "url": "http://example.com/image1.jpg", "classes": [ { "class": "person", "confidence": 0.8641},{ "class": "dog", "confidence": 0.00516 }]},{"url": "http://example.com/image2.jpg","classes": [{"class": "cat","confidence": 0.2115}]},{"url": "http://example.badurl.com/image3.jpg","error": "Invalid URL"}]}
        
        self.paramform = { "param" :[ {"Description": "Request Format For API", "Request Format": requestformat},
                           {"Description": "Response Format From API", "Response Format" : responseformat} ]
                         }
    
    def getInfo(self):
        return json.dumps(self.paramform)
    
@app.route('/getinfo')
def getInfo():
    rinfo = RequestResponseInfo()
    return rinfo.getInfo()

@app.route('/simpleimageclassify', methods=['POST'])
def imageclassify():

    restpayload = InputProcessor(request).process()
    downloadedimages = ImageDownloader(restpayload).location()
    return ImageObjectDetector(downloadedimages).detect()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
	
	

