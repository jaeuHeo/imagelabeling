import time

import requests
import json
from urllib.parse import urlencode
from rest_framework import status
from django.conf import settings


class EsSearchHelper:
    def __init__(self, index, type):
        self.__index = index
        self.__type = type
        self.__method = ""
        self.__requestmethod = "GET"
        self.__querystring = {"index": index,
                              "type": type,
                              "key": 'key_log'}
        self.__url = settings.ES_LOGURL

    def post(self, **kwargs):
        self.__method = "post/"
        self.__requestmethod = "POST"
        if 'data' in kwargs:
            kwargs['data'] = json.dumps(kwargs['data'])
        self.__querystring.update(kwargs)
        ret = self.send()
        if ret != None:
            return status.HTTP_200_OK
        else:
            return status.HTTP_400_BAD_REQUEST

    def send(self):
        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'cache-control': 'no-cache'
        }

        url1 = self.__url + self.__method
        if self.__requestmethod == "GET":
            response = requests.request("GET", url1, headers={}, params=self.__querystring)
        else:
            response = requests.request("POST", url1, headers=headers, data=urlencode(self.__querystring))
        if response.status_code == 200:
            dic = json.loads(response.text)
            return dic
        else:
            return None
