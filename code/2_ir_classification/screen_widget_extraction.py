"""
for each step in steps_clean folder,
extract the respective screen and widget without the touch indicator
"""

import os
import glob
import shutil
import json
import space_func
import numpy as np
import math

### input parameters you need to change ###
usage_root_dir = os.path.abspath('../../video_data_examples')
uied_result_root_dir = '/Users/yixue/Documents/Research/UsageTesting/Develop/UIED2.3-output-optimized/video_data_examples'
input_dir = 'steps_clean'
output_dir = 'ir_data_auto'
v2s_height = 1920 # screen max height in v2s
uied_height = 800 # image max height in UIED
### end of input parameters

def extract_screen(step_image_file, app_root_dir):
    filename = os.path.basename(step_image_file).replace('.jpg', '')
    if 'swipe' in filename:
        return # don't copy the screen associated with swipe action
        # swipe_direction = filename.split('-swipe-')[1]
        # filename = filename.replace('-swipe-' + swipe_direction, '')
        # print('filename', filename)
    elif 'long' in filename:
        filename = filename.replace('-long', '')
    frame_id_with_touch = str(filename).replace('bbox-', '')
    frame_id = int(frame_id_with_touch) - 1
    src_file = os.path.join(app_root_dir, 'detected_frames', 'bbox-' + '{0:0=4d}'.format(frame_id) + '.jpg')
    dst_file = os.path.join(app_root_dir, output_dir, os.path.basename(os.path.normpath(app_root_dir)) + '-' + filename + '-screen.jpg')
    # print(src_file, dst_file)
    shutil.copy(src_file, dst_file)

def extract_widget(step_image_file, app_root_dir, detected_actions_json):
    # if not 'bbox-0285' in os.path.basename(step_image_file):
    #     return
    # make sure to name the file with app_root_folder name in the beginning
    filename = os.path.basename(step_image_file).replace('.jpg', '')
    # print(filename)
    # print(app_root_dir)
    if 'swipe' in filename:
        return  # skip swipe steps since they don't need ir classification
    elif 'long' in filename:
        filename = filename.replace('-long', '')
    frame_id_with_touch = int(str(filename).replace('bbox-', ''))
    # print('frame id', frame_id_with_touch)
    x_v2s, y_v2s = get_coordinates(detected_actions_json, frame_id_with_touch)
    x_uied, y_uied = normalize_coordinates(x_v2s, y_v2s, v2s_height, uied_height)
    compo = find_cropped_widget(x_uied, y_uied, app_root_dir, filename)
    if compo is None:
        print('the cropped compo is None...')
    else:
        src_file = compo['clip_path']
        dst_file = os.path.join(app_root_dir, output_dir,
                                os.path.basename(os.path.normpath(app_root_dir)) + '-' + filename + '-widget.jpg')
        # print(src_file, dst_file)
        shutil.copy(src_file, dst_file)


def rm_outer_compo(compo_found):
    rm_marks = np.zeros(len(compo_found))
    for i, c1 in enumerate(compo_found):
        for j, c2 in enumerate(compo_found):
            if i == j:
                continue
            if space_func.bbox_relation_nms(c1, c2) == 1:  # if c2 is in c1, discard c1 since c2 is a finer compo
                rm_marks[i] = 1
                continue
    inner_compos = []
    for i in range(len(rm_marks)):
        if rm_marks[i] == 0:
            inner_compos.append(compo_found[i])
    return inner_compos

def find_cropped_widget(x, y, app_root_dir, filename):
    app_root_name = os.path.basename(os.path.normpath(app_root_dir))
    screen_UIEDresult_dir = os.path.join(uied_result_root_dir, app_root_name, app_root_name + '-' + filename + '-screen')
    compo_found = []
    with open(os.path.join(screen_UIEDresult_dir, 'compo.json'), 'r') as f:
        compo_json = json.load(f)
        for compo in compo_json['compos']:
            if compo['class'] == 'Background':
                continue
            if space_func.is_point_inside(x, y, compo['row_min'], compo['row_max'], compo['column_min'], compo['column_max']):
                # print(compo['class'], compo['clip_path'])
                compo_found.append(compo)
    # for compo in compo_found:
    #     print(compo['clip_path'])
    if len(compo_found) == 0:
        return None
    elif len(compo_found) == 1:
        return compo_found[0]
    else: # when there are multiple compos found
        compo_found = rm_outer_compo(compo_found)
        distance_min = 2000 # initialized to a max value
        closest_compo = None
        for compo in compo_found:
            mid_x = (compo['column_min'] + compo['column_max']) / 2
            mid_y = (compo['row_min'] + compo['row_max']) / 2
            distance = math.hypot(mid_x - x, mid_y - y)
            if distance < distance_min:
                distance_min = distance
                closest_compo = compo
        return closest_compo

def get_coordinates(detected_actions_json, frame_id):
    for item in detected_actions_json:
        for tap in item['taps']:
            if tap['frame'] == frame_id:
                return tap['x'], tap['y']
    print('no frame', frame_id, 'found...')

def normalize_coordinates(x_v2s, y_v2s, v2s_height, uied_height):
    ratio = uied_height / v2s_height
    x_uied = x_v2s * ratio
    y_uied = y_v2s * ratio
    return x_uied, y_uied


def main():
    for step_dir in glob.glob(usage_root_dir + '/*/' + input_dir):
        if not os.path.exists(step_dir.replace(input_dir, output_dir)):
            os.mkdir(step_dir.replace(input_dir, output_dir))
        app_root_dir = step_dir.replace(input_dir, '') # /Users/yixue/Documents/Research/UsageTesting/UsageTesting-Repo/video_data_examples/6pm-video-signin-3/
        print(app_root_dir)
        with open(os.path.join(app_root_dir, 'detected_actions.json'), 'r') as f:
            detected_actions_json = json.load(f)
            for step_image_file in os.scandir(step_dir):
                # print(step_image_file.path) # full abs path
                if step_image_file.path.endswith('.jpg'):
                    extract_screen(step_image_file, app_root_dir)
                    extract_widget(step_image_file, app_root_dir, detected_actions_json)

if __name__ == '__main__':
    main()
    print('all done! :)')