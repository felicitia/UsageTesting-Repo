import glob, os
import psutil
from PIL import Image
import PIL
import pandas as pd


usage_root_dir = 'C:/Users/leony/Documents/UsageTesting/usage_data/usage_data'
final_label_file = 'C:/Users/leony/Documents/UsageTesting/usage_data/final_labels_all.csv'
df = pd.read_csv(final_label_file)

CLICK_ACTION = 'click'
LONG_TAP_ACTION = 'long'

def get_action_from_step(filename_abspath):
    if LONG_TAP_ACTION in os.path.basename(filename_abspath):
        return LONG_TAP_ACTION
    elif 'swipe' in os.path.basename(filename_abspath):
        filename_array = str(os.path.basename(filename_abspath)).split('-')
        # print(filename_array)
        return filename_array[3].replace('.jpg', '')
    else:
        return CLICK_ACTION

def label_screenIR_and_widgetIr(screen_name, widget_name, app_root_dir):
    new_row = {}

    ### find screen ###
    row_found = df.loc[df['screen'].str.contains(screen_name)]
    if len(row_found) == 0:
        image = Image.open(os.path.join(app_root_dir, 'ir_data_auto', screen_name))
        image.show()
        user_input = input('please enter screen IR manually for ' + screen_name + '\n')
        new_row['screen'] = screen_name
        new_row['tag_screen'] = user_input
        image.close()
    elif len(row_found) == 1:
        if pd.isna(row_found['tag_screen'].values[0]):
            image = Image.open(os.path.join(app_root_dir, 'ir_data_auto', screen_name))
            image.show()
            user_input = input('please enter screen IR manually for ' + screen_name + '\n')
            new_row['screen'] = screen_name
            new_row['tag_screen'] = user_input
            image.close()
    else:
        raise ValueError('row found is > 1 when getting screenIR, check', screen_name)

    ### find widget ###
    row_found = df.loc[df['widget'].str.contains(widget_name)]
    if len(row_found) == 0:
        image = Image.open(os.path.join(app_root_dir, 'ir_data_auto', widget_name))
        image.show()
        user_input = input('please enter widget IR manually for ' + widget_name + '\n')
        new_row['widget'] = widget_name
        new_row['tag_widget'] = user_input
        image.close()
    elif len(row_found) == 1:
        if pd.isna(row_found['tag_widget'].values[0]):
	    # add back below if looking for missing single widgets
            """
            image = Image.open(os.path.join(app_root_dir, 'ir_data_auto', widget_name))
            image.show()
            user_input = input('please enter widget IR manually for ' + widget_name + '\n')
            new_row['widget'] = widget_name
            new_row['tag_widget'] = user_input
            image.close()
            """
            print(widget_name, "is blank")
    else:
        raise ValueError('row found is > 1 when getting widget, check', widget_name)

    with open(final_label_file, 'a') as csv:
        if new_row != {}:
            # if new_row.get('screen') is not None and new_row.get('widget') is not None:
            temp = "\n" + new_row['screen'] + ", " + new_row['widget'] + ", , " + new_row['tag_screen'] + ", " + new_row['tag_widget'] + ",,"
            print(temp)
            csv.write(temp)
            
	    # special case row addition, didn't really work
	    """
            elif new_row.get('screen') is None:
                temp = "\n, " + new_row['widget'] + ", , , " + new_row['tag_widget'] + ",,"
                print(temp)
                csv.write(temp)
            elif new_row.get('widget') is None:
                temp = "\n" + new_row['screen'] + ", , " + new_row['tag_screen'] + ", , ,,"
                print(temp)
                csv.write(temp)
            """
            


if __name__ == '__main__':
    for step_dir in glob.glob(usage_root_dir + '/*/*/steps_clean'):
        app_root_dir = step_dir.replace('steps_clean', '')
        appname = os.path.basename(os.path.normpath(app_root_dir))
        for step_path in glob.glob(step_dir + '/*.jpg'):
            step_name = os.path.basename(os.path.normpath(step_path))
            if 'swipe' in step_name:
                continue
            bbox_name = step_name.split('-')[0] + '-' + step_name.split('-')[1]
            bbox_name = bbox_name.replace('.jpg', '')
            screen_name = appname + '-' + bbox_name + '-screen.jpg'
            widget_name = appname + '-' + bbox_name + '-widget.jpg'
            
            label_screenIR_and_widgetIr(screen_name, widget_name, app_root_dir)

    for proc in psutil.process_iter():
        # print(proc.name())
        if proc.name() == 'Photos':
            proc.kill()