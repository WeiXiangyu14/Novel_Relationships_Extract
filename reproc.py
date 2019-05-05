character_names = []

f = open("names.txt", "r")
for line in f.readlines():
    character_names.append(line.strip().lower())
f.close()
character_names = list(set(character_names))

endtoken = [",", ".", "\"", "?", "!"]

f = open("HP1_ref_replaced.txt")

text = f.read()
for n in character_names:
    twoname = n + " " + n
    text = text.replace(twoname, n)
    for et in endtoken:
        etname = et + n
        text = text.replace(etname, " " + n)

f.close()

fout = open("new.txt", "w")
fout.write(text)
fout.close()
