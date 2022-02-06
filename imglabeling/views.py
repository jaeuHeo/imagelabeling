# -*- coding: utf-8 -*-
import json
import uuid
import pandas as pd

from psycopg2.extras import execute_values

from rest_framework.decorators import api_view

import middleware
from imglabeling.querys import *
from imglabeling.librarys import *
from library.common import get_params, return_response, db_execute, Connection

@api_view(['GET'])
def get_alive_check(request):
    return Response(
        status=200,
        data = {
            "resultCode": 200,
            "resultMsg": "",
            "resultData": None
        }
    )

@api_view(['PUT'])
def saveImage(request):
    # from django.utils.deprecation import MiddlewareMixin
    # from middleware.kibana_log import LogAndExceptionController
    # aa = LogAndExceptionController(MiddlewareMixin)
    # a = aa.process_exception(request, 111)
    
    data = get_params(request)
    num_cls = data['cls']
    data_info = data['data']
    file_img = data['imageFile']
    is_fill = data['isFill']
    shape_cvs = data['shape']
    shape_cvs = [shape_cvs['height'],shape_cvs['width']]
    # shape_cvs = [750,750] #크기 하드코딩
    file_name, draw_file_name, local_name = get_save_img(file_img)

    middleware.KIBANA_DIC[request.META['access_id']] = file_name
    origin_path, origin_img, origin_sh = load_img(file_name)

    origin_img_cp = draw_img(origin_img,origin_sh,data_info,shape_cvs,is_fill)

    save_draw_image(origin_img_cp, draw_file_name)

    conn = Connection()
    cur = conn.cursor()
    insert_base = [(int(num_cls),str(local_name),str(origin_sh),str(shape_cvs),is_fill)]
    # insert_base = [('effesf', local_name, str(origin_sh), str(shape_cvs))]
    query = insert_tbl_image_query(table='base',cols="(num_cls,path_img,sh_img,sh_cvs,is_fill)")
    # query_params_dic = [{'query':query,'params':insert_base,'executemany':False},{'query':query,'params':insert_base,'executemany':False}]
    cur.execute(query, insert_base)
    # db_execute(query_params_dic,sequence = True)
    num_img = int(cur.fetchone()[0])

    insert_info = make_insert_info(num_img,data_info)

    query = insert_tbl_image_query(table='info',cols="(num_img,num_area,cr_area,txt_area,type_area,color_area,is_show,b_box)")
    cur.executemany(query, insert_info)
    # execute_values(cur, query, insert_info, template=None, page_size=100)
    conn.commit()

    if conn:
        conn.close()

    return return_response(status_code=200, data={'numImg': num_img})

@api_view(['POST'])
def lookUp(request):
    
    data = get_params(request)
    num_cls = data['cls']

    query = select_tbl_image_join_query()
    rows_join = db_execute(query, params={'num_cls': num_cls})

    join_list = []
    for row in rows_join:
        join_list.append([int(row['num_img']), row['path_img'], json.loads(row['sh_img']), row['txt_area'], row['color_area']])

    row_df = pd.DataFrame(join_list, columns=['index', 'path_img', 'sh_img', 'txt_area', 'color_area'])

    row_df = row_df.groupby(['index'], as_index=False).agg({'path_img': 'first', 'sh_img': 'first', 'txt_area': lambda x: x.tolist(), 'color_area': lambda x: x.tolist()}).sort_index(ascending=False)

    res_list = []
    for idx, (num_img,path_img, sh_img, txt_areas, color_area) in enumerate(row_df.values.tolist()):
        pair_dic = [{'txt_area': txt, 'txt_color': clr} for txt, clr in zip(txt_areas,color_area)]
        split_imgpath = path_img.split('=')
        split_imgpath.insert(1, '=DRAWIMG_')
        draw_img_path = ''.join(split_imgpath)

        res_list.append({'numImg': num_img, 'pathImg': draw_img_path,'shImg':sh_img, 'pairArea': pair_dic})
    
    return return_response(status_code=200, data=res_list)


@api_view(['PUT'])
def deleteImage(request):
    data = get_params(request)

    num_img = data['numImg']

    conn = Connection()

    cur = conn.cursor()
    query = select_tbl_image_query(table='base', cols='*', where_col="num_img")

    cur.execute(query, {'num_img': num_img})
    rows_base = name_to_json(cur)
    path_img = rows_base[0]['path_img'].split('=')[-1]

    query1 = del_tbl_image_query(table='base', where_col="num_img")
    cur.execute(query1, {'num_img': num_img})

    query2 = del_tbl_image_query(table='info', where_col="num_img")
    cur.execute(query2, {"num_img": num_img})

    file_name = settings.FILES_PATH + path_img
    draw_file_name = settings.FILES_PATH + 'DRAWIMG' + path_img

    conn.commit()

    delete_imgfile(file_name)

    if conn:
        conn.close()

    return return_response(status_code=200, data={'numImg': num_img})


@api_view(['POST'])
def segmentBoundary(request):

    data = get_params(request)

    boundary_value = data['boundaryValue']

    pixel = data['pixel']

    image = data['imageFile']

    type = data['type']

    file_name, draw_file_name, local_name = get_save_img(image)

    origin_img_path, origin_img, origin_sh = load_img(file_name)

    return_data, c_segmentation_img, _ = select2draw(origin_img, pixel, boundary_value)

    if os.path.isfile(origin_img_path):
        os.remove(origin_img_path)

    if type == 1: #배경삭제
        return_dict = {'return_data': return_data}
        return return_response(status_code=200, data=return_dict)

    elif type == 2: #배경삭제안함
        return_dict = {'return_data': c_segmentation_img}
        return return_response(status_code=200, data=return_dict)


@api_view(['POST'])
def segmentImage(request):
    # BOUNDARYVALUE = 10
    # boundary_value = BOUNDARYVALUE
    data = get_params(request)

    return_dict = {'return_data': []}

    return return_response(status_code=200, data=return_dict)