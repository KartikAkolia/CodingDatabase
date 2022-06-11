import os

directory = os.fsencode("/dev/pts")

l=[]

for file in os.listdir(directory):
    filename = os.fsdecode(file)
    l.append(filename)

print(l)
