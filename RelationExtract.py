import nltk
import re
from nltk.parse import CoreNLPParser
from nltk.corpus import sentiwordnet as swn
import stanfordnlp


def download_corpus():
    nltk.download('punkt')
    nltk.download('sentiwordnet')
    nltk.download('wordnet')


class RelationExtract:
    def __init__(self, path="./Corpus/Harry Potter and the Sorcerer's Stone.txt"):
        self.path = path
        self.name_list = None
        self.sentences = None
        self.interest = []
        self.chapters = []
        self.interact = {}  # Count how many times two roles interact.
        self.interact_pos = {}  # Count how many times two roles interact positively.
        self.interact_neg = {}  # Count how many times two roles interact negatively.
        self.nlp = stanfordnlp.Pipeline()

    @staticmethod
    def extract_sentence(path):
        f = open(path, 'r')
        text = f.read()
        text = text.replace("\n\n", "\t")
        text = text.replace("\n", " ")
        text = text.replace("\t", "\n")
        text = text.replace("\"\"", "\". \"")
        f.close()
        sentences = nltk.tokenize.sent_tokenize(text)
        print("Totally ", len(sentences), "sentences.")
        f = open("./sentences.txt", "w")
        for stcs in sentences:
            f.write(stcs + "\n")
        f.close()
        return sentences

    @staticmethod
    def get_name_list():
        f = open("./Corpus/namelist.txt")
        names = f.read().split('\n')
        f.close()
        return [name for name in names if len(name) > 0]

    def get_interest_stcs(self):
        f = open("role_gt_2.txt", "w")
        role_gt_1 = []
        role_gt_2 = []
        # for stcs in self.sentences:
        #     for name in self.name_list:
        #         if stcs.find(name) >= 0:
        #             role_gt_1.append(stcs)
        #             f.write(stcs + "\n")
        #             break
        for stcs in self.sentences:
            num_roles = 0
            roles = []  # Stores the roles show up in this sentence
            stcs_list = stcs.split()
            for name in self.name_list:
                if name in stcs_list:
                    num_roles += 1
                    roles.append(name)
            if num_roles < 2:
                continue

            role_gt_2.append(stcs)
            doc = self.nlp(stcs)

            get_sentiment = self.sentiment_analysis(stcs)

            nsubj = []
            root = None
            for dep_edge in doc.sentences[0].dependencies:
                print(dep_edge[2].text, dep_edge[0].index, dep_edge[1])
                if dep_edge[1] == "root":
                    root = dep_edge[2].text
                if dep_edge[1] == "nsubj":
                    nsubj.append(dep_edge[2].text)

            f.write(stcs + "\n")
            f.write(str(roles) + "\n")
            f.write(str(root) + "\n")
            f.write(str(nsubj) + "\n")
            f.write("\n\n")

            for i in range(len(roles)):
                for j in range(i+1, len(roles)):
                    # Sort the names by up-order
                    if roles[i] > roles[j]:
                        name1, name2 = roles[j], roles[i]
                    else:
                        name1, name2 = roles[i], roles[j]

                    if (name1, name2) in self.interacts in self.interact:
                        self.interact[name1, name2] += 1
                    else:
                        self.interact[name1, name2] = 1

        print("Interested in ", len(role_gt_2), "sentences that has >= 2 roles.")
        f.close()

    @staticmethod
    def sentiment_analysis(sentence):
        # TODO: to be implemented
        return 0

    def print_interact(self):
        f = open("interact.txt", 'w')
        # for i, name1 in enumerate(self.name_list):
        #     for j, name2 in enumerate(self.name_list):
        #         if (name1, name2) in self.interact:
        #             f.write(str(self.interact[name1, name2]) + " ")
        #         else:
        #             self.interact[name1, name2] = 0
        #             f.write(str(self.interact[name1, name2]) + " ")
        #     f.write("\n")
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

    def main(self):
        self.name_list = self.get_name_list()
        self.sentences = self.extract_sentence(self.path)
        # self.fine_tuning()
        self.get_chapters()
        self.get_interest_stcs()
        self.print_interact()


if __name__ == '__main__':
    extractor = RelationExtract()
    extractor.main()

