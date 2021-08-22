import os, glob
import shutil
import pandas as pd
import pickle
import sys
sys.path.insert(0, '/Users/yixue/Documents/Research/UsageTesting/UsageTesting-Repo/code/3_model_generation')

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
    oldIR = 'sign_in_or_sign_up'
    newIR = 'signin_or_signup'
    for file in glob.glob('/Users/yixue/Documents/Research/UsageTesting/v2s_data/UsageTesting-Artifacts/*/LS-annotations.csv'):
        print('processing', file)
        df = pd.read_csv(file)
        df['tag_screen'] = df['tag_screen'].replace(oldIR, newIR)
        # print(df['tag_screen'])
        df.to_csv(file, index=False)

def find_IRs():
    IR = 'keep_signin'
    column = 'tag_screen'
    for file in glob.glob('/Users/yixue/Documents/Research/UsageTesting/v2s_data/Combined/*/LS-annotations.csv'):
        df = pd.read_csv(file)
        rows = df.loc[df[column] == IR]
        if len(rows) != 0:
            print(file)

def rename_widgetIR():
    oldIR = 'get_started'
    newIR = 'continue'
    for file in glob.glob('/Users/yixue/Documents/Research/UsageTesting/v2s_data/UsageTesting-Artifacts/*/LS-annotations.csv'):
        print('processing', file)
        df = pd.read_csv(file)
        df['tag_widget'] = df['tag_widget'].replace(oldIR, newIR)
        # print(df['tag_screen'])
        df.to_csv(file, index=False)

def merge_label_files():
    big_file = '/Users/yixue/Documents/Research/UsageTesting/v2s_data/UsageTesting-Artifacts/1-SignIn/LS-annotations.csv'
    small_file = '/Users/yixue/Documents/Research/UsageTesting/UsageTesting-Repo/video_data_examples/LS-annotations.csv'
    big_df = pd.read_csv(big_file)
    small_df = pd.read_csv(small_file)
    merged_df = big_df.loc[~big_df['screen'].isin(small_df['screen'])]
    merged_df = pd.concat([merged_df, small_df])
    merged_df.to_csv(big_file, index=False)

def merge_filter_labels():
    big_file = '/Users/yixue/Documents/Research/UsageTesting/v2s_data/UsageTesting-Artifacts/15-Filter/LS-annotations.csv'
    small_file = '/Users/yixue/Documents/Research/UsageTesting/v2s_data/UsageTesting-Artifacts/15-Filter/filter-summer-annotations.csv'
    big_df = pd.read_csv(big_file)
    small_df = pd.read_csv(small_file)
    merged_df = big_df.loc[~big_df['screen'].str.contains('-s-bbox')]
    merged_df = pd.concat([merged_df, small_df])
    merged_df.to_csv(big_file, index=False)

def check_nan_state():
    # usatoday-about-2.png has nan state, check it!
    all_states = set()
    for ir_model_file in glob.glob('/Users/yixue/Documents/Research/UsageTesting/v2s_data/UsageTesting-Artifacts/*/*/ir_model.pickle'):
        if not os.path.exists(ir_model_file):
            print('ir model non exist in', ir_model_file)
        else:
            ir_model = pickle.load(open(ir_model_file, 'rb'))
            for state in ir_model.states:
                if pd.isna(state):
                    print('nan state in', ir_model_file)
                    # print()
    print(all_states)

if __name__ == '__main__':
    # usage_root_dir = os.path.abspath('/Users/yixue/Documents/Research/UsageTesting/v2s_data/Combined/18-Textsize')
    # for file in glob.glob('/Users/yixue/Documents/Research/UsageTesting/v2s_data/UsageTesting-Artifacts/18-Textsize/*/ir_model.pickle'):
    #     os.remove(file)
    check_nan_state()
    print('all done! :)')