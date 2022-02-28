import os, sys
import pandas as pd
import json
import glob
import pickle

current_dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(current_dir_path, '..'))
sys.path.insert(0, os.path.join(current_dir_path, '..', '3_model_generation'))
sys.path.insert(0, os.path.join(current_dir_path, '..', '4_dynamic_generation'))


from global_config import *
from App_Config import *


def containsNumber(value):
    for character in value:
        if character.isdigit():
            return True
    return False


def find_all_triggers(ir_model):
    all_triggers = set()
    for state in ir_model.states:
        current_triggers = ir_model.machine.get_triggers(state)
        for trigger in current_triggers:
            if trigger == 'self':
                self_transitions = ir_model.machine.get_transitions(trigger='self', source=state, dest=state)
                for condition in ir_model.get_condition_list(self_transitions):
                    if '#' in condition:
                        all_triggers.add(condition.split('#')[0])
            elif '#' in trigger:
                all_triggers.add(trigger.split('#')[0])
    return all_triggers

def eval_AUT_per_usage(appname, usage_name): # appname: etsy, usage_name: 1-SignIn
    excluding_states = {'start', 'end', 'signin_amazon', 'signin_fb', 'signin_google', 'signin_google_popup'}
    excluding_triggers = {'initial', 'to_start', 'by_amazon', 'by_facebook', 'by_google', 'pick_google_account'}

    eval_json_file = open(os.path.join(FINAL_ARTIFACT_ROOT_DIR, 'output', 'models', usage_name, 'dynamic_output', appname, 'eval_results.json'), 'r')
    eval_json = json.load(eval_json_file)

    states_generated = set()
    triggers_generated = set()

    for key in eval_json:
        if containsNumber(key):
            states_generated.add(eval_json[key]['true_screen_IR'])
            triggers_generated.add(eval_json[key]['true_widget_IR'])

    states_generated = states_generated - excluding_states
    triggers_generated = triggers_generated - excluding_triggers


    states_human = set()
    triggers_human = set()
    human_test_count = 0

    for ir_model_path in glob.glob(os.path.join(FINAL_ARTIFACT_ROOT_DIR, 'usage_data', usage_name, appname+'*', 'ir_model.pickle')):
        human_test_count += 1
        ir_model = pickle.load(open(ir_model_path, 'rb'))
        states_human = states_human.union(set(ir_model.states))
        triggers_human = triggers_human.union(find_all_triggers(ir_model))

    states_human = states_human - excluding_states
    triggers_human = triggers_human - excluding_triggers

    overlapping_states = states_human.intersection(states_generated)
    overlapping_triggers = triggers_human.intersection(triggers_generated)

    result_entry = [{'AUT': appname,
                    'usage': usage_name,
                    'human_states': states_human,
                    'human_triggers': triggers_human,
                    'human_test_count': human_test_count,
                    'generated_states': states_generated,
                    'generated_triggers': triggers_generated,
                    'state_coverage': len(overlapping_states)/len(states_generated),
                    'transition_coverage': len(overlapping_triggers)/len(triggers_generated)}]

    df = pd.DataFrame.from_dict(result_entry)
    df.to_csv('all_eval_results.csv', index=False, header=True)

if __name__ == '__main__':
    appname = 'wish'
    usage_name = usage_folder_map['signin']
    eval_AUT_per_usage(appname, usage_name)
    print('all done! :)')