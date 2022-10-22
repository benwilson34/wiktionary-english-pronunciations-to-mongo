# Run this file to just count the number of pages in the dump. It also does a sanity check to make sure
# that each page has exactly one revision.

import mwxml

from utils.timer import startTimer, stopTimer

DUMP_XML_PATH = 'C:\\full\\path\\to\\dump.xml' # required

def main():
    dump = mwxml.Dump.from_file(open(DUMP_XML_PATH, encoding='utf-8'))

    startTimer()

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
        if (pageCount % 10000 == 0): print(f'current page count: {pageCount}')

    print(f'\ndone processing {pageCount} pages')
    print(f'pages with not one revision: {len(pagesWithNotOneRevision)}')
    timerReport = stopTimer()
    print(timerReport)

main()