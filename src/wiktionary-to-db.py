import traceback
import mwxml
import pprint

from utils.db import deleteAllWordData, insertWordData
from utils.outputfile import initDir, slugify, writeFile, writeFileFromList
from utils.timer import startTimer, stopTimer
from utils.mediawikiparser import doesTextSmellLikeValidPronunciation, getPronunsFromMediaWikiText

# ----- configuration -----
DUMP_XML_PATH = 'C:\\full\\path\\to\\dump.xml' # required
NUM_PAGES_TO_SKIP = 0
NUM_PAGES_TO_PARSE = 100000000
TARGET_WORDS = []
SHOULD_CLEAR_REPORT_FILES = True
SHOULD_CLEAR_MEDIAWIKI_PAGES = True
SHOULD_WRITE_MEDIAWIKI_PAGES = False
SHOULD_CLEAR_FAILED_PAGES = True
SHOULD_CLEAR_WORDS_IN_DB = True
SHOULD_INSERT_WORDS_TO_DB = True
# ----- end configuration -----
# TODO load configuration from file instead?

REPORT_DIR = 'report'
MEDIAWIKI_PAGE_DIR = 'mediawiki'
FAILED_PAGE_DIR = 'failed-pages'

def main():
    startTimer()

    if SHOULD_CLEAR_REPORT_FILES:
        initDir(REPORT_DIR)
    if SHOULD_CLEAR_MEDIAWIKI_PAGES:
        initDir(MEDIAWIKI_PAGE_DIR)
    if SHOULD_CLEAR_FAILED_PAGES:
        initDir(FAILED_PAGE_DIR)

    wikiDump = mwxml.Dump.from_file(open(DUMP_XML_PATH, encoding='utf-8'))

    processedWords = []
    skippedPages = []
    pagesWithNoPronunSmell = []
    pagesWithNoValidEnglishPronuns = []
    failedPages = []
    totalPagesToProcess = NUM_PAGES_TO_SKIP + NUM_PAGES_TO_PARSE

    pagesWithPronuns = 0
    for pageIndex in range(totalPagesToProcess):
        page = next(wikiDump.pages, None)
        if page == None:
            print(f' !! no more pages to process !!')
            break
        pageFileName = getPageFileName(pageIndex, page.id, page.title)
        if pageIndex < NUM_PAGES_TO_SKIP or (len(TARGET_WORDS) > 0 and page.title not in TARGET_WORDS): 
            skippedPages.append(pageFileName)
            continue

        # there's exactly one revision
        text = (next(page)).text

        if not text or len(text) == 0 or not doesTextSmellLikeValidPronunciation(text):
            pagesWithNoPronunSmell.append(pageFileName)
            continue

        if SHOULD_WRITE_MEDIAWIKI_PAGES:
            writeFile(MEDIAWIKI_PAGE_DIR, pageFileName + '.txt', text or '', shouldPrint=False)

        try:
            pagePronuns = getPronunsFromMediaWikiText(text)
            if len(pagePronuns) == 0:
                pagesWithNoValidEnglishPronuns.append(pageFileName)
                continue
            pageWords = [Word(ipa, pageIndex, page.id, page.title) for ipa in pagePronuns]
            print(f'{len(pagePronuns)} pronun(s): {pageIndex:08d} {page.title}')
            processedWords.extend(pageWords)
            pagesWithPronuns += 1
        except Exception:
            print(f'  !! failed to process !!')
            errorStr = traceback.format_exc()
            print(errorStr)
            failedPages.append(f'{pageIndex}: {page.title}\n{errorStr}\n')
            writeFile(FAILED_PAGE_DIR, pageFileName + '.txt', text or '')

    print()
    writeFileFromList(REPORT_DIR, 'processedWords.txt', [formatWordDataLine(word) for word in processedWords])
    writeFileFromList(REPORT_DIR, 'skippedPages.txt', skippedPages)
    writeFileFromList(REPORT_DIR, 'pagesWithNoPronunSmell.txt', pagesWithNoPronunSmell)
    writeFileFromList(REPORT_DIR, 'pagesWithNoValidEnglishPronuns.txt', pagesWithNoValidEnglishPronuns)
    writeFileFromList(REPORT_DIR, 'failedPages.txt', failedPages)

    if SHOULD_CLEAR_WORDS_IN_DB:
        deleteAllWordData()
    if SHOULD_INSERT_WORDS_TO_DB:
        insertWordData(processedWords)
        print(f'\ndone writing to database')

    print(f'\ndone! processed {len(processedWords)} pronuns from {pagesWithPronuns} pages')
    print(f'({len(pagesWithNoPronunSmell)} no smell | {len(pagesWithNoValidEnglishPronuns)} no valid pronun | {len(failedPages)} failed)')
    
    timerReport = stopTimer()
    print(timerReport)

def Word(ipa, pageIndex, pageId, pageTitle):
    return { 'pageTitle': pageTitle, 'pageIndex': pageIndex, 'pageId': pageId, 'title':  pageTitle.lower(), **ipa }

def getPageFileName(index, pageId, pageTitle):
    return f'{index:09d}_{pageId}_{slugify(pageTitle, True)}'

def formatWordDataLine(word):
    pageIndex, pageId, pageTitle, title, pronunLine, accents, ipas = [word[k] for k in ('pageIndex', 'pageId', 'pageTitle', 'title', 'pronunLine', 'accents', 'ipas')]
    return f'i {pageIndex} (id {pageId}):  {pageTitle} ({title}):  {pprint.pformat(accents)}:  {pprint.pformat(ipas)}:    {pronunLine}'


main()
