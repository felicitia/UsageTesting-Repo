import os
import glob

final_data_dir = os.path.abspath('/Users/yixue/Documents/Research/UsageTesting/v2s_data/Combined')

def count_files():
    for sub_dir in sorted(glob.glob(os.path.join(final_data_dir, '*'))):
        totalDir = 0
        for file in glob.glob(os.path.join(sub_dir, '*')):
            if os.path.isdir(file):
                totalDir += 1
        print(os.path.basename(os.path.normpath(sub_dir)) + '\t' + str(totalDir))


def get_subject_apps():
    total_apps = set()
    for sub_dir in sorted(glob.glob(os.path.join(final_data_dir, '*'))):
        apps = set()
        for file in glob.glob(os.path.join(sub_dir, '*')):
            if os.path.isdir(file):
                appName = os.path.basename(os.path.normpath(file)).split('-')[0].lower()
                apps.add(appName)
                total_apps.add(appName)
        print(os.path.basename(os.path.normpath(sub_dir)) + '\t' + str(len(apps)) + '\t' + str(apps))
    print('total apps:', str(len(total_apps)), str(total_apps))

if __name__ == '__main__':
    get_subject_apps()
    print('all done!')