import nltk
nltk.download('punkt')


class RelationExtract:
    def __init__(self, path="./Corpus/Harry Potter and the Sorcerer's Stone.txt"):
        self.path = path
        self.name_list = None
        self.sentences = None
        self.interest = []

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
        f = open("interest.txt", "w")
        for stcs in self.sentences:
            for name in self.name_list:
                if stcs.find(name) >= 0:
                    self.interest.append(stcs)
                    f.write(stcs + "\n")
                    break
        print("Interested in ", len(self.interest), "sentences.")
        f.close()

    def fine_tuning(self):
        f = open("fine_sentences.txt", 'w')
        for i, stcs in enumerate(self.sentences):
            # First split text in CHAPTER
            if stcs.find("CHAPTER"):
                # TODO: split text into CHAPTER
                pass

    def main(self):
        self.name_list = self.get_name_list()
        self.sentences = self.extract_sentence(self.path)
        self.get_interest_stcs()

if __name__ == '__main__':
    re = RelationExtract()
    re.main()
