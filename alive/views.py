# -*- coding: utf-8 -*-

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection

@api_view(['GET'])
def alive_check(request):
    print(request.data.copy())
    return Response({'data':'호호ㅕ호ㅕ호ㅕ'})

