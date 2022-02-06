import numpy as np

def _find_minax_color(img, pixels,boundary_value):
    y = np.array(pixels)[:, 0]
    x = np.array(pixels)[:, 1]
    max_color = img[y, x].max(axis=-2)
    max_color = [255 if i + boundary_value > 255 else i for i in max_color]

    min_color = img[y, x].min(axis=-2)
    min_color = [0 if i - boundary_value <= 0 else i for i in min_color]
    return [max_color, min_color]

def _make_cr_list(c_segmentation_img):
    cr_tuple = np.where(c_segmentation_img == int(2))

    cr_list = [{'x':x,'y':y} for y,x in zip(cr_tuple[0],cr_tuple[1])]
    return cr_list

