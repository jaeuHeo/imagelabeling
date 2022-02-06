import json
import sys

from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.db import connection
from library.common import Connection
from library.eshelper import EsSearchHelper
from library.exceptions import make_exception_logdata, make_logdata, log_exception

class LogAndExceptionController(MiddlewareMixin):

    def process_exception(self, request, exception):
        exc_info = sys.exc_info()
        # eshelp = EsSearchHelper(index=settings.SERVICE_NAME, type='exception')
        # data = make_exception_logdata(request, exception=exception, exc_info=exc_info)
        # status = eshelp.post(data=data)

        if 'db' in str(exception.__class__):

            message = "데이터베이스 조회에 예외상항이 발생했습니다. 고객센터를 통해 문의해 주세요"
        else:
            message = "서비스 호출시 비정상 작동이 감지되었습니다. 고객센터에 문의해주세요"

        # if status != 200:
        #     message += "\n kibana 적재가 실패하였습니다."
        exception_p = log_exception(request=request, exc_info=exc_info)
        print(exception_p)
        data = {"resultCode": 500, "resultMsg": message, "resultData": ''}
        data = json.dumps(data)
        return HttpResponse(data, content_type="application/json", status=500)

    def process_response(self, request, response):

        if request.method == 'OPTIONS':
            return response

        if 'alivecheck' in request.META['PATH_INFO']:
            return response

        # try:
        #     if response.status_code != 500:
        #         eshelp = EsSearchHelper(index=settings.SERVICE_NAME, type='status')
        #         data = make_logdata(request)
        #         eshelp.post(data=data)
        # except Exception as e:
        #     pass

        return response



