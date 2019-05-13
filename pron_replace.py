import sys
import spacy
import pickle
import neuralcoref
from gender_predictor import GenderPredictor
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

    gender_predict = None

    end_token = [".", "!", "?"]
    punctuation = [".", ",", "!", "?", ";"]
    out_dialog_token = ["said", "whispered", "continued", "cried", "replied", "added", "squealed"]
    first_pron_token = ["i", "me", "we", "us"]
    second_pron_token = ["you"]
    third_people_token = ["they", "them"]
    third_person_token = ["he", "she", "him", "her"]

    relation_context = {"child": ["son", "daughter"],
                        "father": ["father", "dad", "papa"],
                        "mother": ["mother", "mom", "mama"],
                        "grantparent": ["grandfather", "grandmother", "grandparents"],
                        "brothers": ["brother", "brothers"],
                        "sisters": ["sister", "sisters"],
                        "classmates": ["classmate", "classmates"],
                        "friends": ["friend", "friends"],
                        "co-workers": ["work with", "worked with", "works with", "working with"],
                        "teacher": ["teach", "taught", "teaching", "learn", "learnt", "learned"],
                        "lover": ["fall in love with", "fell in love with", "fallen in love with"],
                        "wife": ["wife"],
                        "husband": ["husband"]
                        }

    relation_verb = ["have", "had", "has"]
    relation_attr = ["named", "called", "of"]

    relations = {}

    character_dict = {}

    character_names = []

    def __init__(self, filename):
        self.filename = filename
        self.nlp = spacy.load("en_core_web_sm")
        for i in range(self.MAX_PEOPLE_NUM):
            self.current_people.append("")
        for k in self.relation_context:
            self.dict_add(self.relations, k, [])

        self.gender_predict = GenderPredictor()
        self.gender_predict.train_and_test()

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
                                if self.output_twopron_only:
                                    if s_pron_num >= 2:
                                        fout.write("I_OUTSIDE_DIALOG")
                                        fout.write("|||")
                                else:
                                    fout.write("I_OUTSIDE_DIALOG")
                                    fout.write("|||")
                            elif token.lower_ in self.second_pron_token:
                                if self.output_twopron_only:
                                    if s_pron_num >= 2:
                                        fout.write("YOU_OUTSIDE_DIALOG")
                                        fout.write("|||")
                                else:
                                    fout.write("YOU_OUTSIDE_DIALOG")
                                    fout.write("|||")
                            else:
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

    def replace_pron(self, foutname):
        f = open(self.filename, "r").read()
        neuralcoref.add_to_pipe(self.nlp)
        fout = open(foutname, "w")

        text = ""
        chapter_name = ""
        for line in f.readlines():
            words = line.split()
            if len(words) < 3 and len(words) > 0:
                if words[0].lower() == "chapter":
                    if chapter_name != "":
                        fout.write(chapter_name)
                        print(chapter_name)
                    chapter_name = line
                    doc = self.nlp(text)
                    fout.write(doc._.coref_resolved)
                    fout.write("\n")
                    text = ""
                    continue
            text += line
        f.close()
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

    def get_name_list(self, namesfile):
        f = open(namesfile, "r")
        for line in f.readlines():
            self.character_names.append(line.strip().lower())
        f.close()
        self.character_names = list(set(self.character_names))

    def get_dict(self, dictfile):
        f = open(dictfile, "r")
        for line in f.readlines():
            words = line.split(":")
            key = words[0]
            vs = words[1]
            vs = vs.split(",")
            rvs = []
            for v in vs:
                rvs.append(v.strip())
            self.character_dict.update({key: rvs})
        print(self.character_dict)
        f.close()

    def get_twopeople_relations(self):
        for s in self.sentences_origin:

            s_doc = s.as_doc()
            s_ents = s_doc.ents

            print(s_doc.text)
            print(s_ents)

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

            people_indexlist = [[k, people_index[k]] for k in sorted(people_index.keys())]

            # print(s_people)
            # print(people_index)
            # print(people_indexlist)
            # print(s_text)

            if len(people_indexlist) > 1:
                for i in range(len(people_indexlist)-1):
                    context_text = s_text[people_indexlist[i][0]: people_indexlist[i+1][0]]
                    context_text = context_text.replace(",", " ")
                    context_words = context_text.split()
                    for r in self.relation_context:
                        rc = self.relation_context[r]
                        for c in rc:
                            # c_words = c.split()
                            if c in context_words:
                                self.dict_add(self.relations[r], (people_indexlist[i][1], people_indexlist[i+1][1]), 0)
                                print(r)
                                print(people_indexlist)
                                print(s_text)

                                # self.relations[r].append((people_indexlist[i][1], people_indexlist[i+1][1]))
        print(self.relations)

    def find_in_dict(self, name):
        name = name.lower().strip()
        for n in self.character_dict:
            for n2 in self.character_dict[n]:
                if name == n2.lower().strip():
                    return n

    def get_twopeople_times(self):
        times = {}
        # for p1 in self.character_names:
        #     p1dic = {}
        #     for p2 in self.character_names:
        #         if p1 != p2:
        #             p1dic.update({p2: 0})
        #     times.update({p1: p1dic})

        for s in self.sentences_origin:
            s_doc = s.as_doc()
            s_ents = s_doc.ents

            s_t = s.text
            words = s_t.split()

            s_people = []
            for e in s_ents:
                if e.label_ == "PERSON":
                    if e.text not in s_people:
                        s_people.append(e.text.lower())

            # print(s_people)
            for p1 in s_people:
                i1 = -1
                for i in len(words):
                    if words[i].lower() == p1:
                        i1 = i
                for p2 in s_people:
                    if p1 != p2:
                        i2 = -1
                        for i in len(words):
                            if words[i].lower() == p2:
                                i2 = i
                        for i in range(i1-4, i2+4):
                            if i < 0:
                                continue
                            if i > len(words)-1:
                                break
                            if words[i].lower() in self.relation_context:
                                self.relations[words[i].lower()].append((p1, p2))


            useful_people = []
            temp_people = []
            for p in s_people:
                if p in self.character_names:
                    useful_people.append(p)
                    temp_people.append(p)



            if len(words) > 0:
                for p in temp_people:
                    for i in range(1, len(words)):
                        if words[i].lower() == p:
                            if words[i-1][0:2].lower() == "mr":
                                useful_people.append(words[i-1].lower() + " " +p)

            useful_people = list(set(useful_people))



            if len(useful_people) < 2:
                continue

            for p1 in useful_people:
                if p1 not in times:
                    times.update({p1:{}})
                for p2 in useful_people:
                    if p2 not in times[p1]:
                        times[p1].update({p2: 0})
                    if p1 != p2:
                        times[p1][p2] += 1

        # for k in times:
        #     print(k, end = " ")
        #     print(times[k])

        clean_times = {}

        for k in times:
            k_dictname = self.find_in_dict(k)
            if k_dictname not in clean_times:
                clean_times.update({k_dictname:{}})
            for n in times[k]:
                n_dictname = self.find_in_dict(n)
                if n_dictname not in clean_times[k_dictname]:
                    clean_times[k_dictname].update({n_dictname: 0})
                clean_times[k_dictname][n_dictname] += times[k][n]

        for ct in clean_times:
            print(clean_times[ct])

        file_two_names_dict = open("two_names_dict_hp", "wb")
        pickle.dump(clean_times, file_two_names_dict)

        return times


    def extract_tokens(self, sentence, word_mode):
        res_tokens = []
        if word_mode == "pron":
            sentence_doc = sentence.doc
            for w in sentence_doc:
                if w.tag_ == "NNP":
                    res_tokens.append(w)
        return res_tokens

    def detect_vocative(self, str):
        res = ""
        tempstr = str
        tempstr = tempstr.replace("Mrs. ", "Mrs")
        tempstr = tempstr.replace("Mr. ", "Mr")

        for p in self.punctuation:
            tempstr = tempstr.replace(p, " " + p)

        words = tempstr.split()
        potential_vocative = ""
        last_punc = ""
        for w in words:
            if w in self.punctuation:
                if last_punc == "," or w == ",":
                    potential_vocative = potential_vocative.replace("my dear", "")
                    potential_vocative = potential_vocative.replace("My dear", "")
                    potential_vocative = potential_vocative.replace("Dear", "")
                    potential_vocative = potential_vocative.replace("dear", "")
                    potential_vocative = potential_vocative.strip()
                    p_v = potential_vocative.split()
                    if len(p_v) == 1:
                        res = p_v[0]
                potential_vocative = ""
                last_punc = w
            else:
                potential_vocative += w
                potential_vocative += " "

        return res

    def analyze_utterances(self):
        f = open(self.filename, "r")
        curr_utterance = ""

        curr_dialog = {"uttr": "", "sp": "", "ls": ""}
        all_dialogs = []

        all_dialogs.append(curr_dialog)

        word = ""
        last_word = ""
        in_dialog = False

        last_punc = ""

        continue_speaking = False

        name_near_outtoken = []


        text = f.read()
        text = text.replace("\n", " ")
        text = text.replace("\r", " ")

        for c in text:

            if c == "\"":
                in_dialog = not in_dialog
                if in_dialog:
                    if len(curr_utterance) > 0:
                        curr_dialog = {"uttr": "", "sp": "", "ls": ""}
                        listener = self.detect_vocative(curr_utterance)
                        t_ls = listener.lower()
                        if t_ls[0:3] == "mrs":
                            t_ls = t_ls[3:]
                        elif t_ls[0:2] == "mr":
                            t_ls = t_ls[2:]
                        if t_ls not in self.character_names:
                            listener = ""

                        # print(name_near_outtoken)
                        for potential_name in name_near_outtoken:
                            real_name = potential_name.lower()
                            if real_name[0:3] == "mrs":
                                real_name = real_name[3:]
                            elif real_name[0:2] == "mr":
                                real_name = real_name[2:]

                            if real_name in self.character_names:
                                curr_dialog["sp"] = potential_name
                        name_near_outtoken = []

                        if not continue_speaking:
                            if curr_dialog["sp"] == "":
                                curr_dialog["sp"] = all_dialogs[-1]["ls"]

                            if listener == "":
                                curr_dialog["ls"] = all_dialogs[-1]["sp"]
                            else:
                                curr_dialog["ls"] = listener
                                listener = ""
                        else:
                            curr_dialog["sp"] = all_dialogs[-1]["sp"]
                            if listener == "":
                                curr_dialog["ls"] = all_dialogs[-1]["ls"]
                            else:
                                curr_dialog["ls"] = listener
                                listener = ""

                        curr_dialog["uttr"] = curr_utterance

                        all_dialogs.append(curr_dialog)

                        curr_utterance = ""

                    if last_punc == "," or last_punc == ";":
                        continue_speaking = True
                    else:
                        continue_speaking = False

                else:
                    # print(last_word)
                    last_word = ""
                    # name_near_outtoken = []
                continue

            if in_dialog:
                curr_utterance += c


            if c != ' ' and c not in self.punctuation:
                word = word + c
            else:
                if last_word.lower() == "chapter":
                    if word.isdigit():
                        if len(curr_utterance) > 0:
                            curr_dialog = {"uttr": "", "sp": "", "ls": ""}
                            listener = self.detect_vocative(curr_utterance)
                            t_ls = listener.lower()
                            if t_ls[0:3] == "mrs":
                                t_ls = t_ls[3:]
                            elif t_ls[0:2] == "mr":
                                t_ls = t_ls[2:]
                            if t_ls not in self.character_names:
                                listener = ""


                            for potential_name in name_near_outtoken:
                                real_name = potential_name.lower()
                                if real_name[0:3] == "mrs":
                                    real_name = real_name[3:]
                                elif real_name[0:2] == "mr":
                                    real_name = real_name[2:]

                                if real_name in self.character_names:
                                    curr_dialog["sp"] = potential_name
                            name_near_outtoken = []

                            if not continue_speaking:
                                if curr_dialog["sp"] == "":
                                    curr_dialog["sp"] = all_dialogs[-1]["ls"]

                                if listener == "":
                                    curr_dialog["ls"] = all_dialogs[-1]["sp"]
                                else:
                                    curr_dialog["ls"] = listener
                                    listener = ""
                            else:
                                curr_dialog["sp"] = all_dialogs[-1]["sp"]
                                if listener == "":
                                    curr_dialog["ls"] = all_dialogs[-1]["ls"]
                                else:
                                    curr_dialog["ls"] = listener
                                    listener = ""

                            curr_dialog["uttr"] = curr_utterance
                            all_dialogs.append(curr_dialog)
                            blank_dialog = {"uttr": "", "sp": "", "ls": ""}
                            all_dialogs.append(blank_dialog)
                            curr_utterance = ""

                if c in self.punctuation:
                    last_punc = c

                if word.lower() == "mr" or word.lower() == "mrs":
                    continue
                else:
                    # if last_honor != "":
                    #     # print(word)
                    #     # word = last_honor + "." + word
                    #     last_honor = ""

                    if len(word) > 0:

                        if word.lower() in self.out_dialog_token:
                            name_near_outtoken.append(last_word)
                            # in_dialog = False
                        if last_word.lower() in self.out_dialog_token:
                            name_near_outtoken.append(word)


                        last_word = word
                        word = ""



        # for d in all_dialogs:
        #     print(d)
        #     print(self.detect_vocative(d["uttr"]))

        # for d in all_dialogs:
        #     for k in self.relation_context:
        #         for rc in self.relation_context[k]:
        #             if d["uttr"].find(rc) != -1:
        #                 print(k)
        #                 print(d)


        all_dialogs_file = open("utters", "wb")
        pickle.dump(all_dialogs, all_dialogs_file)

    def check_gender(self, name):
        name = name.lower()
        res = -1
        if name[0:3] == "mrs":
            res = 0
        elif name[0:2] == "mr":
            res = 1
        else:
            r = self.gender_predict.classify(name)
            if r == "F":
                return 0
            elif r == "M":
                return 1
        return res


    def extract_real_relations(self, uttersfile):
        all_dialogs_file = open("utters", "rb")
        dialogs = pickle.load(all_dialogs_file)

        for d in dialogs:
            if len(d["ls"]) > 0 and len(d["sp"]) > 0:
                vod = self.detect_vocative(d["uttr"])
                for r in self.relation_context:
                    for rc in self.relation_context[r]:
                        if rc in vod:
                            self.relations[r].append((d["ls"].lower(), d["sp"].lower()))

        templist = self.relations["father"][:]
        for fr in templist:
            f, c = fr
            if self.check_gender(f) != 1:
                self.relations["father"].remove(fr)
        templist = self.relations["mother"][:]
        for fr in templist:
            f, c = fr
            if self.check_gender(f) != 0:
                self.relations["mother"].remove(fr)
        templist = self.relations["brothers"][:]
        for fr in templist:
            f, c = fr
            if self.check_gender(f) != 1:
                self.relations["brothers"].remove(fr)

        mrlist = []
        mrslist = []
        for d in self.character_dict:
            if d.find("._") != -1:
                tempd = d.replace("._", "").lower()
                if tempd[0:3] == "mrs":
                    mrslist.append(tempd[3:])
                elif tempd[0:2] == "mr":
                    mrlist.append(tempd[2:])

        implist = []
        for r in self.relations:
            for (f, s) in self.relations[r]:
                if f[0:3] == "mrs":
                    if f[3:] in mrslist:
                        implist.append(f[3:])
                elif f[0:2] == "mr":
                    if f[2:] in mrlist:
                        implist.append(f[2:])
                if s[0:3] == "mrs":
                    if s[3:] in mrslist:
                        implist.append(s[3:])
                elif s[0:2] == "mr":
                    if s[2:] in mrlist:
                        implist.append(s[2:])

        implist = list(set(implist))

        print(implist)
        print(mrlist)
        print(mrslist)
        for n in implist:
            if n in mrslist and n in mrlist:
                self.relations["wife"].append(("mrs"+n, "mr"+n))
                self.relations["husband"].append(("mr" + n, "mrs" + n))

        child_list = ["sisters", "brothers"]
        parent_list = ["mother", "father"]
        for r in child_list:
            templist = self.relations[r][:]
            for i in range(len(templist)):
                for j in range(1, len(templist)):
                    f1, c1 = templist[i]
                    f2, c2 = templist[j]
                    if f1 == c1:
                        if f2 != c2:
                            if (f2, c2) not in self.relations[r]:
                                self.relations[r].append((f2, c2))
                    elif f1 == c2:
                        if f2 != c1:
                            if (f2, c1) not in self.relations[r]:
                                self.relations[r].append((f2, c1))

                    elif f2 == c2:
                        if f1 != c1:
                            if (f1, c1) not in self.relations[r]:
                                self.relations[r].append((f1, c1))

                    elif f2 == c1:
                        if f1 != c2:
                            if (f1, c2) not in self.relations[r]:
                                self.relations[r].append((f1, c2))

        for r in parent_list:
            templist = self.relations[r][:]
            for i in range(len(templist)):
                f, c = templist[i]
                for r2 in child_list:
                    for (c1, c2) in self.relations[r2]:
                        if c == c2:
                            self.relations[r].append((f, c1))
                        elif c == c1:
                            self.relations[r].append((f, c2))

        for (m, c) in self.relations["mother"]:
            f = ""
            for (f1, f2) in self.relations["wife"]:
                if f1 == m:
                    f = f2
            if f != "":
                if (f, c) not in self.relations["father"]:
                    self.relations["father"].append((f, c))

        for (m, c) in self.relations["father"]:
            f = ""
            for (f1, f2) in self.relations["husband"]:
                if f1 == m:
                    f = f2
            if f != "":
                if (f, c) not in self.relations["mother"]:
                    self.relations["mother"].append((f, c))

        for r in self.relations:
            print(r)
            print(self.relations[r])

        file_relation = open("relation_pap", "wb")
        pickle.dump(self.relations, file_relation)


if __name__ == '__main__':
    # filename = sys.argv[1]
    # filename = "test.txt"
    filename = "PAP_ref_replaced.txt"
    # filename = "HP1_dic_replaced.txt"
    # filename = "testfile.txt"
    # filename = "Cpart.txt"

    pron_replacer = NovelAnalyzer(filename)
    pron_replacer.read_file()
    pron_replacer.get_name_list("name_pride.txt")
    pron_replacer.get_dict("dict_pride(1).txt")
    pron_replacer.get_twopeople_times()

    # pron_replacer.get_twopeople_relations()

    # pron_replacer.output_origin_sentences("sentences.txt")
    # pron_replacer.extract_impt_sentences("pron")
    # pron_replacer.replace_pronoun()

    # filename = "PrideAndPrejudice.txt"
    # analyze_utterance = NovelAnalyzer(filename)
    # # analyze_utterance.read_file()
    # analyze_utterance.get_name_list("name_pride.txt")
    # analyze_utterance.get_dict("dict_pride.txt")
    # # analyze_utterance.analyze_utterances()
    # analyze_utterance.extract_real_relations("utters")



