from langdetect import detect
from langdetect import detect_langs
import sys
import fasttext

model = fasttext.load_model("lid.176.bin")

file = open("INASetnecesLangDetect.txt","r")
file_lines = file.readlines()
file.close()
good_sentences = set([])
sentences = set([])
count = 0
big_sen_count = 0
good_sen_count = 0 
good_value_count = 0
error = 0

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
        lang = model.predict(sentence).__str__()

        result = line.replace("\n", "") + "||" + lang + "\n"
        
        good_sentences.add(result)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        e = sys.exc_info()[0]
        print( "Error:", repr(e) + str(exc_type) + ": " + str(exc_value) + "\n")
        
        error = error + 1


file = open("INASetnecesLangDetectWith176Lang.txt","w")
file.writelines(good_sentences)
