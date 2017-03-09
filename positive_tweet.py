from collections import defaultdict
import re
import en
from random import randint
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.tokenize.moses import MosesDetokenizer
import HTMLParser


#This function takes a tweet and returns text of the same tweet, but with all the negative sentiment words replaced with positive sentiment ones
def positive_tweet(tweet):
    #flag to note if any changes were made
    change_made = False
    text = word_tokenize(tweet.text)
    #tags words by pos - (word, pos)
    tagged = en.sentence.tag(tweet.text)
    lemmatizer = WordNetLemmatizer()
    
    mod_tweet = []
    for word in tagged:
        mod_word = check_replace(word[0], word[1], neg_words)
        mod_tweet.append(mod_word[0])
        if mod_word[1] == True:
            change_made = True

    detokenizer = MosesDetokenizer()
    final = detokenizer.detokenize(mod_tweet, return_str=True)
    final = HTMLParser.HTMLParser().unescape(final)
    
    return [final, change_made]

#All other functions act in support of positive_tweet

#import sentiment word list as list of dicts
#From http://mpqa.cs.pitt.edu/lexicons/subj_lexicon/
#see their license
list_tff = 'subjectivity_clues_hltemnlp05/subjclueslen1-HLTEMNLP05.txt'
tags = ['type', 'pos1', 'stemmed1', 'priorpolarity']

#parses the lines in the tff file containing words and sentiments
#This does not work for capturing hyphenated words
def parse_tff(line, tags):
    features = {}
    for i in tags:
        features[i] = re.findall(r"{}=(\w+)".format(i),line)[0]
    return features


#creat dict of features for negative words
neg_dict = defaultdict(list)

file_fft = open(list_tff) 
for line in file_fft:
    word = re.findall(r"{}=(.*) pos1".format('word1'),line)[0]
    features = parse_tff(line, tags)
    if features["priorpolarity"] == 'negative':
        neg_dict[word].append(features)
        
#create a list of negative words
neg_words = neg_dict.keys()
        
#creat a dictionary of of positive words grouped by pos:
pos_dict = defaultdict(list)
file_fft = open(list_tff)
for line in file_fft:
    pol = re.findall(r"{}=(\w+)".format('priorpolarity'),line)[0]
    word = re.findall(r"{}=(.*) pos1".format('word1'),line)[0]
    pos = en.sentence.tag(word)
    pos = pos[0][1]
    if pol == 'positive':
        pos_dict[pos].append(word)


#translation dict
#converts between varios part of speach (pos) formats
tld = {'JJ':'adj',
       'JJR':'adj',
       'JJS':'adj',
       'NN' : 'noun',
       'NNP' : 'noun',
       'NNPS' : 'noun',
       'NNS' : 'noun',
       'NNP' : 'noun',
        'RB' : 'adverb',
       'RBR' : 'adverb',
       'RBS' : 'adverb',
       'RP' : 'adverb',
       'VA': 'verb',
       'VB': 'verb',
       'VBD': 'verb',
       'VBG': 'verb',
       'VBN': 'verb',
       'VBP': 'verb',
       'VBZ': 'verb',
       'VP': 'verb'
      }


#functions to determine if a word is negative and find a suitable replacement if it is
def check_replace(word, pos, neg_words):
    #is it in the neg dict list?
    mod_word = check_neg_pos_match(word, pos, neg_words, word)
    #if the word doesn't match, try its lem.
    if mod_word[0] == True:
        return [mod_word[1], True]
    else:
        try: 
            pos_lem = tld[pos]
            if pos_lem == 'verb':
                lemmatizer = WordNetLemmatizer()
                lem = lemmatizer.lemmatize(word, wordnet.VERB)
                lem_match = check_neg_pos_match(lem, pos, neg_words, word)
                if lem_match[0] == True:
                    return [lem_match[1], True]
                else:
                    return [mod_word[1], False]
            else:
                return [mod_word[1], False]
        except:
            return [mod_word[1], False]
    
    
def check_neg_pos_match(word_lem, pos_o, neg_words, original_word):
    #flag to see if new word was chosen
    nwc =None
    word_l=word_lem.lower()
    #is the word in the negative words list?
    if word_l in neg_words:
        #if so, do any entries for that word have the same pos?
        for features in neg_dict[word_l]:
            pos = features['pos1']
            #print word_l, pos_o, pos
            #for a matching pos, then return the word and matching pos
            if (pos == "anypos") or tld[pos_o] == pos:
                #print word_l, pos_o, tld[pos_o], pol, pos
                new_word = random_positive_word(pos_o, pos_dict)
                #if it's a verb make sure the tense matches
                if pos == 'verb':
                    new_word = match_tense(new_word,original_word)
                #make sure the capitalization matches
                nwc = match_cap(new_word, original_word)
        if nwc != None:
            return [True, nwc]
        else:
            return [False, original_word]
    else:
        return [False, original_word]



#find similar positive word
def  random_positive_word(pos, pos_dict):
    #change mis-identified words to adjectives
    if pos == "NNP":
        pos = "JJ"
    i = randint(0,len(pos_dict[pos])-1)
    return pos_dict[pos][i]    

#function to correct the tense of any verbs being replaced
def match_tense(word, word_o):
    
    tense = en.verb.tense(word_o)

    test = {'past':en.verb.past(word),
            '3rd singular present':en.verb.present(word, person='3'),
            '3rd singular past':en.verb.past(word, person='3'),
            'past participle':en.verb.past_participle(word),
            'infinitive':en.verb.infinitive(word),
            'present participle':en.verb.present_participle(word),
            '1st singular present':en.verb.present(word, person='1'),
            '1st singular past':en.verb.past(word, person='1'),
            'past plural':en.verb.past(word, person='plural'),
            '2nd singular present':en.verb.present(word, person='2'),
            '2nd singular past':en.verb.past(word, person='2'),
            'present plural':en.verb.present(word, person='plural')
           }

    return test[tense]

#function to match the capitialization used in the original tweet, either first letter capitalized or whole word
def match_cap(out, test):
    if test[0].isupper() == True:
        if test[1].isupper() == True:
            caps = []
            for i in out:
                caps.append(i.upper())
            outcaps =  "".join(caps)
            return outcaps
        else:
            return out[:1].upper() + out[1:]
    else:
        return out