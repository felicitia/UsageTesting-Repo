import sys, os

current_dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(current_dir_path, 'autoencoder'))
sys.path.insert(0, os.path.join(current_dir_path, 'autoencoder', 'aeSrc'))
sys.path.insert(0, os.path.join(current_dir_path, 'autoencoder_KNN'))
sys.path.insert(0, os.path.join(current_dir_path, 'autoencoder_MLP'))

import PIL, psutil
import pandas as pd
from dynamicXML2JSON_convertor import convert_to_json_dynamic
from REMAUI_XML2JSON_convertor import convert_to_json_REMAUI
from createSilhouette import createUIImage
from getEmbeddings import getAEembeddings
from screen_classifier_KNN_autoencoder import KNN_screen_classifier
from MLP_classify import MLP_ScreenClassifierForAUT

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

    def get_dynamic_embedding(self):
        convert_to_json_dynamic(self.UIXML_path)  # will output the json at the same directory as the xml input
        createUIImage(self.UIXML_path.replace('xml', 'json'))
        return getAEembeddings(os.path.dirname(self.UIXML_path), self.UIXML_path.replace('.xml', '-layout.jpg'))


    def get_REMAUI_embedding(self):
        XML_basename = os.path.basename(os.path.normpath(self.UIXML_path)).replace('.xml', '')
        REMAUI_XML_path = os.path.join(os.path.dirname(self.UIXML_path), '..', 'REMAUI', XML_basename, 'activity_main.xml')
        convert_to_json_REMAUI(REMAUI_XML_path)  # will output the json at the same directory as the xml input
        createUIImage(REMAUI_XML_path.replace('xml', 'json'))
        return getAEembeddings(os.path.dirname(REMAUI_XML_path), REMAUI_XML_path.replace('.xml', '-layout.jpg'))

    def get_screenIR(self, AUT, usage_model, text_sim_w2v, text_sim_bert, REMAUI_flag):
        dynamicXML_embedding_autoencoder = self.get_dynamic_embedding()
        REMAUI_embedding_autoencoder = None
        if REMAUI_flag:
            REMAUI_embedding_autoencoder = self.get_REMAUI_embedding()

        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        embeddings_path = os.path.join(current_dir_path, "autoencoder_KNN", "autoencoder_embeddings")
        K = 5
        N = 5
        labels_path = [os.path.join(current_dir_path, "autoencoder_KNN/final_labels_all.csv"),
                       os.path.join(current_dir_path, "autoencoder_KNN/augmented_labels.csv")]
        screen_classifier_KNN = KNN_screen_classifier(AUT, embeddings_path, labels_path, K, N)
        screen_classifier_MLP = MLP_ScreenClassifierForAUT(autoencoder=True)


        # Find Screen title (top-left corner)
        screenIR_KNN, top_n_screenIR_KNN = screen_classifier_KNN.run_knn_query(dynamicXML_embedding_autoencoder)
        screenIR_MLP, top_n_screenIR_MLP = screen_classifier_MLP.classify(dynamicXML_embedding_autoencoder, AUT, N)

        KNN_states, top_n_KNN_states = screen_classifier_KNN.run_knn_query_states(dynamicXML_embedding_autoencoder, usage_model.states)



        screenIR_MLP_all, top_n_screenIR_MLP_all = screen_classifier_MLP.classify_allapp_as_training(dynamicXML_embedding_autoencoder, N)




        screenIR_MLP_states, top_n_screenIR_MLP_states = screen_classifier_MLP.train_and_classify_for_states(AUT,dynamicXML_embedding_autoencoder,
                                                                                                       N, usage_model.states)


        # screenIR_MLP_states_all, top_n_screenIR_MLP_states_all = screen_classifier_MLP.train_and_classify_for_states('allapps',
        #                                                                                                dynamicXML_embedding_autoencoder,
        #                                                                                                N, usage_model.states)

        if REMAUI_embedding_autoencoder is not None:
            REMAUI_KNN_states, REMAUI_top_n_KNN_states = screen_classifier_KNN.run_knn_query_states(REMAUI_embedding_autoencoder,
                                                                                  usage_model.states)
            REMAUI_KNN, REMAUI_top_n_KNN = screen_classifier_KNN.run_knn_query(REMAUI_embedding_autoencoder)
            REMAU_MLP, REMAUI_top_n_MLP = screen_classifier_MLP.classify(REMAUI_embedding_autoencoder, AUT, N)

            REMAUI_all, REMAUI_top_n_all = screen_classifier_MLP.classify_allapp_as_training(
                REMAUI_embedding_autoencoder, N)
            REMAUI_states, REMAUI_top_n_states = screen_classifier_MLP.train_and_classify_for_states(AUT,
                                                                                                     REMAUI_embedding_autoencoder,
                                                                                                     N,
                                                                                                     usage_model.states)
            REMAUI_states_all, REMAUI_top_n_states_all = screen_classifier_MLP.train_and_classify_for_states('allapps',
                                                                                                             REMAUI_embedding_autoencoder,
                                                                                                             N,
                                                                                                             usage_model.states)
        print('KNN:', screenIR_KNN, top_n_screenIR_KNN)
        if REMAUI_flag:
            print('REMAUI KNN:', REMAUI_KNN, REMAUI_top_n_KNN)
        print()
        print('MLP:', screenIR_MLP, top_n_screenIR_MLP)
        if REMAUI_flag:
            print('REMAUI MLP:', REMAU_MLP, REMAUI_top_n_MLP)
        print()
        print('MLP all training:', screenIR_MLP_all, top_n_screenIR_MLP_all)
        if REMAUI_flag:
            print('REMAUI all training:', REMAUI_all, REMAUI_top_n_all)
        print()
        print('MLP states partial training:', screenIR_MLP_states, top_n_screenIR_MLP_states)
        if REMAUI_flag:
            print('REMAUI states partial:', REMAUI_states, REMAUI_top_n_states)
        print()
        print('KNN states:', KNN_states, top_n_KNN_states)
        if REMAUI_flag:
            print('REMAUI KNN states:', REMAUI_KNN_states, REMAUI_top_n_KNN_states)
        print()
        # print('MLP states all apps:', screenIR_MLP_states_all, top_n_screenIR_MLP_states_all)
        if REMAUI_flag:
            print('REMAUI states all apps:', REMAUI_states_all, REMAUI_top_n_states_all)
        print()
        print('usage model states:', usage_model.states)
        print()
        all_ir_candidates = set(top_n_screenIR_KNN).union(set(top_n_screenIR_MLP_states))
        all_ir_candidates = list(all_ir_candidates)
        ## filter out results that's NOT from usage model's states and should be excluded
        for ir in all_ir_candidates:
            if (ir not in usage_model.states) or (ir in ['sign_up_birthday', 'signin_amazon', 'signin_fb', 'signin_google', 'signin_google_popup']):
                all_ir_candidates.remove(ir)

        print('filtered top N:', all_ir_candidates)
        print()
        print('Activity:', self.activity)
        activity_wordlist = self.activity.replace('.', ' ').lower().strip()
        print('Activity wordlist:', activity_wordlist)
        print()
        text_info_strs = set()
        text_info_strs.add(activity_wordlist)
        for element in self.nodes:
            for key in element.data:
                if key == 'text':
                    text_info_strs.add(element.data[key])
                if key == 'content-desc':
                    text_info_strs.add(element.data[key])
                if key == 'resource-id':
                    text_info_strs.add(element.data[key].split('/')[-1])
                if key == 'id':
                    text_info_strs.add(element.data[key])
        text_info_strs = " ".join(text_info_strs)
        print('text info:', text_info_strs)

        if text_sim_w2v is not None and text_sim_bert is not None:
            print('-----textual similarities-----')
            for ir_candidate in all_ir_candidates:
                wordlist = self.get_wordlist(ir_candidate)
                print('wordlist:', wordlist)
                # wordlist = ir_candidate
                bert_sim = text_sim_bert.calc_similarity(text_info_strs, wordlist)
                w2v_sim = text_sim_w2v.calc_similarity(text_info_strs, wordlist)
                print(ir_candidate, 'BERT:' + str(bert_sim), 'W2V:' + str(w2v_sim))

        return None


    def get_wordlist(self, screenIR):
        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        wordlist_dir = os.path.join(current_dir_path, '..', '..', 'IR', 'label_texts')
        wordlist_path = os.path.join(wordlist_dir, screenIR + '.txt')
        if os.path.exists(wordlist_path):
            file = open(wordlist_path, "r")
            return file.read().lower()

        return screenIR # if no wordlist is found for the screenIR, use the screenIR name itself as the wordlist


    def find_widget_to_trigger(self, widgetIR):
        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        widget_ir_csv = os.path.join(current_dir_path, '..', '..', 'IR', 'widget_ir.csv')
        widget_df = pd.read_csv(widget_ir_csv)
        row_found = widget_df.loc[widget_df['ir'] == widgetIR]

        if len(row_found) == 0:
            print('widget IR', widgetIR)
            raise ValueError('no widget IR found')
        else:
            widget_type = row_found['widget_type'].values[0]

        input_element_type = ['EditText', 'AutoCompleteTextView', 'Spinner']
        element_candidates = []
        for element in self.nodes:
            if element.interactable:

                element_type = element.get_element_type().split('.')[-1]
                if (widget_type == 'input' and element_type not in input_element_type) \
                        or (pd.isna(widget_type) and element_type in input_element_type):
                    continue
                element_candidates.append(element)
        for element in element_candidates:
            image = PIL.Image.open(element.path_to_screenshot)
            image.show()
            # element.data # has content-desc, resource-id, text
        i = int(input('widget index to trigger\n'))
        # kill all the images opened by Preview
        for proc in psutil.process_iter():
            # print(proc.name())
            if proc.name() == 'Preview':
                proc.kill()
        if i >= len(element_candidates):
            return None
        return element_candidates[i]



if __name__ == '__main__':
    state = State('')
    state.UIXML_path = '/Users/yixue/Documents/Research/UsageTesting/Final-Artifacts/output/models/1-SignIn/dynamic_output/etsy/screenshots/0-1.xml'
    # state.nodes = ['a', 'b']
    print('all done! :)')
