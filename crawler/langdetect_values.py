from langdetect import detect
from langdetect import detect_langs
import sys

file = open("INAGoodSentences.txt","r")
file_lines = file.readlines()
file.close()

good_sentences = set([])
sentences = set([])
count = 0
big_sen_count = 0
good_sen_count = 0 
good_value_count = 0
error = 0

languages = dict({})

length = len(file_lines)
report_count =0 
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
    
    report_count = report_count + 1
    if report_count % 500 == 0:
        print((report_count / length)*100, "%")
    
    try:
        lang = detect(sentence)
        if lang in languages:
            languages[lang] = languages[lang] + 1
        else:
            languages[lang] = 1
            
        langs = detect_langs(sentence)
        result = line.replace("\n", "") + " || " + str(langs) + " || " + str(lang) + "\n"
        
        good_sentences.add(result)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        e = sys.exc_info()[0]
        print( "Error:", repr(e) + str(exc_type) + ": " + str(exc_value) + "\n")
        
        error = error + 1

languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)
  
file = open("INASetnecesLangDetectDictionary.txt","w")
for key in languages:
    print(key[0] + ":", key[1])
    file.write(str(key[0]) + ": " + str(key[1]) + "\n")
    
file.close()


file = open("INASetnecesLangDetect.txt","w")
file.writelines(good_sentences)
