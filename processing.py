# coding: utf-8

import os
from urlparse import urlparse # For Parsing Image URLs
import urllib2 # For pulling Images
from PIL import Image
import cStringIO
import random 
import datetime
import json
from errorhandling import * 
import logging

                

class ImageLocations:
    
    def __init__(self):
        self.urlcontentlocation = {}
    
    def store(self, url, location, errObj):
        if not url in self.urlcontentlocation:
            self.urlcontentlocation[url] = (location,errObj)
            
    def get(self):
        for k,v in self.urlcontentlocation.iteritems():
            yield k,v


class ImageDownloader:
    
    def __init__(self, url_n_attr):

        self.image_list = url_n_attr[0]
        self.parsecode = url_n_attr[1]
        self.threshhold = url_n_attr[2]
        self.past_download = {}
        self._flogger()

    def _flogger(self):
        self._logger = logging.getLogger('ImageDownloader')
        self._logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)


 
    def location(self):
        '''
        Pull the image content and store it locally. Check for Duplicate entries avoid it
        For error cases record it
        '''
        
        imagelocation = ImageLocations()
        for url in self.image_list.iterulist():
            if not url in self.past_download:
                try:
                    req = urllib2.Request(url)
                    imgdata = urllib2.urlopen(url).read()
                    img = Image.open(cStringIO.StringIO(imgdata))
                    # EPOC + Random number are added for each download to mitigate issue like two different url have the same image name : cat_gray.jpg 
                    rint = int(datetime.datetime.now().strftime("%s"))*random.randint(0,100000)
                    imgfilename = ConstantValue.CAFFE_ROOT.value + "/" + ConstantValue.IMAGE_DOWNLOADFOLDER.value + "/" + str(rint) + "_" + url.split('/')[-1] 
                   
                    img.save(imgfilename)
                    self.past_download.setdefault(url, imgfilename)
                    imagelocation.store(url, imgfilename, ErrorReason(ConstantValue.IMAGE_DOWNLOAD_SUCCESS))
                    
                except Exception as e:
                    
                    self._logger.info('Url %s failed to download Error %s', url, str(e))
                    imagelocation.store(url, None, ErrorReason(ConstantValue.IMAGE_DOWNLOAD_ERROR))
                    continue
            else:
                imagelocation.store(url,self.past_download[url], ErrorReason(ConstantValue.IMAGE_DOWNLOAD_SUCCESS))
            
        return (imagelocation,self.parsecode,self.threshhold)
                    

class ImagesUrl:
    
    def __init__(self, urlinputlist):
        self.urllist = urlinputlist
    
    # We only give urls that are valid for download
    def iterulist(self):
        for url in self.urllist:
            if self.urllist[url].isnerrror():
                yield url


class ImageUrlCheck:
    
    def __init__(self, inputdata):
        self.inputdata =  inputdata
        
    def image_url_parse(self, b):
        '''
        Image URL Parsing
        parameter : url
        Assumption only jpg and jpeg supported
        '''
        result = urlparse(b)
        
        if not (result.scheme ==  ConstantValue.HTTP_PROTOCOL.value or result.scheme == ConstantValue.HTTPS_PROTOCOL.value ):
            return (b, ErrorReason(ConstantValue.MISSING_HTTP_PROTOCOL))
        
        #if not((ConstantValue.MISSING_DOT_COM.value in result.netloc) or (ConstantValue.MISSING_ORG.value in result.netloc)):
        #    return (b, ErrorReason(ConstantValue.INCORRECT_URL_FORMAT))
        
        if ConstantValue.JPG_FORMAT.value in result.path or ConstantValue.JPEG_FORMAT.value in result.path:
            return (b, ErrorReason(ConstantValue.IMAGE_URL_VALID))
        else:
            return (b, ErrorReason(ConstantValue.MISSING_IMAGE_FORMAT))
    
        
    def getUrl(self):
        '''
        Validate and parse request object
        '''
        # threshold setting
        threshold = 0.0

        try:
            reqjson = json.loads(self.inputdata)
        except ValueError:
            return (ImagesUrl({}), ErrorReason(ConstantValue.JSON_PARSE_ERROR),threshold)
        
        if not ConstantValue.IMAGESFIELD.value in reqjson:
            return (ImagesUrl({}), ErrorReason(ConstantValue.MISSING_IMAGES_FIELD),threshold)
        
        self.urllist  = reqjson[ConstantValue.IMAGESFIELD.value]
        
        if(len(self.urllist) == 0):
            return (ImagesUrl({}), ErrorReason(ConstantValue.EMPTY_IMAGE_FIELD),threshold)

        if ConstantValue.THRESHOLD.value in reqjson:
            threshold = float(reqjson[ConstantValue.THRESHOLD.value])
            
        if threshold < 0.0:
            threshold = 0.0
 
        urlmap = {}
        # Segregate bad urls from good one
        for url in self.urllist:
            output = self.image_url_parse(url)
            urlmap.setdefault(output[0], output[1])
            #>>print(output[0],output[1])
            #http://example.com/image1.jpg , {"code": "IMAGE_URL_VALID", "description": "image url is valid"}
            #http://example.com/image2.jpeg, {"code": "IMAGE_URL_VALID", "description": "image url is valid"}
            #http://badurl.com/image3, {"code": "MISSING_IMAGE_FORMAT", "description": "Image format is not jpg or jpeg"}
        
        summary = [truth.isnerrror() for truth in urlmap.values()]
        
        return (ImagesUrl(urlmap), ErrorReason(ConstantValue.INPUT_VALIDATION_SUCCESS), threshold) if not False in summary else (ImagesUrl(urlmap), ErrorReason(ConstantValue.INPUT_VALIDATION_FAILED), threshold)
        
class InputProcessor:

    '''
         It parses the request data, finds valid urls, pull image and store it locally
         parameter request object.
    '''
    
    def __init__(self, irequest):
        self.inputdata = irequest.data
        self._flogger()

    def _flogger(self):
        self._logger = logging.getLogger('JsonInputParser')
        self._logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)
       
    def process(self):
        # On success eval_urllist has a valid list of urls, image location for each, incase download failed
        # that information is stored too.
        self._logger.info('parsing json %s' ,self.inputdata)
        eval_urllist = ImageUrlCheck(self.inputdata).getUrl()
        return eval_urllist
