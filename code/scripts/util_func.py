import os, glob
import shutil
import pandas as pd

def delete_subdire(dirname):
    dir_path = os.path.join(usage_root_dir, '*', dirname)
    dir_list = glob.glob(dir_path)
    for dir in dir_list:
        shutil.rmtree(dir)

def rename_file(dir):
    for src in glob.glob(dir + '/*'):
        dst = src + '_2'
        os.rename(src, dst)

def check_widget_exist(usage_root_dir):
    for screen in glob.glob(usage_root_dir + '/*/ir_data_auto/*-screen.jpg'):
        widget = screen.replace('screen', 'widget')
        if not os.path.isfile(widget):
            print('not exist', widget)

def merge_csvs():
    df = pd.concat(map(pd.read_csv, [
        '/Users/yixue/Documents/Research/UsageTesting/v2s_data/Combined/15-Filter/typing_result.csv',
        '/Users/yixue/Documents/Research/UsageTesting/v2s_data/Combined/15-Filter-Summer/typing_result.csv']),
                   ignore_index=True)
    df.to_csv('/Users/yixue/Documents/Research/UsageTesting/v2s_data/Combined/15-Filter/typing_result.csv')

def rename_files():
    for file in glob.glob('/Users/yixue/Documents/Research/UsageTesting/v2s_data/Combined/15-Filter-Summer/*/ir_data_auto/*.jpg'):
        filename = os.path.basename(file)
        prefix = filename.split('bbox')[0]
        new_filename = filename.replace(prefix, prefix + 's-')
        full_new_file = file.replace(filename, new_filename)
        # print('old file', file)
        # print('new file', full_new_file)
        os.rename(file, full_new_file)

def rename_screenIR():
    oldIR = 'sign_in_username'
    newIR = 'username'
    for file in glob.glob('/Users/yixue/Documents/Research/UsageTesting/v2s_data/Combined/*/LS-annotations.csv'):
        print('processing', file)
        df = pd.read_csv(file)
        df['tag_screen'] = df['tag_screen'].replace(oldIR, newIR)
        # print(df['tag_screen'])
        df.to_csv(file, index=False)

def rename_widgetIR():
    oldIR = 'show_checkbox'
    newIR = 'show'
    for file in glob.glob('/Users/yixue/Documents/Research/UsageTesting/v2s_data/Combined/*/LS-annotations.csv'):
        print('processing', file)
        df = pd.read_csv(file)
        df['tag_widget'] = df['tag_widget'].replace(oldIR, newIR)
        # print(df['tag_screen'])
        df.to_csv(file, index=False)

if __name__ == '__main__':
    # usage_root_dir = os.path.abspath('/Users/yixue/Documents/Research/UsageTesting/v2s_data/Combined/18-Textsize')
    # check_widget_exist(usage_root_dir)
    # rename_file(usage_root_dir)
    # delete_subdire('steps_clean_crop')
    # delete_subdire('clicked_frames')
    # delete_subdire('clicked_frames_crop')
    # delete_subdire('detected_frames')
    rename_widgetIR()
    print('all done! :)')