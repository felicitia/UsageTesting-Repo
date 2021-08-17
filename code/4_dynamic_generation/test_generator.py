import sys
sys.path.insert(0, '/Users/yixue/Documents/Research/UsageTesting/UsageTesting-Repo/code/3_model_generation')

from sys import argv
import os
import re
import explorer
import time
import json
import selenium
import test_generator
import os.path
import pickle
from entities import IR_Model
import glob
import random


class TestCase:
    def __init__(self, test_folder_path):
        self.test_folder_path = test_folder_path
        self.events = []

    def add_event(self, action, state, image_path, text, text_input):
        event = Event(action, state, image_path, text, text_input)
        self.events.append(event)

    def print_test_case(self):
        for event in self.events:
            if event.action == "oracle-text_input":
                print("--------------------")
                print("state: " + event.state)
                print("action: " + event.action)
                print("oracle text input: " + event.text_input)
            else:
                print("--------------------")
                print("state: " + event.state)
                print("action: " + event.action)
                print("image_path: " + event.image_path)
                print(event.text)


class Event:
    def __init__(self, action, state, image_path, text, text_input):
        self.action = action
        self.state = state
        self.image_path = image_path
        self.text = text
        self.text_input = text_input


class DestEvent:
    def __init__(self, action, exec_id_type, exec_id_val, text_input, isEnd):
        self.action = action
        self.exec_id_type = exec_id_type
        self.exec_id_val = exec_id_val
        self.text_input = text_input
        self.isEnd = isEnd

    def print_event(self):
        print("---- printing dest event ----")
        print("action:")
        print(self.action)
        print("exec_id_type")
        print(self.exec_id_type)
        print("exec_id_val")
        print(self.exec_id_val)
        print("text_input")
        print(self.text_input)


class TestGenerator:
    def __init__(self):
        self.explorer = explorer.Explorer()
        self.test_num = 0
        self.MAX_TEST_NUM = 5

    def start(self, output_dir, usage_model_path, appname):
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        self.appname = appname
        self.output_dir = os.path.join(output_dir, appname)
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)
        self.generated_tests_dir = os.path.join(self.output_dir, 'generated_tests')
        self.MAX_ACTION = 20
        if not os.path.isdir(self.generated_tests_dir):
            os.makedirs(self.generated_tests_dir)
        self.load_usage_model(usage_model_path)
        self.generate_test()

    def load_usage_model(self, usage_model_path):
        pickle_filepath = os.path.join(usage_model_path)
        self.usage_model = pickle.load(open(pickle_filepath, 'rb'))

    def is_test_equal(self, test1, test2):
        if not len(test1) == len(test2):
            return False
        i = 0
        while i < len(test1):
            if not self.is_event_equal(test1[i], test2[i]):
                return False
        return True

    def save_test(self, current_generated_test):
        self.test_num += 1
        for test_file in glob.glob(os.path.join(self.generated_tests_dir, 'test_executable*')):
            existing_test = pickle.load(open(test_file, 'rb'))
            if self.is_test_equal(existing_test, current_generated_test):
                return
        file_path = os.path.join(self.generated_tests_dir, 'test_executable' + str(self.test_num) + '.pickle')
        with open(file_path, 'wb') as file:
            pickle.dump(current_generated_test, file)

    def generate_test(self):
        if self.test_num > self.MAX_TEST_NUM:
            return
        step_index = 0
        isEnd = False
        current_generated_test = [] # list of DestEvent
        while step_index < self.MAX_ACTION and not isEnd:
            time.sleep(2)
            current_state = self.explorer.extract_state(self.output_dir)
            current_state.print_state()
            next_event_list = self.find_next_event_list(current_state)
            if len(next_event_list) == 0:
                print('no next event found. ending dynamic generation...')
                break
            elif len(next_event_list) == 1:
                isEnd = next_event_list[0].isEnd
                current_generated_test.append(next_event_list[0])
                self.explorer.execute_event(next_event_list[0])
            else:
                random_idx = random.randint(0, len(next_event_list)-1)
                next_event = next_event_list[random_idx]
                isEnd = next_event.isEnd
                current_generated_test.append(next_event)
                self.explorer.execute_event(next_event)
            step_index += 1

        self.save_test(current_generated_test)
        self.explorer.driver.close_app()
        self.explorer.driver.launch_app()
        self.generate_test()


    def is_event_equal(self, event1, event2):
        if event1.exec_id_type == event2.exec_id_type and event1.exec_id_val == event2.exec_id_val:
            return True
        return False

    def find_mathing_state_in_usage_model(self, current_state):
        ### placeholder for screen classifier
        current_screenIR = input('manually type current state IR based on screenshot here ' + current_state.screenshot_path + '\n')
        print('you typed', current_screenIR)
        triggers = self.usage_model.machine.get_triggers(current_screenIR)
        if len(triggers) == 0:
            ### placeholder for screen classifier to get 2nd, 3rd ... possible matching screenIR when the top1 doesn't have a match ###
            ### should NOT return None but should always find the closest state in the usage model
            return None
        else:
            return current_screenIR

    def classify_widgetIR(self, element):
        ### placeholder for widget classifier ###
        ### element.path_to_screenshot gives you the croped image
        elementIR = input('manually type widget IR based on crop here' + element.path_to_screenshot + '\n')
        print('you typed', elementIR)
        return elementIR

    def find_matching_action_in_app(self, current_state, trigger):
        print('finding matching action for trigger', trigger)
        if trigger == 'self':
            pass ### placeholder, consider input screens ###
        else:
            widgetIR = trigger.split('#')[0]
            action = trigger.split('#')[1]
            # The elements (widgets) are of type of node objects defined in node.py
            for element in current_state.nodes:
                if element.interactable:
                    elementIR = self.classify_widgetIR(element)
                    if elementIR == widgetIR:
                        return element, action
        ### placeholder to relax the criteria and find the closest widget ###
        return None, None

    def is_final_trigger(self, trigger, source):
        if len(self.usage_model.machine.get_transitions(trigger=trigger, source=source, dest='end')) == 0:
            return False
        return True

    def find_next_event_list(self, current_state):
        next_event_list = []
        matching_screenIR = self.find_mathing_state_in_usage_model(current_state)
        if matching_screenIR is None:
            print('no matching state found in the usage model...')
        else:
            for trigger in self.usage_model.machine.get_triggers(matching_screenIR):
                if self.is_final_trigger(trigger=trigger, source=matching_screenIR):
                    isEnd = True
                else:
                    isEnd = False
                matching_element, action = self.find_matching_action_in_app(current_state, trigger)
                if matching_element is None:
                    print('no matching element found on the current screen...')
                else:
                    next_event_list.append(DestEvent(action, matching_element.get_exec_id_type(), matching_element.get_exec_id_val(), '', isEnd))
        return next_event_list

        # In the end your next event is a combination of a widget (next_event_widget) which is the type of the
        # node object defined in node.py. and and action that can be either "click" or "send_keys" or
        # "send_keys_enter" or "long". You can use the code line below to make a DestEvent (which is defined at the top of this file) - if your action type is send keys then the text input
        # argument would be the input ow it would be emmpty string. This funtion should return DestEvent object
        # next_event = DestEvent(action, next_event_widget.get_exec_id_type(),
        #                        next_event_widget.get_exec_id_val(), text_input)
        # return next_event

if __name__ == "__main__":
    start = time.time()
    test_gen = TestGenerator()
    test_gen.start('/Users/yixue/Documents/Research/UsageTesting/UsageTesting-Repo/video_data_examples/dynamic_output',
                   '/Users/yixue/Documents/Research/UsageTesting/UsageTesting-Repo/video_data_examples/usage_model.pickle',
                   'etsy')
    end = time.time()
    print("Dynamic generation running time " + str(end - start) + " seconds")
