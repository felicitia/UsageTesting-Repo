from appium import webdriver
import layout_tree as LayoutTree
import time
import os
from appium.webdriver.common.touch_action import TouchAction
import pickle

class Explorer:
    def __init__(self):
        # replace with you own desired capabilities for Appium
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",
            "newCommandTimeout": 10000,
            "appPackage": "com.etsy.android",
            "appActivity": "com.etsy.android.ui.homescreen.HomescreenTabsActivity"
        }

        # make sure too change to port your Appium server is listening on
        d = webdriver.Remote('http://localhost:4723/wd/hub', self.desiredCapabilities)
        assert d is not None
        self.driver = d
        self.screenshot_idx = 0

    def execute_test(self, test_file):
        test = pickle.load(open(test_file, 'rb'))
        for event in test:
            self.execute_event(event)

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
        screenshot_path = os.path.join(output_dir, 'screenshots', str(self.screenshot_idx) + '.png')
        self.driver.save_screenshot(screenshot_path)
        curr_state.add_screenshot_path(screenshot_path)
        self.screenshot_idx += 1
        return curr_state

    def execute_event(self, event): # return the name of next state (will end test generation is it's 'end')
        element = None
        alreadyClicked = False
        actions = TouchAction(self.driver)
        print('executing event:', event.exec_id_type, event.exec_id_val, event.action)

        if event.exec_id_type == "accessibility-id":
            time.sleep(2)
            # print(event.exec_id_val)
            element = self.driver.find_element_by_accessibility_id(event.exec_id_val)

        if event.exec_id_type == "xPath":
            time.sleep(2)
            element = self.driver.find_element_by_xpath(event.exec_id_val[0])

        if event.exec_id_type == "resource-id":
            time.sleep(2)
            element = self.driver.find_element_by_id(event.exec_id_val)

        if event.action == 'long':
            time.sleep(2)
            alreadyClicked = True
            actions.long_press(element)
            actions.perform()

        if event.action == "send_keys":
            time.sleep(2)
            element.click()
            alreadyClicked = True
            time.sleep(1)
            element.send_keys(event.text_input)

        if event.action == "send_keys_enter":
            time.sleep(2)
            element.click()
            alreadyClicked = True
            time.sleep(1)
            element.send_keys(event.text_input)
            self.driver.press_keycode(66)

        if not alreadyClicked:
            element.click()



if __name__ == "__main__":
    explorer = Explorer()
    explorer.extract_state("example_extraction_output")

