from mimetypes import init
import re
import sys

from src.utils.db import tryGetWordData
from src.utils.outputfile import initDir, slugify, writeFile, writeFileFromList


def main():
    # ----- controls -----
    OUT_SUBDIR = 'text-to-ipa-test'
    REPORT_DIR = f'{OUT_SUBDIR}/report'
    SHOULD_CLEAR_REPORT_FILES = False
    SHOULD_WRITE_REPORT_FILES = True
    # ----- end controls -----

    initDir(OUT_SUBDIR, shouldDeleteIfExisting=False)
    if SHOULD_CLEAR_REPORT_FILES or SHOULD_WRITE_REPORT_FILES:
        initDir(REPORT_DIR)

    convertedWords = []
    convertedText = ''

    # take multiple lines of English text as input
    # https://medium.com/explorations-in-python/redirection-and-piping-in-python-353bba3e6dc3
    for line in sys.stdin:
        for token in line.lower().split():
            token = removePunctuation(token)
            foundIpa = getFirstIpa(token)
            if not foundIpa:
                foundIpa = trySecondaryIpas(token)
                if foundIpa: print(f'{token} -> {foundIpa}') # TODO remove
            if not foundIpa: foundIpa = '(no hit)'
            convertedWords.append(f'"{token}" -> {foundIpa}')
            convertedText += f'{foundIpa} '
            # print(f'"{token}" -> {foundIpa}')
        convertedText += '\n'
    # TODO for now, just report the converted text

    print()
    writeFileFromList(REPORT_DIR, 'converted-words.txt', convertedWords)
    writeFile(REPORT_DIR, 'converted-text.txt', convertedText)

def removePunctuation(token):
    # TODO remove punctuation like .,:;(){}[] but leave -'
    return re.sub(r'[,"\?\!\(\)]', '', token)

def getFirstIpa(token):
    wordData = tryGetWordData(token)
    if not wordData: return None
    # TODO more specific choice - just return the first one for now
    return wordData['ipas'][0]

def trySecondaryIpas(origToken):
    # handle possessive/contractions: "girl's", "world's"
    if origToken.endswith('\'s'):
        subtokens = origToken.split('\'')
        wordData1 = tryGetWordData(subtokens[0])
        wordData2 = tryGetWordData(subtokens[1])
        if wordData1 and wordData2:
            return joinIpas(wordData1['ipas'][0], wordData2['ipas'][0])

    # handle shortened -ing: "walkin'", "comin'"
    if origToken.endswith('in\''):
        token = origToken.replace('in\'', 'ing')
        wordData = tryGetWordData(token)
        if wordData: return wordData['ipas'][0]

    # handle -es plurals: "shapes", "washes"
    if origToken.endswith('es'):
        tokenWithE = origToken[:-1]
        wordData = tryGetWordData(tokenWithE)
        if wordData: return makePlural(wordData['ipas'][0])
        tokenWithoutE = origToken[:-2]
        wordData = tryGetWordData(tokenWithoutE)
        if wordData: return makePlural(wordData['ipas'][0])

    # handle -s plurals: "houseplants", "glitters"
    if origToken.endswith('s'):
        token = origToken[:-1]
        wordData = tryGetWordData(token)
        if wordData: return makePlural(wordData['ipas'][0])

    # handle -er comparitives and agent nouns: "colder", "computer"
    if origToken.endswith('er'):
        tokenWithE = origToken[:-1]
        wordData = tryGetWordData(tokenWithE)
        if wordData: return makeComparitive(wordData['ipas'][0])
        tokenWithoutE = origToken[:-2]
        wordData = tryGetWordData(tokenWithoutE)
        if wordData: return makeComparitive(wordData['ipas'][0])
    
    # TODO handle double consonant -er: "jogger", "swimmer"

    # TODO handle double consonant superlative: "baddest"

    # handle simple superlative: "sharpest", "fastest"
    if origToken.endswith('est'):
        tokenWithE = origToken[:-2]
        wordData = tryGetWordData(tokenWithE)
        if wordData: return makeSuperlative(wordData['ipas'][0])
        tokenWithoutE = origToken[:-3]
        wordData = tryGetWordData(tokenWithoutE)
        if wordData: return makeSuperlative(wordData['ipas'][0])

    return None

def joinIpas(ipa1, ipa2):
    # TODO is it possible that they wouldn't have delimiters?
    return '/' + ipa1[1:-1] + ipa2[1:-1] + '/'

def makePlural(singularIpa):
    # https://en.wiktionary.org/wiki/-s#Pronunciation
    # TODO handle when the last char is a symbol like ')'...
    lastIpaChar = singularIpa[-2]
    if lastIpaChar in [ 'p', 't', 'k', 'f', 'θ' ]:
        return singularIpa[:-1] + 's/'
    elif lastIpaChar in [ 'm', 'n', 'ŋ', 'b', 'd', 'ɡ', 'v', 'ð', 'l' ]:
        return singularIpa[:-1] + 'z/'
    else: 
        return singularIpa[:-1] + 'ɪz/'

def makeSuperlative(ipa):
    return ipa[:-1] + 'ɪst/'

def makeComparitive(ipa):
    return ipa[:-1] + 'ɚ/'

main()
