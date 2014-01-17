# Implementation of RAKE - Rapid Automtic Keyword Exraction algorithm
# as described in:
# Rose, S., D. Engel, N. Cramer, and W. Cowley (2010).
# Automatic keyword extraction from indi-vidual documents.
# In M. W. Berry and J. Kogan (Eds.), Text Mining: Applications and Theory.unknown: John Wiley and Sons, Ltd.

import re
import operator
import logging
logging.basicConfig(level=logging.INFO)
import math

debug = False
test = True

def isnum (s):
    try:
        float(s) if '.' in s else int(s)
        return True
    except ValueError:
        return False

# Utility function to load stop words from a file and return as a list of words
# @param stopWordFile Path and file name of a file containing stop words.
# @return list A list of stop words.
def loadStopWords(stopWordFile):
    stopWords = []
    for line in stopWordFile:
        if (line.strip()[0:1] != "#"):
            for word in line.split( ): #in case more than one per line
                stopWords.append(word)
    return stopWords

# Utility function to return a list of all words that are have a length greater than a specified number of characters.
# @param text The text that must be split in to words.
# @param minWordReturnSize The minimum no of characters a word must have to be included.
def separatewords(text,minWordReturnSize):
    splitter=re.compile('[^a-zA-Z0-9_\\+\\-/]')
    words = []
    for singleWord in splitter.split(text):
        currWord = singleWord.strip().lower()
        #leave numbers in phrase, but don't count as words, since they tend to invlate scores of their phrases
        if len(currWord)>minWordReturnSize and currWord != '' and not isnum(currWord):
            words.append(currWord)
    return words

# Utility function to return a list of sentences.
# @param text The text that must be split in to sentences.
def splitSentences(text):
    sentenceDelimiters = re.compile(u'[.!?,;:\t\\-\\"\\(\\)\\\'\u2019\u2013]')
    sentenceList = sentenceDelimiters.split(text)
    return sentenceList

def buildStopwordRegExPattern(pathtostopwordsfile):
    stopwordlist = loadStopWords(pathtostopwordsfile)
    stopwordregexlist = []
    for wrd in stopwordlist:
        wrdregex = '\\b' + wrd + '\\b'
        stopwordregexlist.append(wrdregex)
    stopwordpattern = re.compile('|'.join(stopwordregexlist), re.IGNORECASE)
    return stopwordpattern

def generateCandidateKeywords(sentenceList, stopwordpattern):
    phraseList = []
    for s in sentenceList:
        tmp = re.sub(stopwordpattern, '|', s.strip())
        phrases = tmp.split("|")
        for phrase in phrases:
            phrase = phrase.strip().lower()
            if (phrase!=""):
                phraseList.append(phrase)
    return phraseList

def calculateWordScores(phraseList):
    wordfreq = {}
    worddegree = {}
    for phrase in phraseList:
        wordlist = separatewords(phrase,0)
        wordlistlength = len(wordlist)
        wordlistdegree = wordlistlength - 1
        #if wordlistdegree > 3: wordlistdegree = 3 #exp.
        for word in wordlist:
            wordfreq.setdefault(word,0)
            wordfreq[word] += 1
            worddegree.setdefault(word,0)
            worddegree[word] += wordlistdegree #orig.
            #worddegree[word] += 1/(wordlistlength*1.0) #exp.
    for item in wordfreq:
        worddegree[item] = worddegree[item]+wordfreq[item]

    # Calculate Word scores = deg(w)/frew(w)
    wordscore = {}
    for item in wordfreq:
        wordscore.setdefault(item,0)
        wordscore[item] = worddegree[item]/(wordfreq[item] * 1.0) #orig.
        #wordscore[item] = wordfreq[item]/(worddegree[item] * 1.0) #exp.
    return wordscore

def generateCandidateKeywordScores(phraseList, wordscore):
    keywordcandidates = {}
    for phrase in phraseList:
        keywordcandidates.setdefault(phrase,0)
        wordlist = separatewords(phrase,0)
        candidatescore = 0
        for word in wordlist:
            candidatescore += wordscore[word]
        keywordcandidates[phrase] = candidatescore
    return keywordcandidates


#### Non ho alcuna idea di cosa facciano le righe sopra; sono un ragazzo
###  semplice e mi limito a copincollare gli esempi


def estrai(text, stoppath):
    sentenceList = splitSentences(text)
    if stoppath is not None:
        stopwordpattern = buildStopwordRegExPattern(open(stoppath))
    else:
        logging.warning("You're running without a stopword list;"
                       + " this will probably give bad results")
        from StringIO import StringIO
        stopwordpattern = buildStopwordRegExPattern(StringIO(''))

    # generate candidate keywords
    phraseList = generateCandidateKeywords(sentenceList, stopwordpattern)

    # calculate individual word scores
    wordscores = calculateWordScores(phraseList)

    # generate candidate keyword scores
    keywordcandidates = generateCandidateKeywordScores(phraseList, wordscores)
    logging.debug(keywordcandidates)

    sortedKeywords = sorted(keywordcandidates.iteritems(),
                            key=operator.itemgetter(1), reverse=True)
    logging.debug(sortedKeywords)

    totalKeywords = len(sortedKeywords)
    logging.debug(totalKeywords)
    return sortedKeywords[:10]


def estrai_cmd(options):
    keywords = estrai(open(options.textpath).read(), options.stoppath)
    print '\n'.join(('%.1f\t%s' % (perc, key.replace('\n', ' '))
                     for key, perc in keywords))
if test:
    from optparse import OptionParser

    usage = "usage: %prog [options] file"
    parser = OptionParser(usage=usage)
    parser.add_option('-s', '--stopword', dest='stoppath',
                      help="The file containing stopwords (one per line)")
    parser.add_option("-D", "--debug", action="store_true", dest="debug",
                      default=False, help="be super verbose (debug)")
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error("Wrong number of arguments")
    options.textpath = args[0]

    estrai_cmd(options)
