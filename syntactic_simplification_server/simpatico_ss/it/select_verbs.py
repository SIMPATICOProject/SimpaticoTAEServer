f = open("dicc.src.verbs", "r")

#for s in f.readlines():
#    tokens = s.split(" ")
#    tag = tokens[2]
#    if tag[0] == "V":
#        print s.strip()
lemmas = {}
for s in f.readlines():
    tokens = s.strip().split(" ")
    verb = tokens[0]
    for i in range(1,len(tokens)):
        if i % 2 != 0:
            if tokens[i] not in lemmas:
                lemmas[tokens[i]] = []
        else:
            lemmas[tokens[i-1]].append(verb+":"+tokens[i].lower())

for l in sorted(lemmas.keys()):
    print l + "\t" + "\t".join(lemmas[l])


