import argparse
import os
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

def Merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res

class GeneralKNNClassifier:
    def __init__(self, train_embeddings, embedding_id_dict, labels_paths, k, n_accuracy):
        self.labels_paths = labels_paths
        self.k = k
        self.embeddings = train_embeddings
        self.embedding_id_dict = embedding_id_dict
        self.n_accuracy = n_accuracy
        self.labels_dict = self.read_label_files()

    def run_dynamic_knn_query(self, query_embedding):
        sims = cosine_similarity(self.embeddings, query_embedding.reshape(1, -1))
        top_k = sims.argsort(axis=0)[-self.k:]
        names = []
        for top in top_k:
            names.append(self.embedding_id_dict[top[0]].split("_")[0])
        top_labels  = self.read_labels(names)
        top_n = (sorted(set(top_labels), key=top_labels.count))[-self.n_accuracy:]
        prediction = max(set(top_labels), key=top_labels.count)
        return prediction, top_n

    def run_knn_query(self, query_embedding, query_name):
        sims = cosine_similarity(self.embeddings, query_embedding.reshape(1,-1))
        top_k = sims.argsort(axis=0)[-self.k:]
        names = []
        for top in top_k:
            names.append(self.embedding_id_dict[top[0]].split("_")[0])

        top_labels = self.read_labels(names)
        gt_label = self.read_query_label(query_name)
        top_n = (sorted(set(top_labels), key=top_labels.count))[-self.n_accuracy:]
        prediction = max(set(top_labels), key=top_labels.count)
        return prediction, gt_label, top_n

    def read_label_files(self):
        # df1 = pd.read_csv("final_labels_all.csv", usecols=['screen', 'tag_screen'], na_filter = False)
        df1 = pd.read_csv(self.labels_paths[0], usecols=['screen', 'tag_screen'], na_filter=False)
        df1.screen = (df1.screen.str.rsplit("/", n=1, expand=True)[1])
        df1.screen = (df1.screen.str.rsplit(".", n=1, expand=True)[0])
        label_dict1 = dict(zip(df1.screen, df1.tag_screen))

        # df2 = pd.read_csv("augmented_labels.csv", usecols=['screen', 'tag_screen'], na_filter=False)
        df2 = pd.read_csv(self.labels_paths[1], usecols=['screen', 'tag_screen'], na_filter=False)
        label_dict2 = dict(zip(df2.screen, df2.tag_screen))

        label_dict = Merge(label_dict1, label_dict2)
        return label_dict


    def read_labels(self, names):
        labels = []
        for name in names:
            try:
                labels.append(self.labels_dict[name])
            except:
                pass
        return labels

    def read_query_label(self, query_name):
        try:
            query_label = self.labels_dict[query_name]
        except:
            raise Exception("Query screen does not exist.")

        return query_label

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='General KNN')
    parser.add_argument('--e', type=str, required=True, help='Path to the embeddings folder')
    parser.add_argument('--q', type=str, required=True, help='Path to the query embedding')
    parser.add_argument('--l', type=str, required=True, help='Path to the label file')
    parser.add_argument('--k', type=str, required=True, help='Number of returned nearest neighbors')
    _args = parser.parse_args()
    classifier = GeneralKNNClassifier(_args.e, _args.l, int(_args.k))
    print(classifier.run_knn_query(_args.q))




