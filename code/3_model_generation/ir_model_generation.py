from transitions import Machine
import os, glob
import pandas as pd

usage_root_dir = os.path.abspath('/Users/yixue/Documents/Research/UsageTesting/UsageTesting-Repo/video_data_examples')
input_dir = 'steps_clean'
screen_widget_dir = 'ir_data_auto'

def get_action_from_step(filename):
    if 'long' in os.path.basename(filename):
        return 'long'
    elif 'swipe' in os.path.basename(filename):
        filename_array = str(filename).split('-')
        return filename_array[3].replace('.jpg', '')
    else:
        return 'click'

def get_screenIR_from_step_LS(app_root_dir, step_image_file):
    annotation_file = os.path.join(usage_root_dir, 'LS-annotations.csv')
    appname = os.path.basename(os.path.normpath(app_root_dir))
    screen = appname + '-' + os.path.basename(step_image_file).replace('.jpg', '-screen.jpg')
    # print(screen)
    df = pd.read_csv(annotation_file)
    row_found = df.loc[df['screen'].str.contains(screen)]
    if len(row_found) == 1:
        # print(row_found['tag_screen'].values[0])
        return row_found['tag_screen'].values[0]
    else:
        input('row found is not 1, check', screen)



def get_widgetIR_from_step_LS(app_root_dir, step_image_file):
    annotation_file = os.path.join(usage_root_dir, 'LS-annotations.csv')
    appname = os.path.basename(os.path.normpath(app_root_dir))
    widget = appname + '-' + os.path.basename(step_image_file).replace('.jpg', '-widget.jpg')
    # print(widget)
    df = pd.read_csv(annotation_file)
    row_found = df.loc[df['widget'].str.contains(widget)]
    if len(row_found) == 1:
        # print(row_found['tag_widget'].values[0])
        return row_found['tag_widget'].values[0]
    else:
        input('row found is not 1, check', widget)

def build_ir_model(app_root_dir, step_dir):
    for step_image_file in os.scandir(step_dir):
        if step_image_file.path.endswith('.jpg'):
            action = get_action_from_step(os.path.basename(step_image_file))
            if action == 'click' or action == 'long':
                screenIR = get_screenIR_from_step_LS(app_root_dir, step_image_file)
                widgetIR = get_widgetIR_from_step_LS(app_root_dir, step_image_file)

def main():
    for step_dir in glob.glob(usage_root_dir + '/*/' + input_dir):
        app_root_dir = step_dir.replace(input_dir, '') # /Users/yixue/Documents/Research/UsageTesting/UsageTesting-Repo/video_data_examples/6pm-video-signin-3/
        print(app_root_dir)
        build_ir_model(app_root_dir, step_dir)

if __name__ == '__main__':
    main()
    print('all done! :)')