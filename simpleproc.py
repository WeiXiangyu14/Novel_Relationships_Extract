def Cap(Name):
    words = Name.split()
    res = ""
    for w in words:
        res += w.capitalize()
    return res

f = open("HP1_ref_replaced.txt")

text = f.read()
words = text.split(" ")

new_text = ""
for w in words:
    new_text += w
    new_text += " "

fd = open("dict.txt", "r")
character_dict = {}
for line in fd.readlines():
    words = line.split(":")
    key = words[0]
    vs = words[1]
    vs = vs.split(",")
    for v in vs:
        character_dict.update({v.strip(): key})
print(character_dict)
fd.close()

for k in character_dict:
    new_text = new_text.replace(" " + k, " " + character_dict[k])
    new_text = new_text.replace(" " + Cap(k), " " + character_dict[k])


fout = open("HP1_ref_replaced_dict.txt", "w")
fout.write(new_text)

f.close()
fout.close()