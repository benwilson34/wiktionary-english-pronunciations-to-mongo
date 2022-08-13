import re
from bs4 import BeautifulSoup, NavigableString


def doesTextSmellLikeValidPronunciation(text):
    return re.search(r'==(English|Translingual)==[\s\S]*\{\{IPA(?!char)', text) is not None

def getIpasFromWikiHtml(html):
    if len(html) == 0: return []
    soup = BeautifulSoup(html, features='html.parser')
    ipas = []

    for englishSection in soup.find_all(id=['w_english', 'w_translingual']):
        for engSib in englishSection.next_siblings:
            if isinstance(engSib, NavigableString): continue
            if engSib.name == 'h2': break # stop if we hit a top-level heading (another language section)
            if engSib.has_attr('id') and engSib['id'].startswith('w_pronunciation'):
                pronunSection = engSib
                for pronunSib in pronunSection.next_siblings:
                    if isinstance(pronunSib, NavigableString): continue
                    if pronunSib.name and pronunSib.name.startswith('h'): break # stop if we hit another heading
                    # TODO also get the part of speech/other sections?
                    sectionIpas = parseIpasFromElement(pronunSib)
                    ipas.extend(sectionIpas)
    return ipas

def parseIpasFromElement(el):
    ipaData = []
    for ipaElement in el.find_all(string=re.compile(r'\{\{IPA')):
        ipaLine = ipaElement.text.replace('\n', '')
        ipas = getIpas(ipaLine)
        if not ipas: continue
        accents = getAccents(ipaLine)
        ipaData.append({ 'ipaLine': ipaLine, 'accents': accents, 'ipas': ipas })
    return ipaData

def getAccents(ipaLine):
    accentResult = re.search(r'\{\{a\|(.+?)\}\}', ipaLine)
    if accentResult: return accentResult.groups()[0].split('|')
    return None

def getIpas(ipaLine):
    ipasResult = re.search(r'\{\{IPA(-lite)?(?!char)\|(en|mul)\|(.+?)\}\}', ipaLine)
    if not ipasResult: return None
    ipaText = ipasResult.groups()[2]
    ipas = ipaText.split('|')
    return ipas
