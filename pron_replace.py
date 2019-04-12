import sys
import os
import nltk


class NovelAnalyzer:
    filename = ""
    lines = []
    sentences = []
    end_token = [".", "!", "?"]

    def __index__(self, filename):
        self.filename = filename

    def read_file(self):
        f = open(self.filename, "r")
        for line in f.readlines():
            self.lines.append(line)
        f.close()

    def extract_sentence(self):
        curr_sentence = []
        for line in self.lines:
            words = line.split()
            for w in words:
                if w in self.end_token:
                    self.sentences.append(curr_sentence)
                    curr_sentence = []
                else:
                    curr_sentence.append(w)


if __name__ == '__main__':
    filename = sys.argv[1]
    pron_replacer = NovelAnalyzer(filename)
    pron_replacer.read_file()
    pron_replacer.extract_sentence()

