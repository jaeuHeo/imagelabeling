import json
import requests
import datetime
import psycopg2
from typing import Union, Optional
from pytz import timezone, utc
from psycopg2.extras import execute_values

from django.db import connection
from django.http import HttpResponse
from django.conf import settings
from rest_framework.response import Response

def Connection():
    default = settings.DATABASES['default']
    conn = psycopg2.connect(
            dbname=default['NAME'],
            user=default['USER'],
            host=default['HOST'],
            password=default['PASSWORD'],
            port=default['PORT']
            # options=f'-c search_path={schema}',
        )

    return conn

class Message:
    """
    return_response 함수의 공통 메시지
    """
    message_200 = 'Success.'
    message_201 = 'Data is inserted.'
    message_203 = 'Non Authoritative Information'
    message_204 = 'Data does not exist.'
    message_400 = 'Parameter is not valid.'
    message_401 = 'Your token is not valid or does not exist.'
    message_404 = 'Data does not exist.'
    message_500 = 'Internal server error.'
    message_9999 = 'service updating'


def get_params(request)->dict:

    if request.method == 'GET':
        data = request.query_params.dict()
        # return data

    else:
        data = request.data.dict()
        # return data

    data_dic = {}
    for k,v in data.items():

        val = data.get(k, None)
        try:
            data_dic[k] = json.loads(val)

        except:
            data_dic[k] = val
    return data_dic


def return_response(
        status_code: int,
        data:Union[dict, list, str]=None,
        message:str=None,
        return_json:bool=False,
        response_type:str = 'rest_framework'
)-> Union[Response, HttpResponse]:
    """
    API Response 형식을 만들어주는 함수
        - Format: {"status": status, "message": message, "data": data}
    :param status_code: http response status
    :param data: response data
    :param message: response message
    :param return_json: return json 변환 여부
    :param response_type: response type 지정 (rest_framework, http)
    :return:
    """
    status_code_string = str(status_code)

    if not message:
        if hasattr(Message, "message_"+status_code_string):
            message = getattr(Message, "message_"+status_code_string)

    response = {"resultCode": status_code, "resultMsg": message, "resultData": data}

    if return_json:
        response = json.dumps(response)
    if response_type == 'rest_framework':
        return Response(response)
    else:
        return HttpResponse(response, content_type="application/json")


def name_to_json(cursor):
    """
    cursor.fetchall() 함수로 받아온 쿼리 결과를 json 형식으로 만들어 반환해주는 함수입니다.
    :param cursor: SQL 연결 변수
    :return: JSON 쿼리 결과 LIST
    """
    row = [dict((cursor.description[i][0], value)
                for i, value in enumerate(row)) for row in cursor.fetchall()]
    return row

def db_execute(
        query:str,
        params:Union[dict, tuple, list],
        execute_type:str ='select',
        executemany:bool = False
)-> Optional[list]:
    """
    django.db connection 및 execute 해주는 함수입니다.
    :param query: 실행시킬 sql query 입니다.
    :param params: sql에 전달될 param 입니다.
    :param execute_type: 실행시킬 sql 명령어 타입으로 (select, delect, update, insert) 4가지를 지원합니다.
    :param executemany: 한개의 query문에 여러개의 param 데이터를 실행시킬지 여부입니다.
    :return:
    """
    conn = Connection()
    cur = conn.cursor()
    if executemany:
        # execute_values(cur, query, params, template=None, page_size=100)
        cur.executemany(query, params)
    else:
        cur.execute(query, params)

    data = name_to_json(cur)
    conn.commit()
    return data

def db_execute2(
        execute_info: list,
        sequence: bool = False
)-> Optional[list]:
    """
    django.db connection 및 execute 해주는 함수입니다.
    :param query: 실행시킬 sql query 입니다.
    :param params: sql에 전달될 param 입니다.
    :param execute_type: 실행시킬 sql 명령어 타입으로 (select, delect, update, insert) 4가지를 지원합니다.
    :param executemany: 한개의 query문에 여러개의 param 데이터를 실행시킬지 여부입니다.
    :return:
    """
    conn = connection
    cur = conn.cursor()
    num_sequence = 0
    if sequence:
        num_sequence = int(cur.fetchone()[0])
    for data in execute_info:
        query, params, executemany = data['query'], data['params'], data['executemany']
        if executemany:
            # execute_values(cur, query, params, template=None, page_size=100)
            cur.executemany(query, params)
        else:
            cur.execute(query, params)

        if sequence:
            num_sequence = int(cur.fetchone()[0])

    data = name_to_json(cur)
    conn.commit()

    return data

def request_common_session_api(
        authorization:str,
        cno:str) -> dict:
    """
    inner gw를 통해 session에 등록되어 있는 user 정보를 가져옵니다.
    :param authorization: authorization
    :param cno: cno
    :return:
    """
    headers = {'Authorization': authorization}
    params = {'cno': cno}
    request_url = settings.INNER_URL + '/common/session'
    res = requests.get(request_url, params=params, headers=headers)

    session_info = json.loads(res.text)
    return session_info


def get_date()-> str:
    """
    현재 시간을 리턴합니다.
    :return:
    """
    KST = timezone('Asia/Seoul')
    now = datetime.datetime.utcnow()
    kst_now = utc.localize(now).astimezone(KST)

    return str(kst_now).split('.')[0]




