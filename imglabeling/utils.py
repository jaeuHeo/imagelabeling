import cv2
import json
import requests
import numpy as np
from json import JSONEncoder

from django.conf import settings


def post_request(end_point='segment', add_data={}):
    try:
        # myfile = {
        #     'image': img_path
        # }
        # response = requests.request("POST", verify=False, url=settings.MODEL_API_URL+end_point+'/', files=myfile, data=add_data)

        response = requests.request("POST", verify=False, url=settings.MODEL_API_URL + end_point, data=add_data)
        data = response.text
        return True, json.loads(data)['data']

    except Exception as e:
        print('detection_error', e)
        return False, e


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


def segment_api(origin_img, type):
    encodedNumpyData = json.dumps(origin_img, cls=NumpyArrayEncoder)
    # print(encodedNumpyData)
    segment_dic = post_request(end_point='segment', add_data={"image": encodedNumpyData, "type": type})
    return segment_dic[1]
