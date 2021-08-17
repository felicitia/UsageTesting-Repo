import os, glob
import shutil

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

if __name__ == '__main__':
    usage_root_dir = os.path.abspath('/Users/yixue/Documents/Research/UsageTesting/v2s_data/Combined/18-Textsize')
    check_widget_exist(usage_root_dir)
    # rename_file(usage_root_dir)
    # delete_subdire('steps_clean_crop')
    delete_subdire('clicked_frames')
    delete_subdire('clicked_frames_crop')
    delete_subdire('detected_frames')
    print('all done! :)')