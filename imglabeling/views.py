# -*- coding: utf-8 -*-
import json
import time
import uuid
import pandas as pd

from psycopg2.extras import execute_values

from rest_framework.decorators import api_view

import middleware

from imglabeling.querys import *
from imglabeling.librarys import *
from imglabeling.utils import segment_api
from library.common import get_params, return_response, db_execute, Connection


@api_view(['POST'])
def segmentImage(request):
    # BOUNDARYVALUE = 10
    # boundary_value = BOUNDARYVALUE
    data = get_params(request)
    file_img = data['imageFile']
    type = data['type']

    file_name, draw_file_name, local_name = get_save_img(file_img)

    middleware.KIBANA_DIC[request.META['access_id']] = file_name
    origin_path, origin_img, origin_sh = load_img(file_name)

    t = time.time()
    segment_dic = segment_api(origin_img, type)

    print(f'segment time: {time.time()-t}')
    return_dic = {'return_data': segment_dic}

    return return_response(status_code=200, data=return_dic)