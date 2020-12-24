file = open("sentencesINA.txt","r")
file_lines = file.readlines()
file.close()

good_sentences = set([])
sentences = set([])
count = 0

for line in file_lines:
    first_split = line.find("|| (('")

    sentence = line[0:first_split]
    split = line[first_split+3:].split("||")

    label = split[0]
    type = split[1]
    website = split[2]

    first = label.find("'")
    second = label.find("'",first+1)

    language = label[first:second+1]

    first = label.find("[")
    second = label.find("]")

    value = label[first+1:second]

    if float(value) >= 0:
        if sentence not in sentences:
            good_sentences.add(line)
            sentences.add(sentence)
        else:
            count = count + 1

print("Sentences deleated:", count)
print("Unique Sentences:", len(good_sentences))

file = open("sentencesINA.txt","w")
file.writelines(good_sentences)
