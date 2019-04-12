import nltk


class RelationExtract:
    def __init__(self, path="./Corpus/Harry Potter and the Sorcerer's Stone.txt"):
        self.f = open(path, 'r')
        self.name_list = self.get_name_list()

    def extract_sentence(self):
        pass

    def get_name_list(self):
        f = open("./Corpus/namelist.txt")
        names = f.read().split('\n')
        return [name for name in names if len(name) > 0]

    def main(self):
        pass


if __name__ == '__main__':
    re = RelationExtract()
    re.main()
