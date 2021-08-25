import os, glob
import PIL
import pandas as pd
import pickle
import psutil
import json
from entities import IR_Model
from ir_model_generation import *

CLICK_ACTION = 'click'
LONG_TAP_ACTION = 'long'
# usage_root_dir = os.path.abspath('/Users/yixue/Documents/Research/UsageTesting/UsageTesting-Repo/video_data_examples')
input_dir = 'steps_clean'
screen_widget_dir = 'ir_data_auto'
input_time = 0

def get_noswiping_next_screenIR(app_root_dir, step_list, i, usage_root_dir):
    action = get_action_from_step(step_list[i+1])
    if action == CLICK_ACTION or action == LONG_TAP_ACTION:
        return get_screenIR_from_step_LS(app_root_dir, step_list[i+1], usage_root_dir)
    else:
        while not (action == CLICK_ACTION or action == LONG_TAP_ACTION):
            i += 1
            action = get_action_from_step(step_list[i])
        return get_screenIR_from_step_LS(app_root_dir, step_list[i], usage_root_dir)

def build_linear_model(app_root_dir, step_dir, usage_root_dir):
    appname = os.path.basename(os.path.normpath(app_root_dir))
    linear_model = IR_Model(appname)
    step_list = sorted(glob.glob(step_dir + '/' + '*.jpg'))
    i = 0
    while i < len(step_list):
        if i == 0: # initial step
            current_action = get_action_from_step(step_list[i])
            # skip swipes in the beginning
            while not (current_action == CLICK_ACTION or current_action == LONG_TAP_ACTION):
                i += 1
                current_action = get_action_from_step(step_list[i])
            if current_action == CLICK_ACTION or current_action == LONG_TAP_ACTION: # only add initial state if the action is NOT swipe
                screenIR = get_screenIR_from_step_LS(app_root_dir, step_list[i], usage_root_dir)
                current_state = screenIR + '#' + str(i)
                linear_model.machine.add_transition('initial', 'start', current_state)
                linear_model.states.append(current_state)
        if i == len(step_list) - 1: # last step
            current_action = get_action_from_step(step_list[i])
            if current_action == CLICK_ACTION or current_action == LONG_TAP_ACTION:
                screenIR = get_screenIR_from_step_LS(app_root_dir, step_list[i], usage_root_dir)
                current_state = screenIR + '#' + str(i)
                final_transition = get_transition_name(app_root_dir, step_list[i], usage_root_dir)
                linear_model.machine.add_transition(final_transition, current_state, 'end')
                linear_model.states.append(current_state)
                linear_model.states.append('end')
            else: # final step is swipe
                last_state = linear_model.states[-1]
                linear_model.machine.add_transition(trigger=current_action, source=last_state, dest='end')
                linear_model.states.append('end')
        else:
            current_action = get_action_from_step(step_list[i])
            if current_action == CLICK_ACTION or current_action == LONG_TAP_ACTION:
                current_transition = get_transition_name(app_root_dir, step_list[i], usage_root_dir)
                current_screenIR = get_screenIR_from_step_LS(app_root_dir, step_list[i], usage_root_dir)
                next_action = get_action_from_step(step_list[i+1])
                if next_action == CLICK_ACTION or next_action == LONG_TAP_ACTION:
                    next_screenIR = get_screenIR_from_step_LS(app_root_dir, step_list[i+1], usage_root_dir)
                else:
                    next_screenIR = get_noswiping_next_screenIR(app_root_dir, step_list, i, usage_root_dir)
                current_state = current_screenIR + '#' + str(i)
                next_state = next_screenIR + '#' + str(i+1)
                linear_model.machine.add_transition(trigger=current_transition, source=current_state, dest=next_state)
                linear_model.states.append(current_state)
                linear_model.states.append(next_state)
            else: # handle swipe since it doesn't have a label and no widget is associated with it
                next_screenIR = get_noswiping_next_screenIR(app_root_dir, step_list, i, usage_root_dir)
                current_state = next_screenIR + '#' + str(i)
                next_state = next_screenIR + '#' + str(i+1)
                linear_model.machine.add_transition(trigger=current_action, source=current_state, dest=next_state)
                linear_model.states.append(current_state)
                linear_model.states.append(next_state)
        i += 1
    return linear_model

def run_linear_model_generation(usage_root_dir):
    for step_dir in glob.glob(usage_root_dir + '/*/' + input_dir):
        app_root_dir = step_dir.replace(input_dir, '') # /Users/yixue/Documents/Research/UsageTesting/UsageTesting-Repo/video_data_examples/6pm-video-signin-3/
        linear_model_path = os.path.join(app_root_dir, 'linear_model.pickle')
        if os.path.exists(linear_model_path):
            print('linear model already existed in', app_root_dir, 'skipping...')
            continue
        print('building linear model for', app_root_dir)
        linear_model = build_linear_model(app_root_dir, step_dir, usage_root_dir)
        linear_model.states = list(set(linear_model.states))
        with open(linear_model_path, 'wb') as file:
            pickle.dump(linear_model, file)
        linear_model.get_graph().draw(os.path.join(app_root_dir, linear_model.name + '-linear.png'), prog='dot')

    for proc in psutil.process_iter():
        # print(proc.name())
        if proc.name() == 'Preview':
            proc.kill()

if __name__ == '__main__':
    run_linear_model_generation('/Users/yixue/Documents/Research/UsageTesting/UsageTesting-Repo/video_data_examples')
    print('all done! :)')