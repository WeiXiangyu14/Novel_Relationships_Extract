import sys
import spacy
import pickle
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
    output_dialog = True
    output_twopron_only = False

    end_token = [".", "!", "?"]
    out_dialog_token = ["said"]
    first_pron_token = ["i", "me", "we", "us"]
    second_pron_token = ["you"]
    third_people_token = ["they", "them"]
    third_person_token = ["he", "she", "him", "her"]

    relation_context = {"parent_child": ["child", "children", "son", "daughter"],
                        "father_child": ["father", "dad"],
                        "mother_child": ["mother", "mom"],
                        "grantparent_child": ["grandfather", "grandmother", "grandparents"],
                        "brothers": ["brother", "brothers"],
                        "sisters": ["sister", "sisters"],
                        "classmates": ["classmate", "classmates"],
                        "friends": ["friend", "friends"],
                        "co-workers": ["work with", "worked with", "works with", "working with"],
                        "teacher_student": ["teach", "taught", "teaching", "learn", "learnt", "learned"],
                        "couple": [""]
                        }

    relation_verb = ["have", "had", "has"]
    relation_attr = ["named", "called", "of"]

    relations = {}

    character_names = []

    def __init__(self, filename):
        self.filename = filename
        self.nlp = spacy.load("en_core_web_sm")
        for i in range(self.MAX_PEOPLE_NUM):
            self.current_people.append("")
        for k in self.relation_context:
            self.dict_add(self.relations, k, {})

    def dict_add(self, dict, term, default_value):
        if term in dict:
            if isinstance(dict[term], int):
                dict[term] += 1
        else:
            dict.update({term: default_value})
        return dict


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
                s_pron_num = self.calc_people_entity_num(s_doc)


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


                    if not in_dialog:
                        if self.output_twopron_only:
                            if s_pron_num >= 2:
                                fout.write(token.text)
                        else:
                            fout.write(token.text)
                        if token.tag_ == "PRP":
                            # print("FIND PRP")
                            if self.output_twopron_only:
                                if s_pron_num >= 2:
                                    fout.write("|||")
                            else:
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
                                    if self.output_twopron_only:
                                        if s_pron_num >= 2:
                                            fout.write(allpeople)
                                            fout.write("|||")
                                    else:
                                        fout.write(allpeople)
                                        fout.write("|||")
                                    # fout.write(allpeople)
                                    # fout.write("|||")
                                else:
                                    if self.output_twopron_only:
                                        if s_pron_num >= 2:
                                            fout.write("UNKNOWN_PEOPLE_NAMES|||")
                                    else:
                                        fout.write("UNKNOWN_PEOPLE_NAMES|||")
                            elif token.lower_ in self.third_person_token:
                                if not self.current_person == "":
                                    if self.output_twopron_only:
                                        if s_pron_num >= 2:
                                            fout.write(self.current_person)
                                            fout.write("|||")
                                    else:
                                        fout.write(self.current_person)
                                        fout.write("|||")
                                else:
                                    if self.output_twopron_only:
                                        if s_pron_num >= 2:
                                            fout.write("UNKNOWN_NAME|||")
                                    else:
                                        fout.write("UNKNOWN_NAME|||")
                            elif token.lower_ in self.first_pron_token:
                                # TODO: check whether "I" is in a dialog, handle first pron
                                if self.output_twopron_only:
                                    if s_pron_num >= 2:
                                        fout.write("I_OUTSIDE_DIALOG")
                                        fout.write("|||")
                                else:
                                    fout.write("I_OUTSIDE_DIALOG")
                                    fout.write("|||")
                            elif token.lower_ in self.second_pron_token:
                                # TODO: check whether "you" is in a dialog, handle second pron
                                if self.output_twopron_only:
                                    if s_pron_num >= 2:
                                        fout.write("YOU_OUTSIDE_DIALOG")
                                        fout.write("|||")
                                else:
                                    fout.write("YOU_OUTSIDE_DIALOG")
                                    fout.write("|||")
                            else:
                                # TODO: check "it", decide whether replace
                                if self.print_log:
                                    print("Other pron: ", end="")
                                    print(token.text)
                                if self.output_twopron_only:
                                    if s_pron_num >= 2:
                                        fout.write("OTHER_PRON")
                                        fout.write("|||")
                                else:
                                    fout.write("OTHER_PRON")
                                    fout.write("|||")

                        if self.output_twopron_only:
                            if s_pron_num >= 2:
                                fout.write(" ")
                        else:
                            fout.write(" ")
                    else:
                        # TODO: Dialog processing
                        if self.output_dialog:
                            fout.write(token.text)
                            fout.write("[D]")
                            fout.write(" ")

                    token_loc += len(token.text)
                    token_loc += 1
                if self.output_dialog:
                    if self.output_twopron_only:
                        if s_pron_num >= 2:
                            fout.write("\n\n")
                    else:
                        fout.write("\n\n")
                else:
                    if not in_dialog:
                        if self.output_twopron_only:
                            if s_pron_num >= 2:
                                fout.write("\n\n")
                        else:
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

    def calc_people_entity_num(self, s_doc):
        res = 0
        for token in s_doc:
            if token.tag_ == "PRP":
                if token.lower_ in self.third_people_token or token.lower_ in self.third_person_token:
                    res += 1

        s_ents = s_doc.ents
        s_people = []
        for e in s_ents:
            if e.label_ == "PERSON":
                if e.text not in s_people:
                    s_people.append(e.text)
        res += len(s_people)

        return res

    def replace_pronoun(self):
        i = 1

    def get_name_list(self, namesfile):
        f = open(namesfile, "r")
        for line in f.readlines():
            self.character_names.append(line.strip().lower())
        f.close()
        self.character_names = list(set(self.character_names))


    def get_twopeople_relations(self):
        for s in self.sentences_origin:
            s_doc = s.as_doc()
            s_ents = s_doc.ents

            s_people = []
            for e in s_ents:
                if e.label_ == "PERSON":
                    if e.text not in s_people:
                        s_people.append(e.text.lower())

            useful_people = []
            for p in s_people:
                if p in self.character_names:
                    if p not in useful_people:
                        useful_people.append(p)

            if len(useful_people) < 2:
                continue

            s_text = s_doc.text.lower()
            people_index = {}
            for p in useful_people:
                ind = s_text.find(p)
                if ind < 0:
                    continue
                people_index.update({ind: p})

            print(people_index)

            people_indexlist = [[k, people_index[k]] for k in sorted(people_index.keys())]

            print(people_indexlist)
            print(s_text)

            if len(people_indexlist) > 1:
                for i in range(len(people_indexlist)-1):
                    context_text = s_text[people_indexlist[i][0], people_indexlist[i+1][0]]
                    for r in self.relation_context:
                        rc = self.relation_context[r]
                        for c in rc:
                            if context_text.find(c) != -1:
                                self.relations[r].append((people_indexlist[i][1], people_indexlist[i+1][1]))
                                break

        print(self.relations)

    def get_twopeople_times(self):
        times = {}
        for p1 in self.character_names:
            p1dic = {}
            for p2 in self.character_names:
                if p1 != p2:
                    p1dic.update({p2: 0})
            times.update({p1: p1dic})

        for s in self.sentences_origin:
            s_doc = s.as_doc()
            s_ents = s_doc.ents


            s_people = []
            for e in s_ents:
                if e.label_ == "PERSON":
                    if e.text not in s_people:
                        s_people.append(e.text.lower())

            useful_people = []
            for p in s_people:
                if p in self.character_names:
                    useful_people.append(p)

            if len(useful_people) < 2:
                continue

            for p1 in useful_people:
                for p2 in useful_people:
                    if p1 != p2:
                        times[p1][p2] += 1

        for k in times:
            print(k, end = " ")
            print(times[k])

        file_two_names_dict = open("two_names_dict", "wb")
        pickle.dump(times, file_two_names_dict)

        return times


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
    filename = "HP1_ref_replaced.txt"
    # filename = "Cpart.txt"
    pron_replacer = NovelAnalyzer(filename)
    pron_replacer.read_file()
    pron_replacer.get_name_list("names.txt")

    # pron_replacer.get_twopeople_times()
    pron_replacer.get_twopeople_relations()

    # pron_replacer.output_origin_sentences("sentences.txt")
    # pron_replacer.extract_impt_sentences("pron")
    # pron_replacer.replace_pronoun()

