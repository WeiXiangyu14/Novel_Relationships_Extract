import sys
import os
import spacy


class NovelAnalyzer:
    filename = ""
    lines = []
    sentences_origin = []
    sentences_important = []

    end_token = [".", "!", "?"]

    def __index__(self, filename):
        self.filename = filename

    def read_file(self):
        f = open(self.filename, "r")
        for line in f.readlines():
            self.lines.append(line)
        f.close()

    def extract_sentence(self, mode):
        curr_sentence = []
        for line in self.lines:
            words = line.split()
            for w in words:
                ### modify with tokenization

                curr_sentence.append(w)
                if w in self.end_token:
                    self.sentences_origin.append(curr_sentence)
                    curr_sentence = []

        if mode == "pron":
            for s in self.sentences_origin:
                prons = self.extract_words(s, mode)
                if len(prons) > 0:
                    self.sentences_important.append(s)

    def replace_pronoun(self):
        for s in self.sentences_important:
            ###
            i = 0


    def extract_words(self, sentence, word_mode):
        res_words = []
        ###

        if word_mode == "pron":
            words = sentence.split()
            for w in words:
                ###
                res_words.append(w)


        ###
        return res_words



if __name__ == '__main__':
    filename = sys.argv[1]
    pron_replacer = NovelAnalyzer(filename)
    pron_replacer.read_file()
    pron_replacer.extract_sentence("pron")
    pron_replacer.replace_pronoun()

