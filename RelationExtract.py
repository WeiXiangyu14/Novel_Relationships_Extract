import nltk
# nltk.download('punkt')


class RelationExtract:
    def __init__(self, path="./Corpus/Harry Potter and the Sorcerer's Stone.txt"):
        self.path = path
        self.name_list = self.get_name_list()
        self.sentences = self.extract_sentence(self.path)

    @staticmethod
    def extract_sentence(path):
        f = open(path, 'r')
        text = f.read().replace("\n", " ")
        print(len(text))
        f.close()
        sentences = nltk.tokenize.sent_tokenize(text)
        return sentences

    @staticmethod
    def get_name_list():
        f = open("./Corpus/namelist.txt")
        names = f.read().split('\n')
        return [name for name in names if len(name) > 0]

    def main(self):
        print(len(self.sentences))
        print(self.sentences)


if __name__ == '__main__':
    re = RelationExtract()
    re.main()
