import nltk
import re
from nltk.parse import CoreNLPParser
from nltk.corpus import sentiwordnet as swn
# import stanfordnlp
import spacy
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import numpy as np
import PIL
from PIL import Image
import matplotlib.pyplot as plt
from sklearn.cluster import SpectralClustering


def download_corpus():
    nltk.download('punkt')
    nltk.download('sentiwordnet')
    nltk.download('wordnet')
    nltk.download('vader_lexicon')
# download_corpus()


class RelationExtract:
    def __init__(self, path="./Corpus/Harry Potter and the Sorcerer's Stone.txt"):
        self.path = path
        self.clean_path = "./clean_text.txt"
        self.replace_text_path = "./replaced_text.txt"
        self.name_list = None
        self.sentences = None
        self.interest = []
        self.chapters = []
        self.interact = {}  # Count how many times two roles interact.
        self.interact_pos = {}  # Count how many times two roles interact positively.
        self.interact_neg = {}  # Count how many times two roles interact negatively.
        # self.nlp = stanfordnlp.Pipeline(use_gpu=False)
        self.sentim_analyzer = SIA()

        self.name2int = {}
        self.int2name = {}
        self.name_look_up = {}
        self.name_replace = {}
        self.pos_mat = None

    def clean_text(self):
        f = open(self.path, "r")
        text = f.read()
        f.close()
        text = text.split(" ")
        text = " ".join(text)
        f = open(self.clean_path, 'w')
        f.write(text)
        f.close()

    def extract_sentence(self, path):
        f = open(self.replace_text_path, 'r')
        text = f.read()
        text = text.replace("\n\n", "\t")
        text = text.replace("\n", " ")
        text = text.replace("\t", "\n")
        f.close()
        sentences = nltk.tokenize.sent_tokenize(text)
        text = text.replace("\"\"", "\". \"")
        f.close()
        sentences = nltk.tokenize.sent_tokenize(text)
        print("Totally ", len(sentences), "sentences.")
        self.sentences = []
        f = open("./sentences.txt", "w")
        sorted_keys = list(self.name_replace.keys())
        sorted_keys.sort(key = lambda i:len(i), reverse=True)
        for stcs in sentences:
            stcs = stcs.lower()
            for key in sorted_keys:
                loc = stcs.find(key)
                if loc < 0:
                    continue
                if loc == 0 or (loc > 0 and (stcs[loc-1] == " " or stcs[loc-1] == "\"") ):
                    if loc + len(key) == len(stcs) - 1 or (loc + len(key) < len(stcs) - 1) and not stcs[loc+len(key)].isalpha():
                        stcs = stcs.replace(key, self.name_replace[key])
            f.write(stcs + "\n")
            self.sentences.append(stcs)
        f.close()

    def get_name_list(self):
        f = open("./Corpus/namelist.txt")
        lines = f.readlines()
        f.close()
        name_list = []
        lookup = {}
        replace = {}
        for l in lines:
            l = l.replace("\n", "")
            index = l.find(":")
            name = l[:index]
            name_list.append(name)
            l = l[index+2:]
            equal = l.split(",")
            for index, alias in enumerate(equal):
                alias = alias.strip().lower()
                # if alias.startswith("mr.") or alias.startswith("ms.") or alias.startswith("mrs."):
                #     alias = alias.replace(" ", "")
                equal[index] = alias
                replace[alias] = name

            lookup[name] = equal

        self.name_list = name_list
        self.name_list.sort(key = lambda i:len(i), reverse=True)
        self.name_look_up = lookup
        self.name_replace = replace
        for index, name in enumerate(self.name_list):
            self.name2int[name] = index
            self.int2name[index] = name


    def get_interest_stcs(self):
        f = open("role_gt_2.txt", "w")
        role_gt_1 = []
        role_gt_2 = []
        for stcs in self.sentences:
            num_roles = 0
            roles = []  # Stores the roles show up in this sentence
            stcs_list = stcs.split()
            for name in self.name_list:
                # if name in stcs_list:
                #     num_roles += 1
                #     roles.append(name)
                if stcs.find(name) > -1:
                    roles.append(name)
                    num_roles += 1
            if num_roles < 2:
                continue

            role_gt_2.append(stcs)
            # doc = self.nlp(stcs)

            pos, neg = self.sentiment_analysis(stcs)

            nsubj = []
            obj = []
            root = None
            # for dep_edge in doc.sentences[0].dependencies:
                # print(dep_edge[2].text, dep_edge[0].index, dep_edge[1])
                # if dep_edge[1] == "root":
                #     root = dep_edge[2].text
                # if dep_edge[1] == "nsubj":
                #     nsubj.append(dep_edge[2].text)
                # if dep_edge[1] == "obj":
                #     obj.append(dep_edge[2].text)

            f.write(stcs + "\n")
            f.write(str(roles) + "\n")
            f.write(str(root) + "\n")
            f.write(str(nsubj) + "\n")
            f.write(str(obj) + "\n")
            f.write("\n\n")

            for i in range(len(roles)):
                for j in range(i+1, len(roles)):
                    # Sort the names by up-order
                    if roles[i] > roles[j]:
                        name1, name2 = roles[j], roles[i]
                    else:
                        name1, name2 = roles[i], roles[j]

                    if (name1, name2) in self.interact:
                        self.interact[name1, name2] += 1
                    else:
                        self.interact[name1, name2] = 1

                    if (name1, name2) in self.interact_pos:
                        self.interact_pos[name1, name2] += pos
                    else:
                        self.interact_pos[name1, name2] = pos
                    if (name1, name2) in self.interact_neg:
                        self.interact_neg[name1, name2] += neg
                    else:
                        self.interact_neg[name1, name2] = neg

        print("Interested in ", len(role_gt_2), "sentences that has >= 2 roles.")
        f.close()

    def sentiment_analysis(self, stcs):
        analyze = self.sentim_analyzer.polarity_scores(stcs)
        pos = analyze["pos"]
        neg = analyze["neg"]
        return pos, neg

    def print_interact(self):
        f = open("interact.txt", 'w')
        f.write(str(self.interact))
        f.close()

    def get_chapters(self):     # split text into CHAPTER
        chapter = []
        for i, stcs in enumerate(self.sentences):
            if "CHAPTER" in stcs.split():
                if len(chapter) > 0:
                    self.chapters.append(chapter)
                    chapter = []
            else:
                chapter.append(stcs)

    def fine_tuning(self):
        f = open("fine_sentences.txt", 'w')
        fine_stcs = []
        i = 0
        while i < len(self.sentences):
            # TODO: deal with mis-separation of "$Sentences".
            # Problem: some little error in "" pairs.
            stcs = self.sentences[i]
            n_cite = stcs.count("\"")
            if n_cite % 2 == 1:
                count = n_cite
                while count % 2 == 1:
                    i += 1
                    count += self.sentences[i].count("\"")
                    stcs += self.sentences[i]

            i += 1
            fine_stcs.append(stcs)
            f.write(stcs + "\n")
        # TODO: deal with talk and speaker
        f.close()

    def simple_ner(self):
        ner_tagger = CoreNLPParser(url='http://localhost:9000', tagtype='ner')
        names = []
        f = open("namelist.txt", "w")

        for i, stcs in enumerate(self.sentences):
            nertag = list(ner_tagger.tag((stcs.split())))
            namelist = [x[0] for x in nertag if x[1] == "PERSON"]
            if i % 20 == 0:
                print("processing: sentence", i, "of ", len(self.sentences))
            for name in namelist:
                if name not in names:
                    names.append(name)
                    f.write(name + "\n")
        f.close()

    def get_sentiment_mat(self, senti_dict):
        senti_mat = np.zeros((len(self.name_list), len(self.name_list)))
        for name1 in self.name_list:
            i = self.name2int[name1]
            for name2 in self.name_list:
                if name1 > name2:
                    name1, name2 = name2, name1
                j = self.name2int[name2]
                if (name1, name2) in senti_dict:
                    senti_mat[i, j] = senti_dict[name1, name2]
        # TODO: DEBUG, all zero
        print(senti_mat)
        return senti_mat

    @staticmethod
    def create_senti_image(senti_mat):
        im = Image.fromarray(senti_mat)
        im.save("interact.jpeg")
        return im

    def cluster_analyze(self, mat):
        mat = np.mat(mat)
        n_clusters = 3
        clusters = SpectralClustering(n_clusters).fit_predict(mat)
        f = open('cluster.txt', 'w')
        for i, cls in enumerate(clusters):
            f.write("Name:" + str(self.int2name[i]) + "; cluster: " + str(cls) + "\n")
        f.close()
        return clusters

    def main(self):
        self.clean_text()
        self.get_name_list()
        self.extract_sentence(self.clean_path)
        # self.get_chapters()
        self.get_interest_stcs()
        # self.print_interact()
        interact_mat = self.get_sentiment_mat(self.interact)
        np.savetxt("interact.txt", interact_mat)
        # self.cluster_analyze(interact_mat)
        plt.matshow(interact_mat)
        plt.show()


if __name__ == '__main__':
    extractor = RelationExtract()
    extractor.main()