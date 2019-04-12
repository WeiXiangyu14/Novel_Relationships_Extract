import nltk
nltk.download('punkt')


class RelationExtract:
    def __init__(self, path="./Corpus/Harry Potter and the Sorcerer's Stone.txt"):
        self.path = path
        self.name_list = None
        self.sentences = None

    @staticmethod
    def extract_sentence(path):
        f = open(path, 'r')
        text = f.read().replace("\n", " ")
        f.close()
        sentences = nltk.tokenize.sent_tokenize(text)
        print("Totally ", len(sentences), "sentences.")
        return sentences

    @staticmethod
    def get_name_list():
        f = open("./Corpus/namelist.txt")
        names = f.read().split('\n')
        return [name for name in names if len(name) > 0]

    def get_interest_stcs(self):
        interest = []
        f = open("interest.txt", "w")
        count = 0
        for stcs in self.sentences:
            for name in self.name_list:
                if stcs.find(name) >= 0:
                    interest.append(stcs)
                    f.write(stcs + "\n")
                    break
        print("Interested in ", len(interest), "sentences.")
        f.close()

    def main(self):
        self.name_list = self.get_name_list()
        self.sentences = self.extract_sentence(self.path)
        self.get_interest_stcs()

if __name__ == '__main__':
    re = RelationExtract()
    re.main()
