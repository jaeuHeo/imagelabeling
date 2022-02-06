import requests
import json

from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

from library.common import request_common_session_api


class SessionCheck(MiddlewareMixin):

    def session_check(
            self,
            authorization: str,
            cno: str,
            r_emp: str,
            r_user_id: str
    ) -> bool:
        """
        위하고 session 정보와 cookie 정보를 비교하여 쿠키의 변조여부를 체크합니다.
        :param authorization: cookie에서 추출한 authorization
        :param cno: cookie에서 추출한 cno
        :param r_emp: cookie에서 추출한 emp_no
        :param r_user_id: cookie에서 추출한 user_id
        :return:
        """

        session_info = request_common_session_api(authorization, cno)
        if session_info['resultCode']!=200:
            return False

        emp_no = str(session_info['resultData']['employee_no.'])
        user_id = str(session_info['resultData']['portal_id'])

        if emp_no == r_emp and user_id == r_user_id:
            return True
        else:
            return False

    def process_request(self, request: HttpRequest):
        """
        header에 포함된 session을 기반으로 요청된 cookie의 변조여부를 체크합니다.
        :param request: HttpRequest
        :return: code: 1(세션만료), 2(쿠기값 손상)
        """

        if 'alivecheck' in request.META['PATH_INFO']:
            return None

        if request.META['PATH_INFO'] in settings.NO_COOKIE_URL:
            return None


        cookie_dict = request.COOKIES if isinstance(request.COOKIES, dict) else {}

        authorization = cookie_dict.get('AUTH_A_TOKEN')
        cno = cookie_dict.get('cell_company_no')
        user_id = cookie_dict.get('h_portal_id')
        emp_no = cookie_dict.get('h_selected_employee_no')

        result_code = 0
        if authorization is None or cno is None or user_id is None or emp_no is None:
            result_code = 1
        else:
            cno = str(cno)
            emp_no = str(emp_no)
            cookie_check = self.session_check(authorization, cno, emp_no, user_id)
            if cookie_check is False:
                result_code = 2

        if result_code == 0:
            return None
        else:
            data = json.dumps({
                "resultCode": 401,
                "resultMsg": "서비스이용권한이 없습니다.",
                "resultData": {"code":result_code}
            })
            return HttpResponse(data, content_type = "application/json")
