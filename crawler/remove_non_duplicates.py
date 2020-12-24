file = open("sentencesNonINA.txt","r")
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
    
#     if line != "Simone Bolelli Create a head to head matchup WTA Agnes Szavay Agnieszka Radwanska Ajla Tomljanovic Akgul Amanmuradova Alberta Brianti Aleksandra Krunic Aleksandra Wozniak Alexa Glatch Alexandra Dulgheru Alexandra Panova Alicia Molik Alisa Kleybanova Alison Riske Alison van Uytvanck Alize Cornet Alla Kudryavtseva Alona Bondarenko Ana Ivanovic Ana Konjuh Anabel Medina Garrigues Anastasia Pavlyuchenkova Anastasia Rodionova Anastasija Sevastova Anastasiya Yakimova Andrea Hlavackova Andrea Petkovic Andreea Mitu Angela Haynes Angelique Kerber Anna Tatishvili Anna Karolina Schmiedlova Anna-Lena Groenefeld Arantxa Parra Santonja Arantxa Rus Aravane Rezai Ashley Harkleroad Ayumi Morita Barbora Strycova Belinda Bencic Bethanie Mattek-Sands Bojana Jovanovski Carina Witthoeft Carla Suarez Navarro Caroline Wozniacki Casey Dellacqua Chanelle Scheepers Christina McHale CoCo Vandeweghe Daniela Hantuchova Danka Kovinic Daria Gavrilova Denisa Allertova Dinara Safina Dominika Cibulkova Edina Gallovits-Hall Ekaterina Makarova Elena Vesnina Eleni Daniilidou Eva Birnerova Evgeniya Rodina Flavia Penne|| website || https://www.tennis.com/players/498/jarmila-gajdosova/vs/635/yanina-wickmayer/\n":
#         good_sentences.add(line)
#     else:
#         print("Found ya!")
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
        if len(sentence) <= 700:
            big_sen_count = big_sen_count + 1

        if float(value) >= 0.9:
            good_value_count = good_value_count + 1

        if float(value) >= 0.9 and len(sentence) <= 400:
            good_sen_count = good_sen_count + 1

        if float(value) >= 0.7 and len(sentence) <= 800:
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

file = open("sentencesNonINA.txt","w")
file.writelines(good_sentences)
