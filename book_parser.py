'''
Book parser written to parse Tolstoy's War and Peace.
Stores book index, book year, chapter index, paragraph index, sentence index,
sentence text, word indices, and word text into a nested dictionary and
serializes dictionary into JSON format.
'''

from collections import defaultdict
from nltk import tokenize
from statemachine import StateMachine
from unidecode import unidecode
import sys
import json

# punct is a list of punctuation to be removed for words
punct = '''!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~``\'\'...'''
# global variables for indexing (for convenience)
book_n, year, chapter_n, paragraph_n = 0, 0, 0, 0

def make_dict():
    # Makes a nested dictionary that allows for changing values at any depth
    return defaultdict(make_dict)

nested_dict = defaultdict(make_dict) # Initiate the nested dict to store words

def dictify(d):
    # Converts nested_dict from defaultdict to normal python dict
    for k,v in d.items():
        if isinstance(v,defaultdict):
            try:
                d[int(k)] = dictify(v)
            except ValueError:
                d[k] = dictify(v)
    return dict(d)

def iter_all(d,depth=1):
    # Prints nested dictionary in a readable way (for debugging)
    for k,v in d.items():
        print("-"*depth,k)
        if type(v) is defaultdict:
            iter_all(v,depth+1)
        else:
            print("-"*(depth+1),v)

# Machine States
def error(text):
    # Unidentifiable line
    sys.stderr.write('Unidentifiable line:\n'+ line)

def end(text):
    # End state
    sys.stdout.write('Processing Successful\n')

def book(text):
    # Start with the book index and year and determine state transition
    # to chapter after 5 consecutive blank lines
    # Resets chapter index
    global chapter_n
    global book_n
    global year
    global nested_dict
    chapter_n = 0
    fp = text
    blankline_count = 0
    while 1:
        line = fp.readline()
        if line in ['\n', '\r\n']:  blankline_count += 1
        else:                       blankline_count = 0
        if line[:4] == 'BOOK' or line[:14] == 'FIRST EPILOGUE' or line[:15] == 'SECOND EPILOGUE':
            book_n += 1
            if line[:4] == 'BOOK' or line[:14] == 'FIRST EPILOGUE':
                year = line[line.find(':')+2:-1]
            # Second Epilogue has no year so set year to 0
            if line[:15] == 'SECOND EPILOGUE':
                year = 0
            nested_dict[book_n]['year'] = year
        if blankline_count == 5:    return chapter, fp
        else:                       continue

def chapter(text):
    # Chapter state, tracks index and can transition to paragraph
    global chapter_n
    global paragraph_n
    chapter_n += 1
    paragraph_n = 0
    fp = text
    while 1:
        line = fp.readline()
        if line in ['\n', '\r\n']:      return paragraph, fp
        else:                           continue

def paragraph(text):
    # Paragraph state, tracks index and transitions to sentence
    global paragraph_n
    paragraph_n += 1
    paragraph = ''
    fp = text
    while 1:
        line = fp.readline()
        if line not in ['\n', '\r\n']:  paragraph += line
        else:                           return sentence, (paragraph, fp)

def sentence(text):
    # Sentence state, tokenizes paragraph into
    # sentences and words (filters out punctuation)
    # Stores information in nested_dict
    global nested_dict
    paragraph, fp = text
    sentences = tokenize.sent_tokenize(paragraph)
    for i, sent in enumerate(sentences):
        sent = unidecode(sent)
        sent = sent.replace('\n',' ') # Replace \n character with space
        nested_dict[book_n][chapter_n][paragraph_n][i+1]['sentence'] = sent
        sent = sent.replace('-',' ') # Replace hyphens with commas to separate words
        words = [w for w in tokenize.word_tokenize(sent[:-1].lower()) \
        if w not in punct] # sent[:-1] remove .!?
        for j, word in enumerate(words):
            nested_dict[book_n][chapter_n][paragraph_n][i+1][j+1] = word
    return end_paragraph, fp

def end_paragraph(text):
    # State at the end of a paragraph after sentences and words are processed
    # Determines the next state based (book, chapter, another paragraph or end)
    fp = text
    index = fp.tell()
    blankline_count = 0
    while 1:
        line = fp.readline()
        if blankline_count > 8:
            fp.seek(index)
            return end, fp
        if line[:4] == 'BOOK' or line[:14] == 'FIRST EPILOGUE' or line[:15] == 'SECOND EPILOGUE':
            fp.seek(index)
            return book, fp
        if line[:7] == 'CHAPTER':
            return chapter, fp
        if line in ['\n', '\r\n']:
            blankline_count += 1
            index = fp.tell() # Sometimes paragraphs are separated by more than 1 blankspace
        else:
            fp.seek(index)
            return paragraph, fp

if __name__== "__main__":
    m = StateMachine()
    m.add_state(book)
    m.add_state(chapter)
    m.add_state(paragraph)
    m.add_state(sentence)
    m.add_state(end_paragraph)
    m.add_state(error, end_state=1)
    m.add_state(end, end_state=1)
    m.set_start(book)
    m.run('warandpeace_body.txt')
    final_dict = dictify(nested_dict) # Reformat defaultdict to normal dictionary
    with open('textbody_dict.json', 'w') as fp:
        json.dump(final_dict, fp, indent=4)
