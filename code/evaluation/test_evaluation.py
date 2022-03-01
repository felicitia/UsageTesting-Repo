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


def find_linear_states_and_triggers(linear_model):
    states = []
    triggers = []

    linear_model.states.remove('start')
    linear_model.states.remove('end')
    linear_model.states.sort(key=lambda x: x.split('#')[1])

    for sorted_state in linear_model.states:
        # print(sorted_state)
        states.append(sorted_state.split('#')[0])
        trigger_list = linear_model.machine.get_triggers(sorted_state)
        if len(trigger_list) == 1:
            triggers.append(trigger_list[0].split('#')[0])
        else:
            print(trigger_list, 'is not only 1')
            raise ValueError

    return states, triggers


def clean_test(test):
    excluding_states = ['start', 'end', 'signin_amazon', 'signin_fb', 'signin_google', 'signin_google_popup']
    excluding_triggers = ['initial', 'to_start', 'by_amazon', 'by_facebook', 'by_google', 'pick_google_account']

    for state in test['states']:
        if state in excluding_states:
            test['states'].remove(state)

    for transition in test['transitions']:
        if transition in excluding_triggers:
            test['transitions'].remove(transition)

    return test



def eval_AUT_per_usage(appname, usage_name): # appname: etsy, usage_name: 1-SignIn

    eval_json_file = open(os.path.join(FINAL_ARTIFACT_ROOT_DIR, 'output', 'models', usage_name, 'dynamic_output', appname, 'eval_results.json'), 'r')
    eval_json = json.load(eval_json_file)

    test1 = {}
    test2 = {}
    test1['states'] = []
    test1['transitions'] = []
    test2['states'] = []
    test2['transitions'] = []

    for key in eval_json:
        print('key in order:', key)
        if '0-' in key:
            test1['states'].append(eval_json[key]['true_screen_IR'])
            test1['transitions'].append(eval_json[key]['true_widget_IR'])
        elif '1-' in key:
            test2['states'].append(eval_json[key]['true_screen_IR'])
            test2['transitions'].append(eval_json[key]['true_widget_IR'])


    generated_test_list = [clean_test(test1), clean_test(test2)]

    human_test_list = []
    for linear_model_path in glob.glob(os.path.join(FINAL_ARTIFACT_ROOT_DIR, 'usage_data', usage_name, appname+'*', 'linear_model.pickle')):
        linear_model = pickle.load(open(linear_model_path, 'rb'))
        human_test = {}
        human_test['states'], human_test['transitions'] = find_linear_states_and_triggers(linear_model)
        human_test_list.append(clean_test(human_test))

    all_pair_results_df = eval_test_pairs(appname, usage_name, human_test_list, generated_test_list)
    return all_pair_results_df


def calculate_coverage(human_test, generated_test):
    overlapping_states = set(human_test['states']).intersection(set(generated_test['states']))
    overlapping_trans = set(human_test['transitions']).intersection(set(generated_test['transitions']))

    state_coverage = len(set(overlapping_states)) / len(set(human_test['states']))
    trans_coverage = len(set(overlapping_trans)) / len(set(human_test['transitions']))

    state_recall = len(set(overlapping_states)) / len(set(generated_test['states']))
    trans_recall = len(set(overlapping_trans)) / len(set(generated_test['transitions']))

    return state_coverage, trans_coverage, state_recall, trans_recall


def eval_test_pairs(appname, usage_name, human_test_list, generated_test_list):

    result_df = pd.read_csv(EVAL_RESULT_PATH, header=0)

    AUT_list = []
    usage_list = []
    test_id_list = []
    human_video_id_list = []
    human_states_list = []
    generated_states_list = []
    human_transitions_list = []
    generated_transitions_list = []
    state_coverage_list = []
    transition_coverage_list = []
    state_recall_list = []
    transition_recall_list = []

    for test_id in range(len(generated_test_list)):
        for human_video_id in range(len(human_test_list)):
            generated_test = generated_test_list[test_id]
            human_test = human_test_list[human_video_id]

            AUT_list.append(appname)
            usage_list.append(usage_name)
            test_id_list.append(test_id)
            human_video_id_list.append(human_video_id)
            human_states_list.append(human_test['states'])
            generated_states_list.append(generated_test['states'])
            human_transitions_list.append(human_test['transitions'])
            generated_transitions_list.append(generated_test['transitions'])

            state_coverage, trans_coverage, state_recall, trans_recall = calculate_coverage(human_test, generated_test)
            state_coverage_list.append(state_coverage)
            transition_coverage_list.append(trans_coverage)
            state_recall_list.append(state_recall)
            transition_recall_list.append(trans_recall)

    result_rows = {'AUT': AUT_list, 'usage': usage_list, 'test_id': test_id_list, 'human_video_id': human_video_id_list,
                   'human_states': human_states_list, 'generated_states': generated_states_list,
                   'human_transitions': human_transitions_list, 'generated_transitions': generated_transitions_list,
                   'state_coverage': state_coverage_list, 'transition_coverage': transition_coverage_list,
                   'state_recall': state_recall_list, 'transition_recall': transition_recall_list}

    df = pd.DataFrame(result_rows)

    result_df = pd.concat([result_df, df], axis=0, ignore_index=True)
    return result_df

def eval_usage_batch(usage_name): # 1-SignIn
    result_df_list = []
    for appname_path in glob.glob(os.path.join(FINAL_ARTIFACT_ROOT_DIR, 'output', 'models', usage_name, 'dynamic_output', '*')):
        if os.path.isdir(appname_path):
            appname = os.path.basename(os.path.normpath(appname_path))
            print('calculating results for', appname)
            all_pair_results_df = eval_AUT_per_usage(appname, usage_name)
            result_df_list.append(all_pair_results_df)

    all_results = pd.concat(result_df_list, axis=0, ignore_index=True)

    usage_result_path = os.path.join(current_dir_path, 'raw_results', usage_name+'.csv')

    all_results.to_csv(usage_result_path, index=False, header=True)

if __name__ == '__main__':

    usage_name = usage_folder_map['signin']
    eval_usage_batch(usage_name)

    print('all done! :)')