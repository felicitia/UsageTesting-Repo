import os, glob
import pandas as pd
from entities import IR_Model

### input parameters to change ###
usage_root_dir = os.path.abspath('/Users/yixue/Documents/Research/UsageTesting/UsageTesting-Repo/video_data_examples')
input_dir = 'steps_clean'
screen_widget_dir = 'ir_data_auto'
### end input parameters ###

def get_action_from_step(filename_abspath):
    if 'long' in os.path.basename(filename_abspath):
        return 'long'
    elif 'swipe' in os.path.basename(filename_abspath):
        filename_array = str(os.path.basename(filename_abspath)).split('-')
        return filename_array[3].replace('.jpg', '')
    else:
        return 'click'

def get_screenIR_from_step_LS(app_root_dir, step_image_file_abspath):
    annotation_file = os.path.join(usage_root_dir, 'LS-annotations.csv')
    appname = os.path.basename(os.path.normpath(app_root_dir))
    screen = appname + '-' + os.path.basename(step_image_file_abspath).replace('.jpg', '-screen.jpg')
    # print(screen)
    df = pd.read_csv(annotation_file)
    row_found = df.loc[df['screen'].str.contains(screen)]
    if len(row_found) == 1:
        # print(row_found['tag_screen'].values[0])
        return row_found['tag_screen'].values[0]
    else:
        print('row found is not 1, check', screen)


def get_widgetIR_from_step_LS(app_root_dir, step_image_file_abspath):
    annotation_file = os.path.join(usage_root_dir, 'LS-annotations.csv')
    appname = os.path.basename(os.path.normpath(app_root_dir))
    widget = appname + '-' + os.path.basename(step_image_file_abspath).replace('.jpg', '-widget.jpg')
    # print(widget)
    df = pd.read_csv(annotation_file)
    row_found = df.loc[df['widget'].str.contains(widget)]
    if len(row_found) == 1:
        # print(row_found['tag_widget'].values[0])
        return row_found['tag_widget'].values[0]
    else:
        print('row found is not 1, check', widget)

'''
if the action is click or long, return 'widgetIR#action'
else (it's swipe), return only the action, e.g., 'up'
'''
def get_transition_name(app_root_dir, step_image_file_abspath):
    action = get_action_from_step(step_image_file_abspath)
    if action == 'click' or action == 'long':
        widgetIR = get_widgetIR_from_step_LS(app_root_dir, step_image_file_abspath)
        return widgetIR + '#' + action
    else:
        return action

def handle_self_loop(ir_model, screenIR, transition_name):
    self_transitions = ir_model.machine.get_transitions('self', screenIR, screenIR)
    if len(self_transitions) == 0:
        new_self_transition = {'trigger': 'self', 'source': screenIR, 'dest': screenIR,
                               'conditions': [transition_name]}
        ir_model.machine.add_transitions(new_self_transition)
    elif len(self_transitions) == 1:
        condition_list = []
        existing_conditions = self_transitions[0].conditions
        for condition in existing_conditions:
            condition_list.append(condition.func) # get the string of the condition, not the condition obj
        if transition_name not in condition_list:
            condition_list.append(transition_name)
        ir_model.machine.remove_transition('self', screenIR, screenIR)
        ir_model.machine.add_transition(trigger='self', source=screenIR, dest=screenIR, conditions=condition_list)
    else:
        print('self transition > 1, check transition (self, ', screenIR, ')')
    return ir_model

def get_noswiping_previous_screenIR(app_root_dir, step_list, i):
    action = get_action_from_step(step_list[i-1])
    if action == 'click' or action == 'long':
        return get_screenIR_from_step_LS(app_root_dir, step_list[i-1])
    else:
        while not (action == 'click' or action == 'long'):
            i = i - 1
            action = get_action_from_step(step_list[i])
        return get_screenIR_from_step_LS(app_root_dir, step_list[i])

def add_transition_buffer(transition_buffer, ir_model, app_root_dir, step_list, i, screenIR):
    # print('transition buffer should have widget#action first, followed by swipes', transition_buffer)
    # add action to connect with previous screen
    trigger = transition_buffer[0]
    previous_screenIR = get_noswiping_previous_screenIR(app_root_dir, step_list, i)
    if previous_screenIR == screenIR:
        handle_self_loop(ir_model, screenIR, trigger)
    else:
        ir_model.machine.add_transition(trigger, previous_screenIR, screenIR)
    # add swipes to self transition's conditions
    transition_buffer.pop(0)
    self_transitions = ir_model.machine.get_transitions('self', screenIR, screenIR)
    if len(self_transitions) == 0:
        transition_buffer = list(set(transition_buffer)) # get unique values only
        new_self_transition = {'trigger': 'self', 'source': screenIR, 'dest': screenIR,
                               'conditions': transition_buffer}
        ir_model.machine.add_transitions(new_self_transition)
    elif len(self_transitions) == 1:
        condition_list = []
        existing_conditions = self_transitions[0].conditions
        for condition in existing_conditions:
            condition_list.append(condition.func)  # get the string of the condition, not the condition obj
        for transition_name in transition_buffer:
            if transition_name not in condition_list:
                condition_list.append(transition_name)
        ir_model.machine.remove_transition('self', screenIR, screenIR)
        ir_model.machine.add_transition(trigger='self', source=screenIR, dest=screenIR, conditions=condition_list)
    else:
        print('self transition > 1, check transition (self, ', screenIR, ')')
    return ir_model

def build_ir_model(app_root_dir, step_dir):
    appname = os.path.basename(os.path.normpath(app_root_dir))
    ir_model = IR_Model(appname)
    step_list = sorted(glob.glob(step_dir + '/' + '*.jpg'))
    transition_buffer = []
    for i in range(len(step_list)):
        current_action = get_action_from_step(step_list[i])
        if i == 0: # initial step
            if current_action == 'click' or current_action == 'long': # only add initial state if the action is NOT swipe
                screenIR = get_screenIR_from_step_LS(app_root_dir, step_list[i])
                ir_model.machine.add_transition('initial', 'start', screenIR)
                try:
                    screenIR_next = get_screenIR_from_step_LS(app_root_dir, step_list[i+1])
                    if screenIR == screenIR_next: # transit to the same screen, such as typing username
                        transition_name = get_transition_name(app_root_dir, step_list[i])
                        ir_model = handle_self_loop(ir_model, screenIR, transition_name)
                    else:
                        current_transition = get_transition_name(app_root_dir, step_list[i])
                        ir_model.machine.add_transition(current_transition, screenIR, screenIR_next)
                except IndexError:
                    # current step is the last step
                    final_transition = get_transition_name(app_root_dir, step_dir[i])
                    ir_model.machine.add_transition(final_transition, screenIR, 'end')
        elif i == len(glob.glob(step_dir + '/' + '*.jpg')) - 1: # last step
            if current_action == 'click' or current_action == 'long':
                screenIR = get_screenIR_from_step_LS(app_root_dir, step_list[i])
                final_transition = get_transition_name(app_root_dir, step_list[i])
                ir_model.machine.add_transition(final_transition, screenIR, 'end')
            else:
                final_screen = get_noswiping_previous_screenIR(app_root_dir, step_list[i])
                ir_model.machine.add_transition(transition_buffer[0], final_screen, 'end')
        else: # middle steps
            next_action = get_action_from_step(step_list[i+1])
            if current_action == 'click' or current_action == 'long':
                screenIR = get_screenIR_from_step_LS(app_root_dir, step_list[i])
                if len(transition_buffer) != 0: # add transition buffer to transit to the current screen
                    ir_model = add_transition_buffer(transition_buffer, ir_model, app_root_dir, step_list, i, screenIR)
                    transition_buffer.clear()
                if next_action == 'click' or next_action == 'long':
                    screenIR_next = get_screenIR_from_step_LS(app_root_dir, step_list[i+1])
                    if screenIR == screenIR_next:  # transit to the same screen, such as typing username
                        transition_name = get_transition_name(app_root_dir, step_list[i])
                        ir_model = handle_self_loop(ir_model, screenIR, transition_name)
                    else:
                        current_transition = get_transition_name(app_root_dir, step_list[i])
                        ir_model.machine.add_transition(current_transition, screenIR, screenIR_next)
                else: # current action is NOT swipe, next action is swipe
                    if len(transition_buffer) != 0:
                        print('transition buffer is not 0, check', step_list[i])
                    else:
                        transition_buffer.append(get_transition_name(app_root_dir, step_list[i]))
            else: # current action is swipe, then add the swiping direction to the transition buffer (will handle at next non-swipe screen)
                transition_buffer.append(get_transition_name(app_root_dir, step_list[i]))
    return ir_model

def main():
    for step_dir in glob.glob(usage_root_dir + '/*/' + input_dir):
        app_root_dir = step_dir.replace(input_dir, '') # /Users/yixue/Documents/Research/UsageTesting/UsageTesting-Repo/video_data_examples/6pm-video-signin-3/
        print('building ir model for', app_root_dir)
        ir_model = build_ir_model(app_root_dir, step_dir)
        ir_model.get_graph().draw(ir_model.name + '.png', prog='dot')


if __name__ == '__main__':
    main()
    print('all done! :)')