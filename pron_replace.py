import sys
import spacy
from queue import Queue


class NovelAnalyzer:
    nlp = None
    filename = ""
    lines = []
    sentences_origin = []
    sentences_important = []
    current_person = ""
    current_people = []
    MAX_PEOPLE_NUM = 4

    end_token = [".", "!", "?"]

    def __init__(self, filename):
        self.filename = filename
        self.nlp = spacy.load("en_core_web_sm")
        for i in range(self.MAX_PEOPLE_NUM):
            self.current_people.append("")

    def read_file(self):
        f = open(self.filename, "r")
        # for line in f.readlines():
        #     self.lines.append(line)

        texts = f.read()
        texts = texts.replace("\n", " ")
        texts = texts.replace("\r", " ")
        doc = self.nlp(texts)
        for s in doc.sents:
            self.sentences_origin.append(s)

        f.close()

    def extract_impt_sentences(self, mode):
        fout = open("pron_sentences.txt", "w")
        i = 0
        in_dialog = False
        if mode == "pron":
            for s in self.sentences_origin:
                i += 1
                if i % 100 == 0:
                    print(i)

                if in_dialog:
                    in_dialog = False

                # s_doc = self.nlp(s.string)
                s_doc = s.as_doc()
                s_ents = s_doc.ents
                s_people = []

                for e in s_ents:
                    if e.label_ == "PERSON":
                        s_people.append((e.text, e.start_char))
                        # self.current_people.put(e.text)
                        # self.current_person = e.text


                    # print(e.text, e.label_)
                print()
                print(s_people)
                print(self.current_people)
                print()


                token_loc = 0
                s_people_idx = 0
                for token in s_doc:
                    if token.tag_ == "\'\'":
                        in_dialog = not in_dialog
                    if in_dialog:
                        print("d: ", end="")
                    if len(s_people) > s_people_idx:
                        if token_loc >= s_people[s_people_idx][1]:
                            # print()
                            # print(s_people[s_people_idx])
                            # print()
                            person_name = s_people[s_people_idx][0]
                            self.add_person(person_name)
                            s_people_idx += 1

                    print(token.text, token.tag_, token_loc)
                    fout.write(token.text)
                    if not in_dialog:
                        if token.tag_ == "PRP":
                            print("FIND PRP")
                            fout.write("|||")
                            # if not self.current_people.empty():
                            #     fout.write(self.current_people.get())
                            #     fout.write("|||")

                            if token.lower_ == "they" or token.lower_ == "them":
                                allpeople = ""
                                for pn in self.current_people:
                                    if not pn == "":
                                        allpeople = allpeople + pn
                                        allpeople = allpeople + "|"
                                if not allpeople == "":
                                    fout.write(allpeople)
                                    fout.write("|||")
                                else:
                                    fout.write("UNKNOWN_PEOPLE_NAMES|||")
                            else:
                                if not self.current_person == "":
                                    fout.write(self.current_person)
                                    fout.write("|||")
                                else:
                                    fout.write("UNKNOWN_NAME|||")
                        fout.write(" ")
                    else:
                        # TODO: Dialog check
                        None

                    token_loc += len(token.text)
                    token_loc += 1
                fout.write("\n\n")

        fout.close()

    def output_origin_sentences(self, fileout):
        fout = open(fileout, "w")
        for s in self.sentences_origin:
            fout.write(s.string)
            fout.write("\n\n")

        fout.close()

    def add_person(self, pname):
        self.current_person = pname
        if not pname == self.current_people[0]:
            for i in range(self.MAX_PEOPLE_NUM-2, -1, -1):
                self.current_people[i+1] = self.current_people[i]
            self.current_people[0] = pname

    def replace_pronoun(self):
        i = 1

    def extract_tokens(self, sentence, word_mode):
        res_tokens = []

        if word_mode == "pron":
            sentence_doc = sentence.doc
            for w in sentence_doc:
                if w.tag_ == "NNP":
                    res_tokens.append(w)

        return res_tokens



if __name__ == '__main__':
    # filename = sys.argv[1]
    filename = "test.txt"
    pron_replacer = NovelAnalyzer(filename)
    pron_replacer.read_file()
    # pron_replacer.output_origin_sentences("sentences.txt")
    pron_replacer.extract_impt_sentences("pron")
    # pron_replacer.replace_pronoun()

