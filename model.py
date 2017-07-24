import numpy as np
from PIL import Image
caffe_root = '../'  # this file should be run from {caffe_root}/examples (otherwise change this line)
import sys
sys.path.insert(0, caffe_root + 'python')
import caffe
import json
import logging
from sklearn.externals import joblib
from errorhandling import * 
'''
Using bvlc_reference_caffenet and bvlc_alexnet pretrained models

'''

class BvlcModel:
    
    def __init__(self):
        
        '''
        Initialize the bvlc model
        '''
        
        model_def = '/home/centos/caffe/models/bvlc_reference_caffenet/deploy.prototxt'
        model_weights = '/home/centos/caffe/models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel'
        mean_file = '/home/centos/caffe/python/caffe/imagenet/ilsvrc_2012_mean.npy'

        self.net = caffe.Net(model_def,      # defines the structure of the model
                             model_weights,  # contains the trained weights
                             caffe.TEST)     # use test mode (e.g., don't perform dropout)
        
        self.net.blobs['data'].reshape(50,        # batch size
                                       3,         # 3-channel (BGR) images
                                       227, 227)  # image size is 227x227
        
        # create transformer for the input called 'data'
        self.transformer = caffe.io.Transformer({'data': self.net.blobs['data'].data.shape})

        mu = np.load(mean_file)
        mu = mu.mean(1).mean(1)  # average over pixels to obtain the mean (BGR) pixel values
        self.transformer.set_transpose('data', (2,0,1))  # move image channels to outermost dimension
        self.transformer.set_mean('data', mu)            # subtract the dataset-mean value in each channel
        self.transformer.set_raw_scale('data', 255)      # rescale from [0, 1] to [0, 255]
        self.transformer.set_channel_swap('data', (2,1,0))  # swap channels from RGB to BGR
        
    def predict(self, image, nclass=5):
        
        '''
        classify image by taking top 5 outputs
        '''
        
        transformed_image = self.transformer.preprocess('data', image)
        # copy the image data into the memory allocated for the net
        self.net.blobs['data'].data[...] = transformed_image
        ### perform classification
        output = self.net.forward()
        # the output probability vector for the first image in the batch
        output_prob = output['prob'][0]
        # sort top five predictions from softmax output
        top_inds = output_prob.argsort()[::-1][:nclass]  # reverse sort and take five largest items
        return (top_inds,output_prob)

class AlexNetModel:

    '''
        Initialize the alexnet model
    '''
    
    def __init__(self):
        model_def_alexnet = '/home/centos/caffe/models/bvlc_alexnet/deploy.prototxt'
        model_weights_alexnet = '/home/centos/caffe/models/bvlc_alexnet/bvlc_alexnet.caffemodel'
        mean_file = '/home/centos/caffe/python/caffe/imagenet/ilsvrc_2012_mean.npy'
        
        self.net_alexnet = caffe.Net(model_def_alexnet,      # defines the structure of the model
                                     model_weights_alexnet,  # contains the trained weights
                                     caffe.TEST)     # use test mode (e.g., don't perform dropout)
        
        # set the size of the input (we can skip this if we're happy
        #  with the default; we can also change it later, e.g., for different batch sizes)
        self.net_alexnet.blobs['data'].reshape(50,        # batch size
                                               3,         # 3-channel (BGR) images
                                               227, 227)  # image size is 227x227

        # create transformer for the input called 'data'
        self.transformer = caffe.io.Transformer({'data': self.net_alexnet.blobs['data'].data.shape})

        mu = np.load(mean_file)
        mu = mu.mean(1).mean(1)  # average over pixels to obtain the mean (BGR) pixel values
        self.transformer.set_transpose('data', (2,0,1))  # move image channels to outermost dimension
        self.transformer.set_mean('data', mu)            # subtract the dataset-mean value in each channel
        self.transformer.set_raw_scale('data', 255)      # rescale from [0, 1] to [0, 255]
        self.transformer.set_channel_swap('data', (2,1,0))  # swap channels from RGB to BGR
        
    def predict(self, image, nclass=5):
        
        '''
        classify image take top 5 outputs
        '''
        
        transformed_image = self.transformer.preprocess('data', image)
        # copy the image data into the memory allocated for the net
        self.net_alexnet.blobs['data'].data[...] = transformed_image
        
        ### perform classification
        output_alex = self.net_alexnet.forward()
        
        output_prob_alex = output_alex['prob'][0]  # the output probability vector for the first image in the batch
        
        # sort top five predictions from softmax output
        top_inds = output_prob_alex.argsort()[::-1][:nclass]  # reverse sort and take five largest items
        return (top_inds,output_prob_alex)


class ImageObjectDetector:
    
    def __init__(self, input_to_process):
        '''
        load synset file ( to get class information )
        parameter: (url, url_local_filesystem_location, error)
        '''
        self.inputimagelist = input_to_process[0]
        self.code = input_to_process[1]
        self.threshold = input_to_process[2]
        self.classInfo = joblib.load('/home/centos/caffe/data/metadata.pkl')
        self.labels = joblib.load('/home/centos/caffe/data/label.pkl')
        caffe.set_mode_cpu()
        self._model = BvlcModel()
        #self._model = AlexNetModel() # bit slow compared to BvlcModel

        self._flogger()

    def _flogger(self):
        self._logger = logging.getLogger('ImageObjectDetector')
        self._logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)

   
    def detect(self):
        '''
        Apply the model but filterout below threshold prob values
        '''
        
        imagedetection = {}
        imagedetection.setdefault("results", [])
        imagedetection.setdefault("status", self.code.reason()[0])
        for url,urlattr in self.inputimagelist.get():
           
            
            if(urlattr[1].isnerrror()):
                self._logger.info('Analyzing Image %s ', urlattr[0])
                image = caffe.io.load_image(urlattr[0])
                (top_inds,output_prob) = self._model.predict(image) 

                pred_map = {"url": url, "classes": [] }
                for prob, synsetv in zip(output_prob[top_inds], self.labels[top_inds]):
                    if prob > self.threshold:
                        pred_map["classes"].append({ "class": self.classInfo[synsetv], "confidence" : str(prob.round(4))})
                    else:
                        break
                imagedetection["results"].append(pred_map)
            else:
                self._logger.info('Failed url %s', url)
                pred_map = {"url": url, "classes": [] , "error": urlattr[1].reason()[0]}
                imagedetection["results"].append(pred_map)
                
        return json.dumps(imagedetection)     
