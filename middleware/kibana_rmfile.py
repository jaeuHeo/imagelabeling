import os
import json
import sys
import time
import uuid
import socket

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

import middleware
from imglabeling.librarys import delete_imgfile

# class RequestLogMiddleware(MiddlewareMixin):
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#     def process_request(self, request):
#         if request.method in ["POST", "PUT", "PATCH"]:
#             request.req_body = request.body
#         request.start_time = time.time()
#
#     def extract_log_info(self, request, response=None, exception=None):
#         log_data = {
#             "remote_address": request.META["REMOTE_ADDR"],
#             "server_hostname": socket.gethostname(),
#             "request_method": request.method,
#             "request_path": request.get_full_path(),
#             "run_time": time.time() - request.start_time,
#             'access_id': request.META['access_id']
#         }
#
#         if request.method in ["PUT", "POST", "PATCH"]:
#             log_data["request_body"] = json.loads(str(request.req_body, "utf-8"))
#
#             if response:
#                 if response["content-type"] == "application/json":
#                     response_body = response.data
#                     log_data["response_body"] = response_body
#
#         if request.user.is_authenticated:
#             log_data["operator_id"] = request.user.operator_id
#             log_data["operator_name"] = request.user.operator_name
#
#         return log_data

class FileRemoveMiddleware(MiddlewareMixin):

    "base/settings/base.py의 MIDDLEWARE_CLASSES 에 해당 키바나 경로를 추가해야합니다."

    def process_request(self, request):
        "request의 데이터로 받은 파일이름을 \
        middleware.KIBANA_DIC[request.META['access_id']]에 저장하는 코드를 \
        views단에서 작성해야합니다."

        # eshelp = EsSearchHelper(index=settings.SERVICE_NAME, type='exception')
        # print(eshelp)
        request.META['access_id'] = uuid.uuid1()
        self.access_id = request.META['access_id']
        middleware.KIBANA_DIC[self.access_id] = {}
        return

    def process_response(self, request, response):
        "code가 200이 아닌 다른 에러일 경우, 파일을 삭제하는 함수입니다.\
        delete_imgfile 메소드는 필요한 로직을 작성하여 커스텀하세요."

        file_name = middleware.KIBANA_DIC.get(self.access_id)
        if response.status_code != 200:
            try:
                delete_imgfile(file_name)
            except Exception as e:
                pass

        return response
