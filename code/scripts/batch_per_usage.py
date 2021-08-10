import sys
sys.path.insert(0, '/Users/yixue/Documents/Research/UsageTesting/UsageTesting-Repo/code/1_step_extraction')
sys.path.insert(0, '/Users/yixue/Documents/Research/UsageTesting/UsageTesting-Repo/code/binaryClassifier')

from step_extraction import generate_clicked_frame
from step_cleaning import copy_useful_steps
from crop_clicked_frames import generate_clicked_frame_crop
from create_symlink import create_sym_keyboard_crops
from labelPredictor import generate_typing_results
from typingLocator import update_typing_results


root_usage_dir_list = ['/Users/yixue/Documents/Research/UsageTesting/v2s_data/Combined/12-AddCart']

if __name__ == '__main__':
    for root_usage_dir in root_usage_dir_list:
        generate_clicked_frame(root_usage_dir, 0)
        generate_clicked_frame_crop(root_usage_dir)
        create_sym_keyboard_crops(root_usage_dir)
        generate_typing_results(root_usage_dir)
        update_typing_results(root_usage_dir)
        copy_useful_steps(root_usage_dir)

    input('first automation all done! :) check steps clean folder now...')
