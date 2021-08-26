import PIL
from appium import webdriver
import layout_tree as LayoutTree
import time
import os, csv
from appium.webdriver.common.touch_action import TouchAction
import pickle
import sys
sys.path.insert(0, '/Users/yixue/Documents/Research/UsageTesting/UsageTesting-Repo/code/3_model_generation')
from entities import IR_Model
from pathlib import Path
import pandas as pd

class Explorer:
    def __init__(self, desiredCapabilities):
        # replace with you own desired capabilities for Appium
        self.desiredCapabilities = desiredCapabilities
        # make sure too change to port your Appium server is listening on
        d = webdriver.Remote('http://localhost:4723/wd/hub', self.desiredCapabilities)
        assert d is not None
        self.driver = d
        self.screenshot_idx = 0
        self.test_num = 0

    def execute_test(self, test_file):
        test = pickle.load(open(test_file, 'rb'))
        for event in test:
            if type(event) is list:
                for self_event in event:
                    self.execute_event(self_event)
            else:
                self.execute_event(event)

    def add_new_annotation(self, new_annotation_dict, filepath, IR):
        new_annotation_dict['filepath'].append(filepath)
        new_annotation_dict['IR'].append(IR)

    def execute_test_and_generate_models(self, test_file):
        test = pickle.load(open(test_file, 'rb'))
        linear_model = []
        ir_model = IR_Model(os.path.basename(os.path.normpath(test_file)))
        dynamic_annotation_file = os.path.join(Path(test_file).parent.parent.parent.parent.absolute(), 'dynamic_annotations.csv')
        if not os.path.exists(dynamic_annotation_file):
            headers = ['filepath', 'IR']
            with open(dynamic_annotation_file, 'w') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(headers)
        annotation_df = pd.read_csv(dynamic_annotation_file)
        new_annotation_dict = {'filepath': [], 'IR': []}

        for event in test:
            if type(event) is list:
                for self_event in event:
                    image = PIL.Image.open(self_event.state_screenshot_path)
                    image.show()
                    current_screenIR = input('type current screen IR shown in the screenshot\n')
                    self.add_new_annotation(new_annotation_dict=new_annotation_dict, filepath=self_event.state_screenshot_path,
                                            IR=current_screenIR)
                    action = self_event.action
                    if 'swipe' in action:
                        swipe_direction = event.action.split('-')[1]
                        linear_model.append({'state': current_screenIR, 'transition': swipe_direction})
                    else:
                        image = PIL.Image.open(self_event.crop_screenshot_path)
                        image.show()
                        widgetIR = input('type widget IR that is about to trigger\n')
                        self.add_new_annotation(new_annotation_dict=new_annotation_dict, filepath=self_event.crop_screenshot_path,
                                                IR=widgetIR)
                        transition_name = widgetIR + '#' + action
                        linear_model.append({'state': current_screenIR, 'transition': transition_name})
                    self.execute_event(self_event)
            else:
                image = PIL.Image.open(event.state_screenshot_path)
                image.show()
                current_screenIR = input('type current screen IR shown in the screenshot\n')
                self.add_new_annotation(new_annotation_dict=new_annotation_dict,
                                        filepath=event.state_screenshot_path,
                                        IR=current_screenIR)
                action = event.action
                if 'swipe' in action:
                    swipe_direction = event.action.split('-')[1]
                    linear_model.append({'state': current_screenIR, 'transition': swipe_direction})
                else:
                    image = PIL.Image.open(event.crop_screenshot_path)
                    image.show()
                    widgetIR = input('type widget IR that is about to trigger\n')
                    self.add_new_annotation(new_annotation_dict=new_annotation_dict,
                                            filepath=event.crop_screenshot_path,
                                            IR=widgetIR)
                    transition_name = widgetIR + '#' + action
                    linear_model.append({'state': current_screenIR, 'transition': transition_name})
                self.execute_event(event)
        annotation_df = pd.concat([annotation_df, pd.DataFrame(new_annotation_dict)], ignore_index=True)
        annotation_df.to_csv(dynamic_annotation_file, index=False)
        print(linear_model)

    def extract_state(self, output_dir):
        layout = LayoutTree.LayoutTree(self.driver, output_dir)
        curr_state = layout.extract_state()
        for element in curr_state.nodes:
            if element.interactable:
                if 'content-desc' in element.attributes.keys():
                    element.add_data('content-desc', element.attributes['content-desc'])
                    element.add_exec_identifier('accessibility-id', element.attributes['content-desc'])

                if 'id' in element.attributes.keys():
                    element.add_data('id', element.attributes['id'])
                    element.add_exec_identifier('id', element.attributes['id'])

                if 'resource-id' in element.attributes.keys():
                    element.add_data('resource-id', element.attributes['resource-id'])
                    element.add_exec_identifier('resource-id', element.attributes['resource-id'])

                if 'text' in element.attributes.keys():
                    element.add_data('text', element.attributes['text'])
        if not os.path.isdir(os.path.join(output_dir, 'screenshots')):
            os.makedirs(os.path.join(output_dir, 'screenshots'))
        screenshot_path = os.path.join(output_dir, 'screenshots', str(self.test_num) + '-' + str(self.screenshot_idx) + '.png')
        self.driver.save_screenshot(screenshot_path)
        xml_path = os.path.join(output_dir, 'screenshots', str(self.test_num) + '-' + str(self.screenshot_idx) + '.xml')
        with open(xml_path, "w") as file:
            file.write(self.driver.page_source)
        curr_state.add_screenshot_path(screenshot_path)
        self.screenshot_idx += 1
        return curr_state

    def execute_swipe(self, direction):
        # Get screen dimensions
        screen_dimensions = self.driver.get_window_size()
        if direction == 'up':
            # Set co-ordinate X according to the element you want to scroll on.
            location_x = screen_dimensions["width"] * 0.5
            # Set co-ordinate start Y and end Y according to the scroll driection up or down
            location_start_y = screen_dimensions["height"] * 0.6
            location_end_y = screen_dimensions["height"] * 0.3
            # Perform vertical scroll gesture using TouchAction API.
            TouchAction(self.driver).press(x=location_x, y=location_start_y).wait(1000)\
                .move_to(x=location_x, y=location_end_y).release().perform()
        if direction == 'down':
            # Set co-ordinate X according to the element you want to scroll on.
            location_x = screen_dimensions["width"] * 0.5
            # Set co-ordinate start Y and end Y according to the scroll driection up or down
            location_start_y = screen_dimensions["height"] * 0.3
            location_end_y = screen_dimensions["height"] * 0.6
            # Perform vertical scroll gesture using TouchAction API.
            TouchAction(self.driver).press(x=location_x, y=location_start_y).wait(1000) \
                .move_to(x=location_x, y=location_end_y).release().perform()
        if direction == 'left':
            # Set co-ordinate start X and end X according
            location_start_x = screen_dimensions["width"] * 0.8
            location_end_x = screen_dimensions["width"] * 0.2
            # Set co-ordinate Y according to the element you want to swipe on.
            location_y = screen_dimensions["height"] * 0.5
            # Perform swipe gesture using TouchAction API.
            TouchAction(self.driver).press(x=location_start_x, y=location_y).wait(1000) \
                .move_to(x=location_end_x, y=location_y).release().perform()
        if direction == 'right':
            # Set co-ordinate start X and end X according
            location_start_x = screen_dimensions["width"] * 0.2
            location_end_x = screen_dimensions["width"] * 0.8
            # Set co-ordinate Y according to the element you want to swipe on.
            location_y = screen_dimensions["height"] * 0.5
            # Perform swipe gesture using TouchAction API.
            TouchAction(self.driver).press(x=location_start_x, y=location_y).wait(1000) \
                .move_to(x=location_end_x, y=location_y).release().perform()

    def execute_event(self, event): # return the name of next state (will end test generation is it's 'end')
        element = None
        alreadyClicked = False
        actions = TouchAction(self.driver)
        print('executing event:', event.exec_id_type, event.exec_id_val, event.action)

        if event.exec_id_type == "accessibility-id":
            time.sleep(3)
            # print(event.exec_id_val)
            element = self.driver.find_element_by_accessibility_id(event.exec_id_val)

        if event.exec_id_type == "xPath":
            time.sleep(3)
            element = self.driver.find_element_by_xpath(event.exec_id_val[0])

        if event.exec_id_type == "resource-id":
            time.sleep(3)
            element = self.driver.find_element_by_id(event.exec_id_val)

        if 'swipe' in event.action:
            time.sleep(3)
            swipe_direction = event.action.split('-')[1]
            self.execute_swipe(swipe_direction)

        if event.action == 'long':
            time.sleep(3)
            alreadyClicked = True
            actions.long_press(element).release().perform()

        if event.action == "send_keys":
            time.sleep(3)
            element.click()
            alreadyClicked = True
            time.sleep(1)
            element.send_keys(event.text_input)

        if event.action == "send_keys_enter":
            time.sleep(3)
            element.click()
            alreadyClicked = True
            time.sleep(1)
            element.send_keys(event.text_input)
            self.driver.press_keycode(66)

        if not alreadyClicked and event.action == 'click':
            element.click()



if __name__ == "__main__":
    desiredCapabilities = {
        "platformName": "Android",
        "deviceName": "emulator-5554",
        "newCommandTimeout": 10000,
        "appPackage": "com.etsy.android",
        "appActivity": "com.etsy.android.ui.homescreen.HomescreenTabsActivity"
    }
    explorer = Explorer(desiredCapabilities)
    while True:
        direction = input('enter swipe direction')
        time.sleep(5)
        explorer.execute_swipe(direction)
    # explorer.extract_state("example_extraction_output")

