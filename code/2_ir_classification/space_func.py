import numpy as np

def is_point_inside(x, y, row_min, row_max, column_min, column_max):
    if (column_min <= x <= column_max) and (row_min <= y <= row_max):
        return True
    return False

def get_bbox_points(compo):
    return compo['column_min'], compo['row_min'], compo['column_max'], compo['row_max']

def bbox_relation_nms(compo_a, compo_b, bias=(0, 0)):
    '''
    Calculate the relation between two rectangles by nms
   :return:
     -1 : a in b
     0  : a, b are not intersected
     1  : b in a
     2  : a, b are intersected
   '''
    col_min_a, row_min_a, col_max_a, row_max_a = get_bbox_points(compo_a)
    col_min_b, row_min_b, col_max_b, row_max_b = get_bbox_points(compo_b)

    bias_col, bias_row = bias
    # get the intersected area
    col_min_s = max(col_min_a - bias_col, col_min_b - bias_col)
    row_min_s = max(row_min_a - bias_row, row_min_b - bias_row)
    col_max_s = min(col_max_a + bias_col, col_max_b + bias_col)
    row_max_s = min(row_max_a + bias_row, row_max_b + bias_row)
    w = np.maximum(0, col_max_s - col_min_s)
    h = np.maximum(0, row_max_s - row_min_s)
    inter = w * h
    area_a = (col_max_a - col_min_a) * (row_max_a - row_min_a)
    area_b = (col_max_b - col_min_b) * (row_max_b - row_min_b)
    iou = inter / (area_a + area_b - inter)
    ioa = inter / (compo_a['width'] * compo_a['height'])
    iob = inter / (compo_b['width'] * compo_b['height'])

    if iou == 0 and ioa == 0 and iob == 0:
        return 0

    # contained by b
    if ioa >= 1:
        return -1
    # contains b
    if iob >= 1:
        return 1
    # not intersected with each other
    # intersected
    if iou >= 0.02 or iob > 0.2 or ioa > 0.2:
        return 2
    # if iou == 0:
    # print('ioa:%.5f; iob:%.5f; iou:%.5f' % (ioa, iob, iou))
    return 0