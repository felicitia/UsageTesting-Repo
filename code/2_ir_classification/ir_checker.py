import pandas as pd

def check_screen(ir_screen, labeled_file):
    df = pd.read_csv(labeled_file)
    rows = df.loc[df['tag_screen'] == ir_screen]
    if len(rows) == 0:
        print('screen non exist')
    else:
        print('screen exist')

def check_widget(ir_widget, labeled_file):
    df = pd.read_csv(labeled_file)
    rows = df.loc[df['tag_widget'] == ir_widget]
    if len(rows) == 0:
        print('widget non exist')
    else:
        print('widget exist')

if __name__ == '__main__':
    labeled_file = '/Users/yixue/Documents/Research/UsageTesting/UsageTesting-Repo/video_data_examples/LS-annotations.csv'
    check_widget('home', labeled_file)
    check_screen('home', labeled_file)