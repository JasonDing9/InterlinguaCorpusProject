file = open("sentencesINA.txt","r")
file_lines = file.readlines()
file.close()

good_sentences = set([])
sentences = set([])
count = 0
big_sen_count = 0
good_sen_count = 0 
good_value_count = 0
error = 0

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
    try:
        if len(sentence) <= 500:
            big_sen_count = big_sen_count + 1

        if float(value) >= 0.9:
            good_value_count = good_value_count + 1

        if float(value) >= 0.9 and len(sentence) <= 400:
            good_sen_count = good_sen_count + 1

        if float(value) >= 0.9 and len(sentence) <= 400:
            if sentence not in sentences:
                good_sentences.add(line)
                sentences.add(sentence)
            else:
                count = count + 1
        else:
            count = count + 1
    except:
        print(line)
        error = error + 1

print("Sentences deleated:", count)
print("Unique Sentences:", len(good_sentences))
print("Small Sentences:", big_sen_count)
print("Value Sentences:", good_value_count)
print("Good Sentences:", good_sen_count)
print("Error:", error)



file = open("INAGoodSentences.txt","w")
file.writelines(good_sentences)
