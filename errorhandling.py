from enum import Enum
class ConstantValue(Enum):
    IMAGESFIELD = "images"
    THRESHOLD = "threshold"
    HTTP_PROTOCOL = "http"
    HTTPS_PROTOCOL = "https"
    MISSING_DOT_COM = ".com"
    MISSING_ORG = ".org"
    JPG_FORMAT = "jpg"
    JPEG_FORMAT = "jpeg"
    CAFFE_ROOT = "/home/centos/caffe" # Caffe installation location, Usually this should be taken from a configuration file
    IMAGE_DOWNLOADFOLDER = "imagerepo" # Usually this should be taken from a configuration file
    INPUT_VALIDATION_SUCCESS = 0
    MISSING_IMAGES_FIELD = 1
    INCORRECT_URL_FORMAT = 2
    LENGTHY_URL_FORMAT = 3
    MISSING_HTTP_PROTOCOL = 4
    MISSING_IMAGE_FORMAT = 5
    IMAGE_DOWNLOAD_ERROR = 6
    INTERNAL_ERROR = 7
    UNKNOWN_ERROR = 8
    JSON_PARSE_ERROR = 9
    EMPTY_IMAGE_FIELD = 10
    IMAGE_URL_VALID= 11
    INPUT_VALIDATION_FAILED = 12
    IMAGE_DOWNLOAD_SUCCESS = 13
    
class ImageProcessingErrorCodes:  
    def __init__(self):
        self.errorcode = { 0: ['INPUT_VALIDATION_SUCCESS', "Input is valid"],
                           1: ['MISSING_IMAGES_FIELD', "In request images field is missing"],
                           2: ['INCORRECT_URL_FORMAT', "Not a valid url format"],
                           3: ['LENGTHY_URL_FORMAT', "Url is too long more than 1024"],
                           4: ['MISSING_HTTP_PROTOCOL', "http:// is missing or incorrect"],
                           5: ['MISSING_IMAGE_FORMAT', "Image format is not jpg or jpeg"],
                           6: ['IMAGE_DOWNLOAD_ERROR', "Image download failed"],
                           7: ['INTERNAL_ERROR', "Internal error occurred"],
                           8: ['UNKNOWN_ERROR', 'Unknown Error'],
                           9: ['JSON_PARSE_ERROR', 'input json paring failed'],
                           10: ['EMPTY_IMAGE_FIELD', 'image field is empty'],
                           11: ['IMAGE_URL_VALID', 'image url is valid'],
                           12: ['INPUT_VALIDATION_FAILED', "Input is not perfect"],
                           13: ['IMAGE_DOWNLOAD_SUCCESS', "Image download succeeded"],
                         }
        
    def error(self):
        return self.errorcode
    def error(self, errnum):
        if errnum in self.errorcode:
            return self.errorcode[errnum]
        else:
            return self.errorcode[ConstantValue.INTERNAL_ERROR.value]

class ErrorReason:
    def __init__(self, errnum):
        self.errnum = errnum
        self.errorcodes = ImageProcessingErrorCodes()
        
    def reason(self):
        return self.errorcodes.error(self.errnum.value)
    
    def __repr__(self):
        ec = self.errorcodes.error(self.errnum.value)
        return json.dumps({ 'code' : ec[0], 'description': ec[1]})
    
    def __str__(self):
        ec = self.errorcodes.error(self.errnum.value)
        return json.dumps({ 'code' : ec[0], 'description': ec[1]})
    
    def isnerrror(self):
        return (self.errnum.value == ConstantValue.INPUT_VALIDATION_SUCCESS.value) or (self.errnum.value == ConstantValue.IMAGE_URL_VALID.value) or (self.errnum.value == ConstantValue.IMAGE_DOWNLOAD_SUCCESS.value)
