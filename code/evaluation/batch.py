import sys
sys.path.insert(0, '/Users/yixue/Documents/Research/UsageTesting/UsageTesting-Repo/code/3_model_generation')

import glob, os
from ir_model_generation import run_ir_model_generation

def ir_model_batch():
    final_data_root = '/Users/yixue/Documents/Research/UsageTesting/v2s_data/UsageTesting-Artifacts'
    for usage_dir in glob.glob(os.path.join(final_data_root, '*')):
        # print(usage_dir)
        run_ir_model_generation(usage_dir)


if __name__ == '__main__':
    # ir_model_batch()
    print('all done! :)')