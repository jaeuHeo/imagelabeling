# -*- coding: utf-8 -*-
import sys; sys.setrecursionlimit(1000000)

import re
import os
import cv2
import uuid
import datetime
import platform
import numpy as np

import psycopg2
import matplotlib.pyplot as plt

from PIL import Image, ImageFont, ImageDraw
from typing import Tuple

from rest_framework.response import Response
from django.conf import settings

from imglabeling.utils import _make_cr_list, _find_minax_color

def img_show(img, size =(15,15)):
    plt.rcParams["figure.figsize"] = size
    imgplot = plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.show()


def name_to_json(cursor):
    """
    cursor.fetchall() 함수로 받아온 쿼리 결과를 json 형식으로 만들어 반환해주는 함수입니다.
    :param cursor: SQL 연결 변수
    :return: JSON 쿼리 결과 LIST
    """
    row = [dict((cursor.description[i][0], value)
                for i, value in enumerate(row)) for row in cursor.fetchall()]
    return row


def convert_to_text(text):
    text = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', text).replace(" ", "")
    text = ''.join(text.split())
    return text


def get_save_img(img_file):
    # n = 20  # 문자의 개수(문자열의 크기)
    # rand_str = ""  # 문자열
    # for i in range(n):
    #     rand_str += str(random.choice(string.ascii_lowercase))
    #
    # extension = str(path_img).split('.')[-1]
    # img_time = convert_to_text(''.join(str(datetime.datetime.now()).split(' ')))
    key = str(uuid.uuid4())
    file_name = key + '.' + str(img_file).split('.')[-1]
    print(file_name)
    draw_file_name = 'DRAWIMG' + '_' + file_name

    with open(settings.FILES_PATH + file_name, 'wb') as w:

        for chunk in img_file.chunks():
            w.write(chunk)

    local_name = settings.MEDIA_URL + '?img=' + file_name

    return file_name, draw_file_name, local_name

def load_img(file_name):

    origin_img_path = os.path.join(settings.FILES_PATH, file_name)
    # origin_img = imgproc.loadImage(origin_path)
    origin_img = cv2.imread(origin_img_path)
    # origin_img = img_resize(origin_img, dsize=(737, 553))
    origin_sh = [origin_img.shape[0], origin_img.shape[1]]
    return origin_img_path, origin_img, origin_sh

def draw_img(origin_img,origin_img_sh,data_info,shape_img, is_fill):

    def _color_data(data_color):
        color_string = data_color.split(',')

        color = [int(re.sub(r'[^0-9]', '', string)) for string in color_string]

        color = (color[2], color[1], color[0])

        # opacity = float(re.sub('[)]', '', color_string[3]))
        opacity = 0.4

        return color, opacity
 
    def _draw_cr_types(data, resize_xy, origin_img_cp, isclosed, color, opacity, is_fill):
        if data['isShow']:
            cr_area = []
            for idx, pt in enumerate(data['coordinate']):

                if data['type'] == 'line':
                    isclosed = False
                    if idx == 0:
                        cor = [0, 0, pt['endX'] * resize_xy[1], pt['endY'] * resize_xy[0]]
                        cr_area.append(cor[2:4])

                    else:
                        cor = [pt['startX'] * resize_xy[1], pt['startY'] * resize_xy[0], pt['endX'] * resize_xy[1], pt['endY'] * resize_xy[0]]
                        cr_area.append(cor[2:4])

                        line_crs = np.array(cor).reshape(-1, 2).astype(np.int32)
                        origin_img_cp = cv2.polylines(origin_img_cp, [line_crs], isclosed, color, int(max(resize_xy)), cv2.LINE_AA)

                else:
                    cor = [pt['x'] * resize_xy[1], pt['y'] * resize_xy[0]]
                    cr_area.append(cor)

            cr_inner_area = []
            if data['type'] == 'colorpick':
                for inner_dic in data['innerCoords']:
                    inner_list = [[xy['x'] * resize_xy[1], xy['y'] * resize_xy[0]] for xy in inner_dic['coordinate']]
                    array_inner_list = np.array(inner_list).reshape(-1, 2).astype(np.int32)
                    cr_inner_area.append(array_inner_list)
                    origin_img_cp = cv2.polylines(origin_img_cp, [array_inner_list], isclosed, color, int(max(resize_xy)), cv2.LINE_AA)

            if data['type'] != 'line':
                pts = np.array(cr_area).reshape(-1, 2).astype(np.int32)
                origin_img_cp = cv2.polylines(origin_img_cp, [pts], isclosed, color, int(max(resize_xy)), cv2.LINE_AA)

                if is_fill:
                    zero_img = np.zeros_like(origin_img_cp, np.uint8)
                    if data['type'] == 'colorpick':
                        if len(cr_inner_area) > 0:
                            cr_inner_area.insert(0,pts)
                            zero_img = cv2.fillPoly(zero_img, cr_inner_area, color)
                        else:
                            zero_img = cv2.fillPoly(zero_img, [pts], color)
                    else:
                        zero_img = cv2.fillPoly(zero_img, [pts], color)

                    # else:
                    #     y = np.array(pts)[:, 1]
                    #     x = np.array(pts)[:, 0]
                    #     zero_img[:,:,0][y,x] = color[0]
                    #     zero_img[:,:,1][y,x] = color[1]
                    #     zero_img[:,:,2][y,x] = color[2]
                    #
                    #     contours, hierarchy = cv2.findContours(zero_img[:, :, 0], cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                    #     for cnt in contours:
                    #         cv2.drawContours(origin_img_cp, [cnt], 0, color, 1)

                    mask = zero_img.astype(bool)
                    origin_img_cp[mask] = cv2.addWeighted(origin_img_cp, opacity, zero_img, opacity, 0)[mask]

            if data['type'] == "line" or data['type'] == "polygon":
                for area in cr_area:
                    array_area = np.array(area).reshape(-1, 2).astype(np.int32)
                    origin_img_cp = cv2.circle(origin_img_cp, array_area[0], 3*int(max(resize_xy)), (251, 144, 28), -1)

        return origin_img_cp

    def _draw_text(data, origin_img_cp, color, resize_xy):
        # thickness = 2
        # font = cv2.FONT_HERSHEY_SIMPLEX
        # edge = (data['bbox']['x3'], data['bbox']['y3']) if data['bbox']['y1'] < 2 else (data['bbox']['x1'], data['bbox']['y1'])
        # fontScale = 1
        # # Using cv2.putText() method
        # origin_img_cp = cv2.putText(origin_img_cp, data['value'], edge, font, fontScale, color, thickness, cv2.LINE_AA)

        text_h = 20
        per_text_h = int(text_h * max(resize_xy))

        if platform.system() == 'Darwin':  # 맥
            font = 'AppleGothic.ttf'
        elif platform.system() == 'Linux':  # 리눅스 (구글 콜랩)
            '''
            !wget "https://www.wfonts.com/download/data/2016/06/13/malgun-gothic/malgun.ttf"
            !mv malgun.ttf /fonts
            import matplotlib.font_manager as fm 
            fm._rebuild() 
            '''
            # font = '/fonts/malgun.ttf'
            font = '/fonts/DOUZONEText50.ttf'

        else:  # 윈도우
            # font = '/fonts/malgun.ttf'
            font = '/fonts/DOUZONEText50.ttf'
        try:
            imageFont = ImageFont.truetype(font, per_text_h)

        except:
            imageFont = ImageFont.load_default()

        # font = ImageFont.truetype("fonts/gulim.ttc", text_h)
        try:
            img_cp = Image.fromarray(origin_img_cp)
            draw = ImageDraw.Draw(img_cp)
            text = data['value']
            re_x1, re_y1 = data['bbox']['x1'] * resize_xy[1], data['bbox']['y1'] * resize_xy[0]
            re_x3, re_y3 = data['bbox']['x3'] * resize_xy[1], data['bbox']['y3'] * resize_xy[0]
            if re_y1 < per_text_h:
                edge = (re_x1, re_y3)
            # elif re_y1 < per_text_h and (re_x3 + per_text_h) > (origin_img_cp.shape[1] - per_text_h):
            #     edge = (re_x1, re_y3)
            else:
                edge = (re_x1, re_y1 - (per_text_h+5))

            draw.text(edge, text, font=imageFont, fill=color)
            origin_img_cp = np.array(img_cp)
        except Exception as e:
            pass

        return origin_img_cp

    origin_img_cp = origin_img.copy()
    resize_xy = [(origin_img_sh[0]/shape_img[0]), (origin_img_sh[1]/shape_img[1])]

    for data in data_info:

        isclosed = True

        if data['index'] > 0:
            color, opacity = _color_data(data['color'])
            origin_img_cp = _draw_cr_types(data, resize_xy, origin_img_cp, isclosed, color, opacity, is_fill)

            origin_img_cp = _draw_text(data, origin_img_cp, color, resize_xy)

    return origin_img_cp

def save_draw_image(origin_img_cp,draw_file_name):
    local_img = Image.fromarray(cv2.cvtColor(origin_img_cp, cv2.COLOR_BGR2RGB))
    local_img.save(settings.FILES_PATH + format(draw_file_name))

def make_insert_info(num_img,data_info):
    info_list = []

    for idx,info in enumerate(data_info):

        # data_dic ={}
        cr_dic = {}

        num_area = info.get('index', None)
        cr_area = info.get('coordinate', None)
        txt_area = info.get('value', None)
        type_area = info.get('type', '')
        color_area = info.get('color', '')
        # is_fill = info.get('isFill', False)
        is_show = info.get('isShow', False)
        bbox = info.get('bbox', '{}')

        # if idx == 0:
            # cr_dic = str(cr_dic)
            # info_list.append((num_img, num_area, cr_dic, txt_area, type_area, color_area, is_fill, is_show))
            # info_list.append((num_img, num_area, cr_dic, txt_area, type_area, color_area, is_show))
        # else:
        if idx != 0:
            if type_area != 'line':
                for ids, cr in enumerate(cr_area,1):

                    if ids == 1:
                        cr_dic["p" + str(ids)] = [cr['x'],cr['y']]

            else:
                for ids, cr in enumerate(cr_area,1):

                    if ids == 1:
                        cr_dic["p" + str(ids)] = [cr['endX'],cr['endY']]
                    else:
                        cr_dic["p" + str(ids)] = [cr['startX'], cr['startY'], cr['endX'], cr['endY']]

        # cr_dic = json.dumps(cr_dic)
        # info_list.append((num_img,num_area, cr_dic, txt_area, type_area, color_area, is_fill, is_show))
        info_list.append((num_img, num_area, str(cr_dic), txt_area, type_area, color_area, is_show, str(bbox)))

    return info_list

def responseCode(resultCode=9999,resultData='새로고침해줘',resultMsg=''):

    resultCode = int(resultCode)

    # if resultCode == 200:
    # resultData = resultData
    # else:
    #     resultData = {'flag':resultData}

    result = {
              'resultCode':resultCode,
              'resultData': resultData,
              'resultMsg':str(resultMsg)
    }
    return Response(data=result)

def delete_imgfile(file_name):
    if len(file_name) > 0:
        if os.path.isfile(settings.FILES_PATH + file_name):
            os.remove(settings.FILES_PATH + file_name)
        if os.path.isfile(settings.FILES_PATH + 'DRAWIMG_' + file_name):
            os.remove(settings.FILES_PATH + 'DRAWIMG_' + file_name)
    else:
        pass
def img2segmentation(img: np.array,
                     max_color: list,
                     min_color: list,
                     boundary_value: int,
                     rgb= True
                     ) -> np.array:
    """
    이미지에서 선택한 색과 유사한 색이 있는 픽셀 정보를 리턴합니다.
    이미지와 동일한 shape 크기의 2차원 numpy 값을 리턴합니다.

    parameters
    ----------
    img : numpy.array
        0~255값을 가진 이미지 입니다.
    target_color : list
        기준이되는 컬러값입니다.
    boundary_value : int
        얼마나 유사한 색을 추출할 것인지에 대한 임계값입니다.

    returns
    -------
    seg_image : numpy.array
        0과 1로 표시된 2차원 array입니다. 1일 경우 유사색으로 판단된 픽셀입니다.
    """
    # mix, max 임계값 정하기
    # min_color = [i - boundary_value for i in target_color]
    # max_color = [i + boundary_value for i in target_color]

    min_color = [i - boundary_value for i in min_color]
    max_color = [i + boundary_value for i in max_color]

    # 임계값 안에 들어가는 이미지 픽셀 추출
    if rgb:
        seg_image_c1 = (img[:, :, 0] > min_color[0]) & (img[:, :, 0] < max_color[0])
        seg_image_c2 = (img[:, :, 1] > min_color[1]) & (img[:, :, 1] < max_color[1])
        seg_image_c3 = (img[:, :, 2] > min_color[2]) & (img[:, :, 2] < max_color[2])
        seg_image = seg_image_c1 & seg_image_c2 & seg_image_c3
    else:
        seg_image = (img > min_color[0]) & (img < max_color[0])

    seg_image = seg_image.astype(int)
    return seg_image


# x,y 값을 받아 갈 수 있는지 없는지 체크하는 메소드 정의
def _checker(img: np.array, x: int, y: int) -> bool:

    if x < 0 or y < 0:
        return False

    try:

        if img[y][x] == 0:
            return False

        elif img[y][x] == 2:
            return False

        else:
            img[y][x] = 2
            return True

    except Exception as e:
        return False


# 동서남북 갈 수 있는 곳을 찾아서 queue에 집어넣는 메소드 정의
def insert_queue(img: np.array, queue: list, x: int, y: int):

    if _checker(img, x + 1, y):
        queue.append([x + 1, y])
        # print('x + 1, y',queue)
    if _checker(img, x - 1, y):
        queue.append([x - 1, y])
        # print('x - 1, y',queue)
    if _checker(img, x, y + 1):
        queue.append([x, y + 1])
        # print('x, y + 1',queue)
    if _checker(img, x, y - 1):
        queue.append([x, y - 1])
        # print('x, y - 1',queue)

def pixel_selection(img, x, y):

    queue = []

    queue.append([x, y])
    _checker(img, x, y)
    while True:
        if len(queue) == 0:
            break

        p = queue.pop()
        x, y = p[0], p[1]
        insert_queue(img, queue, x, y)
    img = img.astype('uint8')

    return img

def flood_fill(img,x,y,max_color,min_color):
    rows, cols = img.shape[:2]
    # 마스크 생성, 원래 이미지 보다 2픽셀 크게 ---①
    mask = np.zeros((rows + 2, cols + 2), np.uint8)
    # 채우기에 사용할 색 ---②
    newVal = (255, 255, 255)
    # 최소 최대 차이 값 ---③

    loDiff = (img[y,x] - min_color).tolist()
    upDiff = (max_color - img[y, x]).tolist()
    # loDiff, upDiff = (10, 10, 10), (10, 10, 10)
    seed = (x, y)
    # 색 채우기 적용 ---④

    retval = cv2.floodFill(img, mask, seed, newVal, loDiff, upDiff)
    # print(retval)
    img_show(img)
    cr_tuple = np.where(img==2)

    return_data = (img==2).astype(int)
    cr_list = [{'x': x, 'y': y} for y, x in zip(cr_tuple[0], cr_tuple[1])]
    # 채우기 변경 결과 표시 ---⑤
    # return_val = retval[1][retval[1] == -999]
    return return_data,cr_list,retval


def img_resize(img, dsize=(300,200)):
    dst = cv2.resize(img, dsize=dsize, interpolation=cv2.INTER_AREA)
    return dst

def select2draw(img : np.array, pixel: list, boundary_value : int):

    RESIZE_V = 200

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # get segmentation img
    # img_cp = img.copy()
    img_shape = img.shape
    rgb = True if len(img_shape) == 3 else False

    # image resize
    # resize_p = RESIZE_V / np.max(img_shape)

    resize_p = 1
    pixel_array = np.array([[round(i['y']) * resize_p, round(i['x']) * resize_p] for i in pixel])
    y_0, x_0 = tuple(pixel_array[0])
    
    dsize = (int(img_shape[1] * resize_p), int(img_shape[0] * resize_p))
    r_x, r_y = int(x_0 * resize_p), int(y_0 * resize_p)

    r_img = img_resize(img, dsize = dsize)
    max_color, min_color = _find_minax_color(r_img, pixel_array, boundary_value)
    segmentation_img = img2segmentation(r_img, max_color, min_color, boundary_value, rgb=rgb)
    # return_data, cr_list, retval = flood_fill(r_img.copy(), r_x, r_y, max_color, min_color)
    # 경계픽셀 포인트와 선택 픽셀과 인접한 값만 추출해서 가져옵니다.
    # boundary_points = []
    c_segmentation_img = pixel_selection(segmentation_img, r_x, r_y)
    c_segmentation_img = img_resize(c_segmentation_img, dsize=(img_shape[1], img_shape[0]))
    return_data = (c_segmentation_img == 2).astype(int)

    # c_segmentation_img = img_resize(retval[1], dsize=(img_shape[1], img_shape[0]))
    # return_data = (c_segmentation_img == 2).astype(int)
    cr_list = _make_cr_list(c_segmentation_img)
    return return_data, c_segmentation_img, cr_list


def cal_pixel(pixel):

    pixel_list = []
    cr_s, cr_e = pixel
    if cr_e['x'] != cr_s['x']:
        a = (cr_e['y'] - cr_s['y']) / (cr_e['x'] - cr_s['x'])
        b = cr_e['y'] - (a * cr_e['x'])
        large_x, small_x = max(cr_e['x'],cr_s['x']), min(cr_e['x'],cr_s['x'])
        for x in range(int(small_x), int(large_x) + 1):
            y = int((a * x) + b)
            pixel_list.append({'x': x, 'y': y})

    else:
        x = cr_e['x'] == cr_s['x']
        large_y, small_y = max(cr_e['y'], cr_s['y']), min(cr_e['y'], cr_s['y'])
        for y in range(int(small_y), int(large_y) + 1):
            pixel_list.append({'x': x, 'y': y})

    return pixel_list