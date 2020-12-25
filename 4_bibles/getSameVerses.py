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
            
            first_colon = line.find(":")
            if first_colon != -1 and line[first_colon-1].isdigit() and line[first_colon+1].isdigit:
                start = first_colon - 1
                while start >= 0:
                    if not line[start].isdigit():
                        break
                    start = start - 1
                start = start + 1

                end = first_colon + 1
                while end < len(line):
                    if not line[end].isdigit():
                        break
                    end = end + 1

                verse_number_one = line[start:end]
        elif j == 1:
            pair += line + "\n"
            second = len(line)
            
            first_colon = line.find(":")
            if first_colon != -1 and line[first_colon-1].isdigit() and line[first_colon+1].isdigit:
                start = first_colon - 1
                while start >= 0:
                    if not line[start].isdigit():
                        break
                    start = start - 1
                start = start + 1

                end = first_colon + 1
                while end < len(line):
                    if not line[end].isdigit():
                        break
                    end = end + 1

                verse_number_two = line[start:end]
        else:
            pair += "\n"
        i = i + 1
        
    if (verse_number_one != verse_number_two) or (pair.find(":")==-1):
        stop = 1
    if first > 1.5*second or second > 1.5*first:
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
file = open("4_books_verse_number_QC.txt","w")
file.writelines(pairs)