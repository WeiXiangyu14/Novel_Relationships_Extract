import spacy
import neuralcoref
from sympy import *

nlp = spacy.load("en_core_web_sm")
neuralcoref.add_to_pipe(nlp)
print("load successful")

f = open("PrideAndPrejudice.txt", "r")
fout = open("PAP_ref_replaced.txt", "w")

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
            doc = nlp(text)
            fout.write(doc._.coref_resolved)
            fout.write("\n")
            text = ""
            continue

    text += line


# doc = nlp(text)



# fout.write(doc._.coref_resolved)
fout.close()
f.close()