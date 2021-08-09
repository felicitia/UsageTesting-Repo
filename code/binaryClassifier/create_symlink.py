import os
import glob

''' 
this script creates symlinks in order to work with 
pytorch's ImageFolder file structure 
'''

usage_root_dir = os.path.abspath('/Users/yixue/Documents/Research/UsageTesting/v2s_data/Combined/9-About')
include_folder = 'clicked_frames_crop'

sym_root_dir = 'sym_' + os.path.basename(usage_root_dir)

if not os.path.exists(sym_root_dir):
    os.mkdir(sym_root_dir)

for src_dir in glob.glob(usage_root_dir + '/*/' + include_folder):
    dst_dir = os.path.join(sym_root_dir, src_dir.replace(usage_root_dir + "/", "").replace('/', '-'))
    os.symlink(src_dir, dst_dir)
    print('create symlink', src_dir, dst_dir)

print('all done! :)')