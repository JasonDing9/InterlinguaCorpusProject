import os
import fasttext

baseDir = os.getcwd()

os.chdir(baseDir + "/4_books_parallel_sentences")

file = open("4_books_everything.txt","r")
file_lines = file.readlines()
file.close()

pairs = set([])
i=0
stop_count = 0
duplicate_count = 0
good_count = 0
while i < len(file_lines):
    pair = ""
    if len(file_lines) - i < 2:
        break
        
    stop = 0
    for j in range(3):
        line=file_lines[i].replace("\n","")
        if j == 0:
            pair += line + "\n"
            first = len(line)
        elif j == 1:
            pair += line + "\n"
            second = len(line)
        else:
            pair += "\n"
        i = i + 1
        
    if first > 1.7*second or second > 1.7*first:
        stop = 1
    
    if stop == 0:
        if pair in pairs:
            duplicate_count = duplicate_count + 1
        else:
            pairs.add(pair)
            good_count = good_count + 1
    else:
        stop_count = stop_count + 1
        
print(duplicate_count)
print(len(pairs))
print("Stop:", stop_count)

os.chdir(baseDir)
file = open("4_books_everything_removed.txt","w")
file.writelines(pairs)