import traceback
import mwxml
import pprint
import re
from mediawiki import *

from utils.db import deleteAllWordData, insertWordData
from utils.outputfile import initDir, slugify, writeFile, writeFileFromList
from utils.timer import startTimer, stopTimer
from wiktionaryToDb.wiktionaryparser import doesTextSmellLikeValidPronunciation, getIpasFromWikiHtml


def main():
    # ----- controls -----
    DUMP_PATH = "C:\\Users\\ben\\Downloads\\enwiktionary-20220701-pages-meta-current.xml"
    OUT_SUBDIR = 'wiktionary-to-db'
    REPORT_DIR = f'{OUT_SUBDIR}/report'
    SHOULD_CLEAR_REPORT_FILES = True
    MEDIAWIKI_PAGE_DIR = f'{OUT_SUBDIR}/mediawiki'
    SHOULD_CLEAR_MEDIAWIKI_PAGES = True
    SHOULD_WRITE_MEDIAWIKI_PAGES = True
    NONSMELL_PAGE_DIR = f'{OUT_SUBDIR}/non-smell-pages'
    SHOULD_CLEAR_NONSMELL_PAGES = True
    SHOULD_WRITE_NONSMELL_PAGES = True #
    HTML_PAGE_DIR = f'{OUT_SUBDIR}/html'
    SHOULD_CLEAR_HTML_PAGES = True
    SHOULD_WRITE_HTML_PAGES = True #
    FAILED_PAGE_DIR = f'{OUT_SUBDIR}/failed-pages'
    SHOULD_CLEAR_FAILED_PAGES = True
    SHOULD_CLEAR_WORDS_IN_DB = False #
    SHOULD_INSERT_WORDS_TO_DB = False #
    # NUM_PAGES_TO_SKIP = 403071
    NUM_PAGES_TO_SKIP = 500
    # NUM_PAGES_TO_PARSE = 10000000
    NUM_PAGES_TO_PARSE = 1000
    TARGET_WORDS = []
    # TARGET_WORDS = ['said', 'evening', 'shop']
    # ----- end controls -----

    startTimer()

    initDir(OUT_SUBDIR, shouldDeleteIfExisting=False)
    if SHOULD_CLEAR_REPORT_FILES:
        initDir(REPORT_DIR)
    if SHOULD_CLEAR_MEDIAWIKI_PAGES:
        initDir(MEDIAWIKI_PAGE_DIR)
    if SHOULD_CLEAR_NONSMELL_PAGES:
        initDir(NONSMELL_PAGE_DIR)
    if SHOULD_CLEAR_HTML_PAGES:
        initDir(HTML_PAGE_DIR)
    if SHOULD_CLEAR_FAILED_PAGES:
        initDir(FAILED_PAGE_DIR)

    wikiDump = mwxml.Dump.from_file(open(DUMP_PATH, encoding='utf-8'))

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
            if SHOULD_WRITE_NONSMELL_PAGES:
                writeFile(NONSMELL_PAGE_DIR, pageFileName + '.txt', text or '', shouldPrint=False)
            continue

        if SHOULD_WRITE_MEDIAWIKI_PAGES:
            writeFile(MEDIAWIKI_PAGE_DIR, pageFileName + '.txt', text or '', shouldPrint=False)

        text = escapeTroublesomeCharacters(text)
        try:
            html = wiki2html(text, False)
            if SHOULD_WRITE_HTML_PAGES:
                writeFile(HTML_PAGE_DIR, pageFileName + '.html', html, shouldPrint=False)
            pageIpas = getIpasFromWikiHtml(html)
            if len(pageIpas) == 0:
                pagesWithNoValidEnglishPronuns.append(pageFileName)
                continue
            # TODO having multiple English sections could throw a wrench into the works here.
            # for now, I'm going to assume that all the pageIpas are for the same word (same meaning)
            pageWords = [Word(ipa, pageIndex, page.id, page.title) for ipa in pageIpas]
            print(f'{pageIndex:08d} {page.title}: {len(pageIpas)} IPAs')
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

def escapeTroublesomeCharacters(text):
    text = re.sub(r'<', '&lt;', text)
    text = re.sub(r'\{\{multiple images[\s\S]*?\}\}', '', text)
    return text
    # return re.sub(r'(<nowiki\s*?\/?\s*>|<)', '', text)

def Word(ipa, pageIndex, pageId, pageTitle):
    return { 'pageTitle': pageTitle, 'pageIndex': pageIndex, 'pageId': pageId, 'title':  pageTitle.lower(), **ipa }

def getPageFileName(index, pageId, pageTitle):
    return f'{index:09d}_{pageId}_{slugify(pageTitle, True)}'

def formatWordDataLine(word):
    pageIndex, pageId, pageTitle, title, ipaLine, accents, ipas = [word[k] for k in ('pageIndex', 'pageId', 'pageTitle', 'title', 'ipaLine', 'accents', 'ipas')]
    return f'i {pageIndex} (id {pageId}):  {pageTitle} ({title}):  {pprint.pformat(accents)}:  {pprint.pformat(ipas)}:    {ipaLine}'


main()
