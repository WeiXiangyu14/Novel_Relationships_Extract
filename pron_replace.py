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
    print_log = True

    end_token = [".", "!", "?"]
    out_dialog_token = ["said"]
    first_pron_token = ["i", "me", "we", "us"]
    second_pron_token = ["you"]
    third_people_token = ["they", "them"]
    third_person_token = ["he", "she", "him", "her"]

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
        texts = texts.replace("\"\"", "\" \"")
        doc = self.nlp(texts)
        for s in doc.sents:
            self.sentences_origin.append(s)

        f.close()

    def extract_impt_sentences(self, mode):
        fout = open("pron_sentences.txt", "w")
        i = 0
        in_dialog = False
        last_token_text = ""
        if mode == "pron":
            for s in self.sentences_origin:
                i += 1
                if i % 100 == 0:
                    print(i)

                # if in_dialog:
                #     in_dialog = False

                # s_doc = self.nlp(s.string)
                s_doc = s.as_doc()
                s_ents = s_doc.ents
                s_people = []

                for e in s_ents:
                    if e.label_ == "PERSON":
                        s_people.append((e.text, e.start_char))
                        # self.current_people.put(e.text)
                        # self.current_person = e.text

                if self.print_log:
                    print()
                    print(s_people)
                    print(self.current_people)
                    print()


                token_loc = 0
                s_people_idx = 0
                for token in s_doc:
                    if token.lower_ in self.out_dialog_token:
                        in_dialog = False
                    if token.tag_ == "\'\'":
                        in_dialog = not in_dialog
                        # if last_token_text in self.end_token:
                        #     in_dialog = False
                    last_token_text = token.text

                    if self.print_log:
                        if in_dialog:
                            print("d: ", end="")
                    if len(s_people) > s_people_idx:
                        if token_loc >= s_people[s_people_idx][1]:
                            person_name = s_people[s_people_idx][0]
                            self.add_person(person_name)
                            s_people_idx += 1

                    if self.print_log:
                        print(token.text, token.tag_, token_loc)
                    fout.write(token.text)
                    if not in_dialog:
                        if token.tag_ == "PRP":
                            # print("FIND PRP")
                            fout.write("|||")
                            # if not self.current_people.empty():
                            #     fout.write(self.current_people.get())
                            #     fout.write("|||")

                            if token.lower_ in self.third_people_token:
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
                            elif token.lower_ in self.third_person_token:
                                if not self.current_person == "":
                                    fout.write(self.current_person)
                                    fout.write("|||")
                                else:
                                    fout.write("UNKNOWN_NAME|||")
                            elif token.lower_ in self.first_pron_token:
                                # TODO: check whether "I" is in a dialog, process first pron
                                fout.write("I_OUTSIDE_DIALOG")
                                fout.write("|||")
                            elif token.lower_ in self.second_pron_token:
                                # TODO: check whether "you" is in a dialog, process second pron
                                fout.write("YOU_OUTSIDE_DIALOG")
                                fout.write("|||")
                        fout.write(" ")
                    else:
                        # TODO: Dialog check
                        fout.write("[D]")
                        fout.write(" ")

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
    # filename = "test.txt"
    # filename = "HP1.txt"
    filename = "Cpart.txt"
    pron_replacer = NovelAnalyzer(filename)
    pron_replacer.read_file()
    pron_replacer.output_origin_sentences("sentences.txt")
    pron_replacer.extract_impt_sentences("pron")
    # pron_replacer.replace_pronoun()

