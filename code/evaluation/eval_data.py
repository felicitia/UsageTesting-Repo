import os
import glob
import pandas as pd

final_data_dir = os.path.abspath('/Users/yixue/Documents/Research/UsageTesting/v2s_data/UsageTesting-Artifacts')
screenIR_file = '/Users/yixue/Documents/Research/UsageTesting/UsageTesting-Repo/IR/screen_ir.csv'
widgetIR_file = '/Users/yixue/Documents/Research/UsageTesting/UsageTesting-Repo/IR/widget_ir.csv'

def count_files():
    for sub_dir in sorted(glob.glob(os.path.join(final_data_dir, '*'))):
        totalDir = 0
        for file in glob.glob(os.path.join(sub_dir, '*')):
            if os.path.isdir(file):
                totalDir += 1
        print(os.path.basename(os.path.normpath(sub_dir)) + '\t' + str(totalDir))

def count_labels():
    total_screen_label = 0
    total_widget_label = 0
    screenIRs = []
    widgetIRs = []
    for file in glob.glob(final_data_dir + '/*/LS-annotations.csv'):
        df = pd.read_csv(file)
        screenIRs += df['tag_screen'].unique().tolist()
        widgetIRs += df['tag_widget'].unique().tolist()
        total_screen_label += df.count(axis=0)['tag_screen']
        total_widget_label += df.count(axis=0)['tag_widget']
    print('screen total labels:', total_screen_label)
    print('widget total labels:', total_widget_label)
    print('total screen IRs', len(set(screenIRs)), set(screenIRs))
    print('total widget IRs', len(set(widgetIRs)), set(widgetIRs))

    screen_df = pd.read_csv(screenIR_file)
    widget_df = pd.read_csv(widgetIR_file)
    screenIR_def = screen_df['ir'].unique().tolist()
    widgetIR_def = widget_df['ir'].unique().tolist()
    print('screen diff:', set(screenIRs) - set(screenIR_def))
    print('screen diff other way:', set(screenIR_def) - set(screenIRs))
    print('widget diff:', set(widgetIRs) - set(widgetIR_def))
    print('widget diff other way:', set(widgetIR_def) - set(widgetIRs))

def count_subject_apps():
    total_apps = {}
    for sub_dir in sorted(glob.glob(os.path.join(final_data_dir, '*'))):
        apps = {}
        for file in glob.glob(os.path.join(sub_dir, '*')):
            if os.path.isdir(file):
                appName = os.path.basename(os.path.normpath(file)).split('-')[0].lower()
                if appName in apps.keys():
                    apps[appName] += 1
                else:
                    apps[appName] = 1
                if appName in total_apps.keys():
                    total_apps[appName] += 1
                else:
                    total_apps[appName] = 1
        print(os.path.basename(os.path.normpath(sub_dir)) + '\t' + str(apps))
        # print(os.path.basename(os.path.normpath(sub_dir)) + '\t' + str(len(apps)) + '\t' + str(apps))
    print('total apps:', total_apps)
    print('total app count', len(total_apps))
    count = 0
    for key in total_apps.keys():
        count += total_apps[key]
    print('total traces count', count)

if __name__ == '__main__':
    count_labels()
    print('all done!')