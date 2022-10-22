# see https://simple.wiktionary.org/wiki/Template:IPA
# see https://simple.wiktionary.org/wiki/Template:Audio-IPA

import re
import more_itertools as mit

# Quick heuristic check if the text contains a valid language section and some IPA definition thereafter.
# If a text doesn't smell valid, it's guaranteed not to contain any valid pronuns. If it does smell valid, it needs
# to be investigated further.
def doesTextSmellLikeValidPronunciation(text):
    return re.search(r'==(English|Translingual)==[\s\S]*\{\{(audio-)?IPA(?!char)', text, re.IGNORECASE) is not None

def getPronunsFromMediaWikiText(text):
    pronuns = []

    lineIter = mit.peekable(text.splitlines())
    for textLine in lineIter:
        if re.search(r'^==(English|Translingual)', textLine, re.IGNORECASE) is None: continue
        for sectionLine in lineIter:
            if re.search(r'^==[^=]', sectionLine) is not None: 
                # stop if we hit a top-level heading (another language section)
                lineIter.prepend(sectionLine) # rewind the current line
                break
            # TODO get part of speech, other sections?
            if re.search(r'===Pronunciation', sectionLine, re.IGNORECASE) is None: continue
            blockAccents = None
            for pronunLine in lineIter:
                if pronunLine.startswith('='): 
                    # stop if we hit another heading
                    lineIter.prepend(pronunLine) # rewind the current line
                    break
                
                # handle block accents (pronun subsections with accent "headers")
                maybeAccents = getAccents(pronunLine)
                if pronunLine.startswith('; {{') and maybeAccents:
                    blockAccents = maybeAccents
                if len(pronunLine.strip()) == 0:
                    blockAccents = None

                if re.search(r'\{\{(audio-)?IPA', pronunLine) is None: continue
                ipas = getIpas(pronunLine)
                if not ipas: continue
                accents = blockAccents or maybeAccents
                pronuns.append({ 'pronunLine': pronunLine, 'accents': accents, 'ipas': ipas })
    return pronuns

def getAccents(ipaLine):
    accentResult = re.search(r'\{\{a\|(.+?)\}\}', ipaLine, re.IGNORECASE)
    if accentResult: return accentResult.groups()[0].split('|')
    return None

def getIpas(ipaLine):
    allIpas = []
    for ipasResult in re.findall(r'\{\{(audio-)?IPA(-lite)?(?!char)\|(en|mul)\|(.+?)\}\}', ipaLine, re.IGNORECASE):
        IPAS_GROUP_INDEX = 3
        ipas = ipasResult[IPAS_GROUP_INDEX].split('|')

        # handle special case for audio-API template
        AUDIO_PREFIX_GROUP_INDEX = 0
        if ipasResult[AUDIO_PREFIX_GROUP_INDEX] == 'audio-':
            audioIpaValidIpaIndex = 1
            allIpas.append(ipas[audioIpaValidIpaIndex])
        else:
            allIpas.extend(ipas)
    return allIpas
