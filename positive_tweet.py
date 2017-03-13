import HTMLParser

import re

from collections import defaultdict

from random import randint

import en

from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize.moses import MosesDetokenizer

# This function takes a tweepy tweet object and returns text of the same tweet,
# but with all the negative sentiment words replaced with a random positive
# sentiment word matching it's part of speech(POS).


def positive_tweet(tweet):
    # Flag to note if any changes were made
    change_made = False
    # Tags words by pos - (word, pos)
    tagged = en.sentence.tag(tweet.text)
    mod_tweet = []

    for word in tagged:
        mod_word = check_replace(word[0], word[1], neg_words)
        mod_tweet.append(mod_word[0])
        if mod_word[1] is True:
            change_made = True

    detokenizer = MosesDetokenizer()
    final = detokenizer.detokenize(mod_tweet, return_str=True)
    final = HTMLParser.HTMLParser().unescape(final)

    return [final, change_made]

# All other functions act in support of positive_tweet.

# Imports sentiment word list as list of dicts.
# Word list comes from http://mpqa.cs.pitt.edu/lexicons/subj_lexicon/
# See their license for use.
list_tff = 'subjectivity_clues_hltemnlp05/subjclueslen1-HLTEMNLP05.txt'
tags = ['type', 'pos1', 'stemmed1', 'priorpolarity']

# Parses the lines in the tff file containing words and sentiments.
# This does not work for capturing hyphenated words.


def parse_tff(line, tags):
    features = {}
    for i in tags:
        features[i] = re.findall(r"{}=(\w+)".format(i), line)[0]
    return features


# Creates dict of features for negative words
neg_dict = defaultdict(list)

file_fft = open(list_tff)
for line in file_fft:
    word = re.findall(r"{}=(.*) pos1".format('word1'), line)[0]
    features = parse_tff(line, tags)
    if features["priorpolarity"] == 'negative':
        neg_dict[word].append(features)

# Creates a list of negative words
neg_words = neg_dict.keys()

# Creates a dictionary of of positive words grouped by POS.
pos_dict = defaultdict(list)
file_fft = open(list_tff)
for line in file_fft:
    pol = re.findall(r"{}=(\w+)".format('priorpolarity'), line)[0]
    word = re.findall(r"{}=(.*) pos1".format('word1'), line)[0]
    pos = en.sentence.tag(word)
    pos = pos[0][1]
    if pol == 'positive':
        pos_dict[pos].append(word)


# Translation dict
# Converts between various POS formats
tld = {'JJ': 'adj',
       'JJR': 'adj',
       'JJS': 'adj',
       'NN': 'noun',
       'NNP': 'noun',
       'NNPS': 'noun',
       'NNS': 'noun',
       'NNP': 'noun',
       'RB': 'adverb',
       'RBR': 'adverb',
       'RBS': 'adverb',
       'RP': 'adverb',
       'VA': 'verb',
       'VB': 'verb',
       'VBD': 'verb',
       'VBG': 'verb',
       'VBN': 'verb',
       'VBP': 'verb',
       'VBZ': 'verb',
       'VP': 'verb'
       }


# Functions to determine if a word is negative and find
# a suitable replacement if it is.
def check_replace(word, pos, neg_words):
    # Is it in the neg dict list?
    mod_word = check_neg_pos_match(word, pos, neg_words, word)
    # If the word doesn't match, try its lem.
    if mod_word[0] is True:
        return [mod_word[1], True]
    else:
        try:
            pos_lem = tld[pos]
            if pos_lem == 'verb':
                lemmatizer = WordNetLemmatizer()
                lem = lemmatizer.lemmatize(word, wordnet.VERB)
                lem_match = check_neg_pos_match(lem, pos, neg_words, word)
                if lem_match[0] is True:
                    return [lem_match[1], True]
                else:
                    return [mod_word[1], False]
            else:
                return [mod_word[1], False]
        except:
            return [mod_word[1], False]


def check_neg_pos_match(word_lem, pos_o, neg_words, original_word):
    # Flag to see if new word was chosen.
    nwc = None
    word_l = word_lem.lower()
    # Is the word in the negative words list?
    if word_l in neg_words:
        # If so, do any entries for that word have the same pos?
        for features in neg_dict[word_l]:
            pos = features['pos1']
            # For a matching pos, then return the word and matching pos
            if (pos == "anypos") or tld[pos_o] == pos:
                new_word = random_positive_word(pos_o, pos_dict)
                # If it's a verb make sure the tense matches
                if pos == 'verb':
                    new_word = match_tense(new_word, original_word)
                # Make sure the capitalization matches
                nwc = match_cap(new_word, original_word)
        if nwc is not None:
            return [True, nwc]
        else:
            return [False, original_word]
    else:
        return [False, original_word]


# Find a similar positive word.
def random_positive_word(pos, pos_dict):
    # Change mis-identified words to adjectives
    if pos == "NNP":
        pos = "JJ"
    i = randint(0, len(pos_dict[pos]) - 1)
    return pos_dict[pos][i]


# Function to correct the tense of any verbs being replaced.
def match_tense(word, word_o):

    tense = en.verb.tense(word_o)

    test = {'past': en.verb.past(word),
            '3rd singular present': en.verb.present(word, person='3'),
            '3rd singular past': en.verb.past(word, person='3'),
            'past participle': en.verb.past_participle(word),
            'infinitive': en.verb.infinitive(word),
            'present participle': en.verb.present_participle(word),
            '1st singular present': en.verb.present(word, person='1'),
            '1st singular past': en.verb.past(word, person='1'),
            'past plural': en.verb.past(word, person='plural'),
            '2nd singular present': en.verb.present(word, person='2'),
            '2nd singular past': en.verb.past(word, person='2'),
            'present plural': en.verb.present(word, person='plural')
            }
    return test[tense]


# Function to match the capitialization used in the original tweet,
# either first letter capitalized or whole word.
def match_cap(out, test):
    if test[0].isupper() is True:
        if test[1].isupper() is True:
            caps = []
            for i in out:
                caps.append(i.upper())
            outcaps = "".join(caps)
            return outcaps
        else:
            return out[:1].upper() + out[1:]
    else:
        return out
