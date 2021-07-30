import os, glob
import shutil

def delete_subdire(dirname):
    dir_path = os.path.join(usage_root_dir, '*', dirname)
    dir_list = glob.glob(dir_path)
    for dir in dir_list:
        shutil.rmtree(dir)

if __name__ == '__main__':
    usage_root_dir = os.path.abspath('/Users/yixue/Documents/Research/UsageTesting/v2s_data/Combined/SignIn')
    delete_subdire('clicked_frames')
    delete_subdire('clicked_frames_crop')
    delete_subdire('detected_frames')
    print('all done! :)')