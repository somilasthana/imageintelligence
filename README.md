Image Detection Service Framework

Used caffe pretrained models to classify images pulled from internet
1. bvlc_reference_caffenet
2. bvlc_alexnet

More details on these premodels can be found at http://caffe.berkeleyvision.org/model_zoo.html

Input : list of urls with optional "threshold" value

{
  "images": [
    "http://example.com/image1.jpg"
  ],
  "threshold": 0.0001
}

Response : classification 
{
	"status": "INPUT_VALIDATION_SUCCESS",
	"results": [{
		"url": "https://badurl.com/image1.jpg",
		 "classes": [
                 {
                    "class": "person",
                    "confidence": 0.8641
                 },
                 {
                    "class": "dog",
                    "confidence": 0.00516
                 }
          ]
		
	}]
}

Labels were taken from https://github.com/Evolving-AI-Lab/ppgn/blob/master/misc/map_clsloc.txt

Running instructions 
1. from caffee python directory ie 
   /home/centos/caffe/python run:
   
   python imageintelligence/app.py 
      
2. API  can be accessed from http://X.X.X.X:8080/simpleimageclassify ( ImageProcessingTesting.ipynb has more details)

Designed such that error handling is done smoothly not distrupting the logical flow of the application.
Avoid using exception errors instead captured and pushed the status. Therefore, no "if block statements" required in app.py
Coded to capture as many failure scenarios. Used standard native python models to parse url, download.
Both hands-on and unittest framework used but more can be done. Instead of reading synset_words.txt in app.py
created a serializable hash map using python pickles, that can be read directly.

TODO:

1. More models could be tried caffe has many pretrained models. Can models be mixed in someway to get better results.
Further, models need to be static and initialized only once.

2. Many test scenarios still need to be implemented.

3. GPU resource was not available, did not install the libraries therefore, could not test on GPU settings. But I think its not difficult cafee supports it.
