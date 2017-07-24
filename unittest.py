import unittest
from model import *
from errorhandling import *
from processing import *

class TestImageProcessingService(unittest.TestCase):

    def test_errorcode(self):
        errorcodes = ImageProcessingErrorCodes()
        self.assertEqual(errorcodes.error(4)[0], 'MISSING_HTTP_PROTOCOL')
        self.assertEqual(errorcodes.error(10)[0], 'INTERNAL_ERROR')
        self.assertEqual(errorcodes.error(-1)[0], 'INTERNAL_ERROR')

    def input_url_len(self):

        payload = '{ "images": ["http://synchronicityaustralia.com.au/wp-content/uploads/2016/12/sfw_apa_2013_28342_232388_briankushner_blue_jay_kk_high.jpeg", "https://badurl.com/image3.jpg", "https://upload.wikimedia.org/wikipedia/commons/3/32/House_sparrow04.jpg"]}'
        outputlist = InputProcessor(payload).process()
        self.assertEqual(len(outputlist), 3)

        urllist = ImageUrlCheck(self.inputdata).getUrl()
        self.assertEqual(len(urllist), 3)

        inputimagelist = ImageDownloader(urllist).location()
        self.assertEqual(len(inputimagelist), 3)


    def output_check(self):

        request = '{"images": []}'
        restpayload = InputProcessor(request).process()
        inputimagelist = ImageDownloader(restpayload).location()
        response = ImageObjectDetector(inputimagelist).detect()
        jresponse = json.loads(response)
        self.assertEqual(jresponse["status"],"EMPTY_IMAGE_FIELD")
        self.assertEqual(len(jresponse["results"]), 0)
 

        request = '{"threshold": 0.001}'
        restpayload = InputProcessor(request).process()
        inputimagelist = ImageDownloader(restpayload).location()
        response = ImageObjectDetector(inputimagelist).detect()
        jresponse = json.loads(response)
        self.assertEqual(jresponse["status"],"MISSING_IMAGES_FIELD")
        self.assertEqual(len(jresponse["results"]), 0)


        request = '{ "images": ["http://synchronicityaustralia.com.au/wp-content/uploads/2016/12/sfw_apa_2013_28342_232388_briankushner_blue_jay_kk_high.jpeg"]}'
        restpayload = InputProcessor(request).process()
        inputimagelist = ImageDownloader(restpayload).location()
        response = ImageObjectDetector(inputimagelist).detect()
        jresponse = json.loads(response)
        self.assertNotEqual(len(jresponse["results"]), 0)
        self.assertEqual(len(jresponse["results"]["classes"]), 0)
        
        # icorrect json request
        request = '{"images": ["http://example.com/image1.jpg"],}'
        restpayload = InputProcessor(request).process()
        inputimagelist = ImageDownloader(restpayload).location()
        response = ImageObjectDetector(inputimagelist).detect()
        jresponse = json.loads(response)
        self.assertEqual(jresponse["status"],"JSON_PARSE_ERROR")
        self.assertEqual(len(jresponse["results"]), 0)

