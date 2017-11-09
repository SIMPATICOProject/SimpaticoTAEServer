f1 = open("t1", "r").read().split("\n")
f2 = open("t2", "r").read().split("\n")
c = 0 
for i in range(0,len(f1)):
    if f1[i].split() != f2[i].split():
        c += 1

print c
