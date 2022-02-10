import sys, os
sys.path.insert(0, 'autoencoder/')
sys.path.insert(0, 'autoencoder/aeSrc')
sys.path.insert(0, 'autoencoder_KNN/')

from dynamicXML2JSON_convertor import convert_to_json_new_data
from createSilhouette import createUIImage
from getEmbeddings import getAEembeddings
from screen_classifier_KNN_autoencoder import KNN_screen_classifier

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

    def get_screenIR(self, AUT):
        convert_to_json_new_data(self.UIXML_path)  # will output the json at the same directory as the xml input
        createUIImage(self.UIXML_path.replace('xml', 'json'))
        screen_embedding_autoencoder = getAEembeddings(os.path.dirname(self.UIXML_path), self.UIXML_path.replace('.xml', '-layout.jpg'))
        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        embeddings_path = os.path.join(current_dir_path, "autoencoder_KNN", "autoencoder_embeddings")
        k = 10
        n = 10
        labels_path = [os.path.join(current_dir_path, "autoencoder_KNN/final_labels_all.csv"),
                       os.path.join(current_dir_path, "autoencoder_KNN/augmented_labels.csv")]
        screen_classifier = KNN_screen_classifier(AUT, embeddings_path, labels_path, k, n)
        screenIR, top_n_screenIR = screen_classifier.run_knn_query(screen_embedding_autoencoder)
        print('screenIR results:', screenIR, top_n_screenIR)
        return screenIR

if __name__ == '__main__':
    state = State('')
    state.UIXML_path = '/Users/yixue/Documents/Research/UsageTesting/Final-Artifacts/output/models/1-SignIn/dynamic_output/etsy/screenshots/0-1.xml'
    state.get_screenIR('etsy')
