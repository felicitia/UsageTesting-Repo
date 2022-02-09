import sys, os
sys.path.insert(0, '/Users/yixue/Documents/Research/UsageTesting/UsageTesting-Repo/code/4_dynamic_generation/autoencoder/')
sys.path.insert(0, '/Users/yixue/Documents/Research/UsageTesting/UsageTesting-Repo/code/4_dynamic_generation/autoencoder/aeSrc')

from dynamicXML2JSON_convertor import convert_to_json_new_data
from createSilhouette import createUIImage
from getEmbeddings import getAEembeddings

class State:
    def __init__(self, screenshot):
        self.screenshot = screenshot
        self.nodes = []
        self.actions = {}
        self.name_actions = {}
        self.activity = ''
        self.transitions = {}
        self.screenshot_path = ''
        self.UIXML_path = ''

    def add_screenshot_path(self, path):
        self.screenshot_path = path

    def add_UIXML_path(self, path):
        self.UIXML_path = path

    def add_node(self, node):
        self.nodes.append(node)

    def get_node(self, node_id):
        return self.nodes[node_id]

    def get_actions(self):
        return self.actions

    def get_name_actions(self):
        return self.name_actions

    def add_action(self, node_id, tag, action_type):
        self.actions[node_id]=action_type
        self.name_actions[tag]=action_type

    def set_activity(self, activity_name):
        self.activity = activity_name

    def add_transition(self, action, state):
        self.transitions[action] = state

    def print_state(self):
        print('Activity:', self.activity)
        print('Actions:', self.name_actions)
        print("-------------------")
        for node in self.nodes:
            if node.interactable:
                print(node.get_exec_identifiers())
        print("-------------------")

    def get_screenIR(self):
        convert_to_json_new_data(self.UIXML_path)  # will output the json at the same directory as the xml input
        createUIImage(self.UIXML_path.replace('xml', 'json'))
        getAEembeddings(os.path.dirname(self.UIXML_path))
        return 'home'

if __name__ == '__main__':
    state = State('')
    state.UIXML_path = '/Users/yixue/Documents/Research/UsageTesting/Final-Artifacts/output/models/1-SignIn/dynamic_output/etsy/screenshots/0-0.xml'
    state.get_screenIR()
