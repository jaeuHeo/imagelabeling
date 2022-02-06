import sys

from django.conf import settings


def make_logdata(request):
    """
    kibana에 적재할 log 데이터를 생성합니다.
    :param request:
    :return:
    """
    cookie_dict = request.COOKIES if isinstance(request.COOKIES, dict) else {}

    data = {}
    data['authorization'] = cookie_dict.get('AUTH_A_TOKEN','')
    data['cno'] = cookie_dict.get('cell_company_no','')
    data['user_id'] = cookie_dict.get('h_portal_id','')
    data['emp_no'] = cookie_dict.get('h_selected_employee_no','')
    data["service"] = settings.SERVICE_NAME
    if request.method.upper() == "GET":
        data["request-param"] = str(request.GET)
    else:
        data["request-param"] = str(request.POST)
    return data


def make_exception_logdata(request, exception, exc_info):
    """
    kibana에 적재할 exception log 데이터를 생성합니다.
    :param request:
    :param exception:
    :param exc_info:
    :return:
    """
    data = make_logdata(request)
    data["exception-type"] = str(exc_info[0])
    data["exception"] = log_exception(request=request, exc_info=exc_info)

    return data


def log_exception(request, exc_info):
    """
    exception 정보를 가져옵니다.
    :param request:
    :param exc_info:
    :return:
    """
    try:
        request_repr = repr(request)
    except:
        request_repr = "Request repr() unavailable"

    message = "%s\n\n%s" % (_get_traceback(exc_info), request_repr)
    return message


def _get_traceback(exc_info=None):
    """Helper function to return the traceback as a string"""
    import traceback
    return '\n'.join(traceback.format_exception(*(exc_info or sys.exc_info())))

