import urllib.request
from urllib.request import urlopen, urlretrieve
import bs4 as bs
from bs4 import NavigableString, Tag
import sys
import time
import io, re
import fasttext
import pdfplumber
import requests
import PyPDF2
import fitz
import operator
import traceback
from collections import OrderedDict
import signal
import difflib

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

class TimeoutException(Exception):   # Custom exception class
    pass

def timeout_handler(signum, frame):   # Custom signal handler
    raise TimeoutException

def get_html(link_url):
    link_url=link_url.replace(" ", "%20")
    source = urlopen(link_url)
    return source


def get_soup(url):
    source = get_html(url)
    soup = bs.BeautifulSoup(source, 'lxml')
    return soup

def get_paragraphs(soup):
    texts = []
    newline = ["\r\n", "\r", "\n"]
    for p in soup.findAll('p'):
        text = ""
        for child in p:
            if isinstance(child, NavigableString):
                add = str(child)
                for line in newline:
                    add = add.replace(line, " ")
                text += add
            elif isinstance(child, Tag):
                if child.name != 'br':
                    add = child.text
                    for line in newline:
                        add = add.replace(line, " ")
                    text += add
                else:
                    text += '\n'

        result = text.strip().split('\n')
        for sen in result:
            texts.append(sen)

    for p in soup.findAll('span'):
        text = ""
        for child in p:
            if isinstance(child, NavigableString):
                add = str(child)
                for line in newline:
                    add = add.replace(line, " ")
                text += add
            elif isinstance(child, Tag):
                if child.name != 'br':
                    add = child.text
                    for line in newline:
                        add = add.replace(line, " ")
                    text += add
                else:
                    text += '\n'

        result = text.strip().split('\n')
        for sen in result:
            texts.append(sen)

    for p in soup.find_all('div'):
        text = ""
        for child in p:
            if isinstance(child, NavigableString):
                add = str(child)
                for line in newline:
                    add = add.replace(line, " ")
                text += add
            elif isinstance(child, Tag):
                if child.name != 'br':
                    add = child.text
                    for line in newline:
                        add = add.replace(line, " ")
                    text += add
                else:
                    text += '\n'

        result = text.strip().split('\n')
        for sen in result:
            texts.append(sen)
            
            
    return texts


def extract_sentences(fraction, texts):
    spaces = [" ", "\u00A0"]
    newline = ["\r\n", "\r", "\n"]
    punctuation = [".", "!", "?"]
    abbreviations = ["i.a.", "i. a.", "i.e.", "i. e.", "p.ex.", "p. ex.", "sr.", "sra.", "srta.", "a.i.", "a. i.",
                     "etc.", ".html", ".com", "...", "Dr.", "Mrs.", "Mr.", "Ms.", "pp."]
    websites = ["com", "org", "net", "int", "edu", "gov", "mil","rice", "onet", "se", "pl"]
    alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                "u", "v", "w", "x", "y", "z", "\"", "\'", "‘"]
    quotes = ["\"", "\'", "‘","’"]
    sentences = []
    for text in texts:
        split = text.split()
        if len(split) > 0 and split[0][-1] == ":":  # check if the first word ends with a ":"
            split.remove(split[0])

        text = " ".join(split)
        sentence_ends = [i for i, ltr in enumerate(text) if
                         ltr in punctuation]  # find period locations in sent.
        start = 0

        i = 0
        breakx = 0
        while i < len(sentence_ends):  # looking at all period locations
            interrupt = 0
            if len(sentence_ends) > 0 and sentence_ends[i] >= 3 and text[sentence_ends[i] - 3:sentence_ends[i]+1] == "www.":  # check if period is part of a link
                while True:
                    for webend in websites:
                        if sentence_ends[i] < len(text) - 1 - len(webend) and text[sentence_ends[i] + 1:sentence_ends[
                                                                                                        i] + 1 + len(webend)] == webend:
                            interrupt = 1
                            break
                        i = i + 1
                        if i == len(sentence_ends):
                            i = i-1
                            breakx = 1
                            break
                    if(interrupt == 1 or breakx == 1):
                        break

            if sentence_ends[i]+1<len(text) and text[sentence_ends[i]+1] not in quotes and text[sentence_ends[i]+1] != " ":
                                                                                   # if there is a character after the punctuation,
                                                                                   # it is most likely an abbreviation
                interrupt = 1

            if i + 1 < len(sentence_ends):                                                           # if there is only 1 or 2 words between punctuations
                if len(text[sentence_ends[i] + 1 : sentence_ends[i+1] + 1].split()) <= 2 or \
                                        sentence_ends[i+1] - sentence_ends[i] <= 5:                  # or less than 5 chars long
                                                                                                     # it is most likely not a sentence end.
                    interrupt = 1

            for abr in abbreviations:  # checking if the period is in an abbreviation and not a sentence end
                abr_periods = [i for i, ltr in enumerate(abr) if ltr == "."]
                for period_index in abr_periods:
                    if sentence_ends[i] - period_index >= 0 and \
                            sentence_ends[i] + len(abr) - period_index <= len(text) and \
                            text[(sentence_ends[i] - period_index):(
                                    sentence_ends[i] + len(abr) - period_index)].lower() == abr.lower():
                        interrupt = 1
                        break
                if interrupt == 1:
                    break

            if interrupt == 0:
                if text[start].isupper() or text[start].islower() or (text[start] in quotes):  # check if the first letter of the sentence upper case
                    if sentence_ends[i] + 1 < len(text) and \
                            (text[sentence_ends[i] + 1] in quotes):
                        sentences.append(text[start:sentence_ends[i] + 2])
                        sentence_start = 2
                    else:
                        sentences.append(text[start:sentence_ends[i] + 1])
                        sentence_start = 1
                else:
                    sentence_start = 1

                while True:
                    if sentence_ends[i] < len(text) - sentence_start and \
                            text[sentence_ends[
                                          i] + sentence_start].lower() in alphabet:  # check if the character next to the period a space
                        start = sentence_ends[i] + sentence_start
                        break
                    elif sentence_ends[i] >= len(text) - sentence_start:
                        break
                    else:
                        sentence_start = sentence_start + 1

            i = i + 1
    i = 0
    # while i < len(sentences):
    #     if len(sentences[i].split()) <= 2 and len(sentences[i]) <= 5:  # If a "sentence" has 2 or less words and less
    #                                                                    # than or equal to 5 chars, delete it
    #         sentences.remove(sentences[i])
    #         i = i - 1
    #     i = i + 1

    output = findAndSeperateLanguage(sentences, fraction, "__label__INA")
    # if(output[0]):
    #     return output[1], output[2]
    # else:
    #     return output[1], -1
    return output[1], output[2], output[0], sentences

def findLanguage(sentences, fraction, language_lable):
    count = 0
    for sentence in sentences:
        if model.predict(sentence)[0][0] == language_lable:
            count  = count + 1
    return len(sentences)*fraction + 1 <= count

def findAndSeperateLanguage(sentences, fraction, language_lable):
    count = 0
    INA = []
    nonINA = []
    for sentence in sentences:
        if model.predict(sentence)[0][0] == language_lable:
            count  = count + 1
            INA.append(sentence + " || " + model.predict(sentence).__str__())
        else:
            nonINA.append(sentence + " || " +  model.predict(sentence).__str__())
    return len(sentences)*fraction + 1 <= count, INA, nonINA

def get_links(soup, original_link):
    links = []
    for link in soup.findAll('a', href=True):
        text = link['href']
        if text.find("http")!=-1:
            links.append(text)
        else:
            if(get_link_root(original_link) != "-1"):
                links.append(get_link_root(original_link) + text)
    return links


def get_link_root(link):
    websites = ["com", "org", "net", "int", "edu", "gov", "mil"]
    for extension in websites:
        index = link.find(extension)
        if(index!=-1):
            return link[0:index+3] + "/"
    return "-1"


def load_vectors(fname):
    fin = io.open(fname, 'r', encoding='utf-8', newline='\n', errors='ignore')
    n, d = map(int, fin.readline().split())
    data = {}
    for line in fin:
        tokens = line.rstrip().split(' ')
        data[tokens[0]] = map(float, tokens[1:])
    return data


def checkForLanguage(lable, fraction, soup):
    print()
    print("Checking if page is " + lable)
    valid = 0
    count = 0
    total_count = 0
    for p in soup.findAll('p'):
        if model.predict(p.getText().replace("\n",""))[0][0] == lable:
            count = count + 1
        total_count = total_count + 1
    if total_count == 0:
        valid = valid + 0.5
    elif total_count * fraction <= count:
        valid = valid + 1
    print("paragraph", count, total_count)

    count = 0
    total_count = 0
    for a in soup.findAll('a'):
        if len(a.getText()) > 3:
            if model.predict(a.getText().replace("\n",""))[0][0] == lable:
                count = count + 1
            total_count = total_count + 1
    if total_count == 0:
        valid = valid + 0.5
    elif total_count * fraction <= count:
        valid = valid + 1
    print("anchor", count, total_count)

    count = 0
    total_count = 0
    for h in soup.find_all(re.compile('^h[1-6]$')):
        if model.predict(h.getText().replace("\n",""))[0][0] == lable:
            count = count + 1
        total_count = total_count + 1
    if total_count == 0:
        valid = valid + 0.5
    elif total_count * fraction <= count:
        valid = valid + 1
    print("heading", count, total_count)

    title = soup.find('title')
    try:
        if (model.predict(title.getText())[0][0] == lable and model.predict(title.getText())[1][0] >= 0.95):
            valid = valid + 1
            print("Title is INA")
        elif title.getText().lower().find("interlingua")!=-1:
            valid = valid + 1
            print("Title contains interlingua")

        elif title.getText().lower().find("wiki")!=-1 and \
                        model.predict(title.getText())[0][0] == lable and model.predict(title.getText())[1][0] >= 0.5:
            print("Title is wiki INA")
            valid = valid + 1
        else:
            print("Title:", model.predict(title.getText())[0][0], model.predict(title.getText())[1][0])
            print("Title not INA:", title.getText())
    except:
        pass



    print("Valid value (>=2):",  valid)
    print()

    if valid >= 2:
        return True
    else:
        return False


def fonts(doc, granularity=False):
    """Extracts fonts and their usage in PDF documents.
    :param doc: PDF document to iterate through
    :type doc: <class 'fitz.fitz.Document'>
    :param granularity: also use 'font', 'flags' and 'color' to discriminate text
    :type granularity: bool
    :rtype: [(font_size, count), (font_size, count}], dict
    :return: most used fonts sorted by count, font style information
    """
    styles = {}
    font_counts = {}

    for page in doc:
        blocks = page.getText("dict")["blocks"]
        for b in blocks:  # iterate through the text blocks
            if b['type'] == 0:  # block contains text
                for l in b["lines"]:  # iterate through the text lines
                    for s in l["spans"]:  # iterate through the text spans
                        if granularity:
                            identifier = "{0}_{1}_{2}_{3}".format(s['size'], s['flags'], s['font'], s['color'])
                            styles[identifier] = {'size': s['size'], 'flags': s['flags'], 'font': s['font'],
                                                  'color': s['color']}
                        else:
                            identifier = "{0}".format(s['size'])
                            styles[identifier] = {'size': s['size'], 'font': s['font']}

                        font_counts[identifier] = font_counts.get(identifier, 0) + 1  # count the fonts usage

    font_counts = sorted(font_counts.items(), key=operator.itemgetter(1), reverse=True)

    if len(font_counts) < 1:
        raise ValueError("Zero discriminating fonts found!")

    return font_counts, styles


def font_tags(font_counts, styles):
    """Returns dictionary with font sizes as keys and tags as value.
    :param font_counts: (font_size, count) for all fonts occuring in document
    :type font_counts: list
    :param styles: all styles found in the document
    :type styles: dict
    :rtype: dict
    :return: all element tags based on font-sizes
    """
    p_style = styles[font_counts[0][0]]  # get style for most used font by count (paragraph)
    p_size = p_style['size']  # get the paragraph's size

    # sorting the font sizes high to low, so that we can append the right integer to each tag
    font_sizes = []
    for (font_size, count) in font_counts:
        font_sizes.append(float(font_size))
    font_sizes.sort(reverse=True)

    # aggregating the tags for each font size
    idx = 0
    size_tag = {}
    for size in font_sizes:
        idx += 1
        if size == p_size:
            idx = 0
            size_tag[size] = '<p>'
        if size > p_size:
            size_tag[size] = '<h{0}>'.format(idx)
        elif size < p_size:
            size_tag[size] = '<s{0}>'.format(idx)

    return size_tag


def headers_para(doc, size_tag):
    """Scrapes headers & paragraphs from PDF and return texts with element tags.
    :param doc: PDF document to iterate through
    :type doc: <class 'fitz.fitz.Document'>
    :param size_tag: textual element tags for each size
    :type size_tag: dict
    :rtype: list
    :return: texts with pre-prended element tags
    """
    header_para = []  # list with headers and paragraphs
    first = True  # boolean operator for first header
    previous_s = {}  # previous span

    for page in doc:
        blocks = page.getText("dict")["blocks"]
        for b in blocks:  # iterate through the text blocks
            if b['type'] == 0:  # this block contains text

                # REMEMBER: multiple fonts and sizes are possible IN one block

                block_string = ""  # text found in block
                for l in b["lines"]:  # iterate through the text lines
                    for s in l["spans"]:  # iterate through the text spans
                        if s['text'].strip():  # removing whitespaces:
                            if first:
                                previous_s = s
                                first = False
                                block_string = size_tag[s['size']] + s['text']
                            else:
                                if s['size'] == previous_s['size']:

                                    if block_string and all((c == "|") for c in block_string):
                                        # block_string only contains pipes
                                        block_string = size_tag[s['size']] + s['text']
                                    if block_string == "":
                                        # new block has started, so append size tag
                                        block_string = size_tag[s['size']] + s['text']
                                    else:  # in the same block, so concatenate strings
                                        block_string += " " + s['text']

                                else:
                                    header_para.append(block_string)
                                    block_string = size_tag[s['size']] + s['text']

                                previous_s = s

                    # new block started, indicating with a pipe
                    block_string += "|"

                header_para.append(block_string)

    return header_para


def get_pdf_text(url, is_url=True):
    out = []
    if is_url:
        urlretrieve(url, 'temp.pdf')
        doc = fitz.open("temp.pdf")
    else:
        doc = fitz.open(url)

    font = fonts(doc)

    # print(font)

    tags = font_tags(font[0], font[1])

    # print(tags)

    headers = headers_para(doc, tags)

    # print(headers)

    for text in headers:
        if(text.find("<p>")==0):
            out.append(" ".join(text[3:].replace("|"," ").split()))
        # text = text[text.find(">")+1:]
        # out.append(" ".join(text.replace("|"," ").split()))

    return out


def text_from_txt(url, is_url=True):
    linebreaks = ["\r\n","\r","\n"]
    if is_url:
        source = urlopen(url)

        lines = []
        text = ""

        for line in source:
            line = line.decode("utf-8")
            if(line in linebreaks):
                if text != "":
                    lines.append(text)
                text = ""
            else:
                for breaks in linebreaks:
                    line = line.replace(breaks, " ")
                text += line
        return lines
    else:
        file = open(url, "r")
        file_lines = file.readlines()
        text = ""
        lines = []

        for line in file_lines:
            if(line in linebreaks):
                if text != "":
                    lines.append(text)
                text = ""
            else:
                for breaks in linebreaks:
                    line = line.replace(breaks, " ")
                text += line
        return lines

def remove_duplicates(file):
    open_file = open(file, "r")
    file_elements = open_file.readlines()
    file_elements = list(OrderedDict.fromkeys(file_elements))
    open_file.close()

    write_file = open(file, "w")
    for line in file_elements:
        write_file.write(line)
    write_file.close()


def translation(file_INA, file_NON):
    if(file_INA.find(".txt")!=-1):
        lines = text_from_txt(file_INA,False)
        print(lines)
        sentences_INA = extract_sentences(0.3, lines)[3]
    elif(file_INA.find(".pdf")!=-1):
        sentences_INA =  extract_sentences(0.3,get_pdf_text(file_INA, False))[3]
    elif (file_INA.find(".html")!=-1):
        soup = get_soup(file_INA)
        sentences_INA = extract_sentences(0.4,get_paragraphs(soup))[3]
    else:
        return -1

    if(file_NON.find(".txt")!=-1):
        lines = text_from_txt(file_NON, False)
        sentences_NON = extract_sentences(0.3, lines)[3]
    elif(file_NON.find(".pdf")!=-1):
        sentences_NON =  extract_sentences(0.3,get_pdf_text(file_NON, False))[3]
    elif (file_NON.find(".html")!=-1):
        soup = get_soup(file_NON)
        sentences_NON = extract_sentences(0.4,get_paragraphs(soup))[3]
    else:
        return -2

    if(len(sentences_INA) == len(sentences_NON)):
        for i in range(len(sentences_INA)):
            check_characters = [",",".","!","?","\"","\'","‘","’", ";"]
            check_checks_out = 1
            for check in check_characters:
                if sentences_INA[i].count(check) != sentences_NON[i].count(check):
                    check_checks_out = 0
                    break
            if check_checks_out == 1:
                print(sentences_INA[i], "<===========>", sentences_NON[i])
    for i in range(len(sentences_INA)):
        print(sentences_INA[i], "<===========>", sentences_NON[i])


    print(len(sentences_INA), len(sentences_NON))



def crawler(number_of_iterations, number_of_links_per_iteration, percent = 0.4, only_ia_wiki = False):
    signal.signal(signal.SIGALRM, timeout_handler)

    for j in range(number_of_iterations):
        start = time.time()
        traversed_links_file = open("traversed_links.txt", "r")
        links_file = open("link_queue.txt", "r")
        sentences_file = open("sentencesINA.txt", "a")
        sentences_file_non = open("sentencesNonINA.txt", "a")
        failed_links = open("failedWebsites.txt", "a")

#         link_dict = {}
#         link_types = open("link_dict.txt", "r")
#         link_type_array = link_types.readlines()
#         for element in link_type_array:
#             temp = element.split(" ")
#             link_dict[temp[0]] = int(temp[1])

        traversed_links = traversed_links_file.readlines()
        for i in range(len(traversed_links)):
            traversed_links[i] = traversed_links[i].replace("\n","")

        traversed_links = set(traversed_links)
        link_queue = links_file.readlines()

        traversed_titles_file = open("traversed_titles.txt", "r")
        traversed_titles = traversed_titles_file.readlines()
        for i in range(len(traversed_titles)):
            traversed_titles[i] = traversed_titles[i].replace("\n","")
        traversed_titles = set(traversed_titles)

        for i in range(number_of_links_per_iteration):
            signal.alarm(0)
            print("URL Number", i)
            if len(link_queue) != 0:
                url = link_queue.pop(0)

                url = url.replace("\n", "").replace(" ","%20")
                while True:
                    length = len(url)
                    url = url[0:8] + url[8:].replace("//","/")
                    if len(url)==length:
                        break

                print(url)

                print("Extracting")
                if url not in traversed_links:
                    signal.alarm(0)
                    signal.alarm(30)
                    traversed_links.add(url)

                    bad_links = ["action=edit", "&oldid", "&mobileaction=","upload.wikimedia.org", "&returnto=", "&section=", "Special:","&diff","File:", "#cite_ref","#cite_ref-ref", ".mp3"]
                    bad_wiki_parts = ["?","&","="]

                    is_bad_link = 0
                    for bad_link in bad_links:
                        if(url.find(bad_link)!=-1):
                            is_bad_link = 1
                        if(only_ia_wiki and (url.find("wikipedia")!=-1 or url.find("wiktionary")!=-1) and (url.find("//ia.")==-1 and url.find("interlingua")==-1)):
                            is_bad_link = 1

                    if(url.find("wiki")!=-1):
                        for bad in bad_wiki_parts:
                            if(url.find(bad)!=-1):
                                is_bad_link = 1

                    if is_bad_link == 0:
                        try:
                            url_tag = ""

                            index_period = url.rfind(".")
                            index_slash = url.find("/",index_period)
                            if(index_slash!=-1):
                                type = url[index_period:index_slash]
                            else:
                                type = url[index_period:]

#                             if type in link_dict:
#                                 link_dict[type] = link_dict[type] + 1
#                             else:
#                                 link_dict[type] = 1

                            if url.find(".pdf")!=-1:
                                print("This is a pdf")
                                url_tag = "pdf"
                                sentences =  extract_sentences(0.3,get_pdf_text(url))

                                if not sentences[2]:
                                    for sentence in sentences[0]:
                                        sentences_file.write(sentence + " || " + url_tag + " || " + url + "\n")
                                    if sentences[1] != -1:
                                        for sentence in sentences[1]:
                                            sentences_file_non.write(sentence + " || " + url_tag + " || " + url + "\n")
                                    print("Number of IA Sentences:", len(sentences[0]))
                                    print("Not interlingua!")

                                else:
                                    for sentence in sentences[0]:
                                        sentences_file.write(sentence + " || " + url_tag + " || " + url + "\n")
                                    if sentences[1] != -1:
                                        for sentence in sentences[1]:
                                            sentences_file_non.write(sentence + " || " + url_tag + " || " + url + "\n")
                                    print("Number of IA Sentences:", len(sentences[0]))
                                    print("Success!")
                            elif url.find(".txt")!=-1:
                                print("This is a text file")
                                url_tag = "text"
                                lines = text_from_txt(url)
                                sentences = extract_sentences(0.3, lines)

                                if not sentences[2]:
                                    for sentence in sentences[0]:
                                        sentences_file.write(sentence + " || " + url_tag + " || " + url + "\n")
                                    if sentences[1] != -1:
                                        for sentence in sentences[1]:
                                            sentences_file_non.write(sentence + " || " + url_tag + " || " + url + "\n")
                                    print("Number of IA Sentences:", len(sentences[0]))
                                    print("Not interlingua!")

                                else:
                                    for sentence in sentences[0]:
                                        sentences_file.write(sentence + " || " + url_tag + " || " + url + "\n")
                                    if sentences[1] != -1:
                                        for sentence in sentences[1]:
                                            sentences_file_non.write(sentence + " || " + url_tag + " || " + url + "\n")
                                    print("Number of IA Sentences:", len(sentences[0]))
                                    print("Success!")
                            else:
                                print("This is a website")
                                url_tag = "website"
                                soup = get_soup(url)

                                title = soup.find('title')
                                title = title.getText()

                                print("Title:", title)
                                if title in traversed_titles:
                                    print("Title already traversed!")
                                else:
                                    traversed_titles.add(title)
                                    sentences = extract_sentences(percent,get_paragraphs(soup))
                                    if not checkForLanguage("__label__INA",percent,soup):
                                        for sentence in sentences[0]:
                                            sentences_file.write(sentence + " || " + url_tag + " || " + url + "\n")
                                        if sentences[1] != -1:
                                            for sentence in sentences[1]:
                                                sentences_file_non.write(sentence + " || " + url_tag + " || " + url + "\n")
                                        print("Number of IA Sentences:", len(sentences[0]))
                                        print("Not interlingua!")

                                    else:
                                        for sentence in sentences[0]:
                                            sentences_file.write(sentence + " || " + url_tag + " || " + url + "\n")
                                        if sentences[1] != -1:
                                            for sentence in sentences[1]:
                                                sentences_file_non.write(sentence + " || " + url_tag + " || " + url + "\n")
                                        print("Number of IA Sentences:", len(sentences[0]))
                                        print("Success!")

                                        links = get_links(soup, url)
                                        for link in links:
                                            if link not in traversed_links:
                                                link_queue.append(link + "\n")
                        except TimeoutException:
                            print("Timeout Exception")
                            print("---------")
                            failed_links.write(url + " -> " + "Timeout Exception" + ": " + "Link took over 30 second to be processed" + "\n")
                            continue
                        except Exception as e:
                            signal.alarm(0)
                            exc_type, exc_value, exc_traceback = sys.exc_info()
                            traversed_links.add(url)
                            e = sys.exc_info()[0]
                            print( "Error:", repr(e))

                            fails = ["HTTP Error 403: Forbidden", "HTTP Error 410: Gone", "HTTP Error 404: Not Found",
                                     "HTTP Error 400: Bad Request"]
                            if str(exc_value) not in fails:
                                failed_links.write(url + " -> " + str(exc_type) + ": " + str(exc_value) + "\n")
                            pass
                        else:
                            signal.alarm(0)
                    else:
                        print("Bad link.")
                else:
                    print("Link already traversed")
                print("---------")
            else:
                print("Queue empty!")
                break

        signal.alarm(0)
#         link_dict = sorted(link_dict.items(), key=lambda x: x[1], reverse=True)
#         print(link_dict)

        traversed_links_file.close()
        links_file.close()
#         link_types.close()
        sentences_file.close()
        sentences_file_non.close()
        traversed_links_file = open("traversed_links.txt", "w")
        links_file = open("link_queue.txt", "w")
        traversed_titles_file = open("traversed_titles.txt", "w")

        # link_types = open("link_dict.txt", "w")

        for link in traversed_links:
            link = link.replace("\n","")
            link = link.replace("\t","")
            traversed_links_file.write(link + "\n")

        for link in link_queue:
            link = link.replace("\n","")
            link = link.replace("\t","")
            links_file.write(link + "\n")

        for title in traversed_titles:
            title = title.replace("\n","")
            title = title.replace("\t","")
            traversed_titles_file.write(title + "\n")

        # for link_type in link_dict:
            # link_types.write(link_type[0] + " " + str(link_type[1]) + "\n")

        remove_duplicates("sentencesINA.txt")
        remove_duplicates("sentencesNonINA.txt")

        traversed_links_file.close()
        links_file.close()
#         link_types.close()

        remove_duplicates("link_queue.txt")

        end = time.time()
        elapsed = end - start
        print("Time:", elapsed, "seconds")


if __name__ == "__main__":
    model = fasttext.load_model("8_lang_50k_model.bin")
    crawler(30,100000,0.6,True)
