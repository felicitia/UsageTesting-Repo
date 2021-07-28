''' This function outputs whether the touch indicator falls onto the keyboard or not '''

import os
import pandas as pd
import json

### input parameters you need to change ###
typing_result_file = os.path.abspath('sym_SignIn/typing_result.csv') # output file to append 'touch_location' results
usage_root_dir = os.path.abspath('/Users/yixue/Documents/Research/UsageTesting/v2s_data/Combined/SignIn')
KEYBOARD_Y = 1110 # threashold for the keyboard region. Y coordinate where keyboard starts when Y >= KEYBOARD_Y
frame_index = 0 # Index of the frame list. keep it consistent with the value in the step_extraction.py
### end input parameters ###

df_typing_result = pd.read_csv(typing_result_file)

# add results to new column 'touch_location': the results are either 'onKeyboard' or 'out'
def find_touch_location(row):
    split_word = '-clicked_frames_crop/bbox-'
    app_dir = str(row['filename']).split(split_word)[0]
    frame_id = int(str(row['filename']).split(split_word)[1].replace('.jpg', ''))
    # print(app_dir, frame_id)
    Y_cor = get_touch_Y(app_dir, frame_id)
    if Y_cor is None:
        print('frame NOT FOUND! check: ', row['filename'])
    elif Y_cor >= KEYBOARD_Y:
        return 'onKeyboard'
    return 'out'

def get_touch_Y(app_dir, frame_id):
    action_file = open(os.path.join(usage_root_dir, app_dir, 'detected_actions.json'), 'r')
    action_array = json.load(action_file)
    for action in action_array:
        # print(frame_id, action['taps'][frame_index]['frame'])
        if frame_id == action['taps'][frame_index]['frame']:
            return action['taps'][frame_index]['y']
    return None

def main():
    df_typing_result['touch_location'] = df_typing_result.apply(lambda row: find_touch_location(row), axis = 1) # apply find_touch_location function to each row
    df_typing_result.to_csv(typing_result_file)
if __name__ == '__main__':
    main()
