# INFO run this file to just count the number of pages in the dump. Assumes that each page has exactly one revision

import mwxml
import os
import time
from mediawiki import *

dump = mwxml.Dump.from_file(open("C:\\Users\\ben\\Downloads\\enwiktionary-20220701-pages-meta-current.xml", encoding='utf-8'))

def writeListToDataFile(list, filename):
    DATA_DIR = './data'
    path = os.path.join(DATA_DIR, filename)
    data = ''.join(f'{i}\n' for i in list)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)
    print(f'finished writing data to {filename}')

def main():
    startTime = time.perf_counter()
    print(f'start time: {startTime}')

    pageCount = 0
    pagesWithNotOneRevision = []
    for page in dump.pages:
        revCount = 0
        for revision in page:
            revCount += 1
        if (revCount != 1):
            print(f'Got a page with not one revision: {page.title}')
            pagesWithNotOneRevision.append(f'{pageCount}: {page.title}')
        pageCount += 1
        if (pageCount % 1000 == 0): print(f'current page count: {pageCount}')

    print(f'\ndone processing {pageCount} pages')
    print(f'pages with not one revision: {len(pagesWithNotOneRevision)}')
    endTime = time.perf_counter()
    print(f'start time: {startTime}')
    print(f'end time: {endTime}')
    print(f'elapsed: {endTime - startTime} sec')

    print(pagesWithNotOneRevision)
    if len(pagesWithNotOneRevision) > 0:
        writeListToDataFile(pagesWithNotOneRevision, 'pagesWithNotOneRevision.txt')

main()