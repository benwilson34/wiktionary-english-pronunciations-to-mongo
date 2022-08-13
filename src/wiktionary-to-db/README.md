## Instructions

- Download latest English wiktionary dump, latest revisions only
- Extract using bzip2
- Specify `DUMP_PATH` to extracted file
- Set other controls as desired. It's not recommended to write pages out when you're processing a lot of them.


## TODO

- [x] Install Mongo
- [x] Actually insert data to Mongo database
- [ ] Look into fishy IPAs
- - [ ] Print out English sections from first 1MM pages...check for different formats...
- [x] Investigate failing pages (first 1MM OK)
- [x] Modularize main file
- [ ] Fancy terminal output?
- [ ] Multithreading?


## Worth investigating

- 000000715_1164_acanthocephala - "Translingual" pronun section w IPA; no English.
- 000000998_1722_i.html - existent English pronunciation sections, but IPA is not formatted.


## Rough algo

Givens:
- Database of English words <-> English IPA ("db")
- Block of English text to mangle ("input")
- Options?

Input -> IPA:
- Remove punctuation
- Convert as many words from input as possible via db.
- [eventually] Prompt user for validation, potential choices? i.e. unknown words or heterophones?

IPA mangling:
- [eventually] Preserve certain words? i.e. based on part of speech? To try to maintain some sentence structure?
- [ok now the hard part: how to go from converted IPA back to English words?]
- 
- Need table of "similar" or "mutable" symbols? e.g. "m" can be changed to "n" if needed. Only fall back to those if needed?
- Weight different resolution options?


### Some useful regexes

- \{\{IPA(?!(font|char))
