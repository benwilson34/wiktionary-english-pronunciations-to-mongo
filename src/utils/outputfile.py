import os
import re
import shutil
import unicodedata

OUT_DIR = os.path.join(os.getcwd(), 'out')

def initDir(dir, shouldDeleteIfExisting = True):
    dirPath = os.path.join(OUT_DIR, dir)
    if shouldDeleteIfExisting: 
        try:
            shutil.rmtree(dirPath)
        except FileNotFoundError: pass
    try:
        os.mkdir(dirPath)
    except FileExistsError: pass

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

def writeFileFromList(dir, filename, dataList):
    data = ''.join(f'{d}\n' for d in dataList)
    writeFile(dir, filename, data)

def writeFile(dir, filename, data, shouldPrint=True):
    path = os.path.join(OUT_DIR, dir, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)
    if shouldPrint: print(f'finished writing data to {filename}')
