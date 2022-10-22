# wiktionary-english-pronunciations-to-mongo

This app iterates over pages in a wiktionary (mediawiki) database dump, parses English pronunciations (IPA strings) for words on those pages, and inserts them to a MongoDB database.

It could be adapted to parse more than English sections. It could also be adapted to insert to another database program - even a SQL one as the data is pretty structured.

For only the most recent parsed data, see this repo:
TODO


## Installation

- Install Python 3.10. It might work with earlier versions. Tested with 3.10.4 on Windows 10 Professional.
- Clone the repo.
- Install Python dependencies:
    - `pip install mwxml`
    - `pip install pprint`
    - `pip install pymongo`
    - `pip install more-itertools`
- Install MongoDB locally or change the connection string in [./src/utils/db.py](./src/utils/db.py) to a remote server.
    - MongoDB Compass is recommended for inspecting/querying the data.


## Preparing the database dump file

- Download latest English wiktionary dump, latest revisions only:
    - Go to [this page](https://dumps.wikimedia.org/backup-index.html), search for "enwiktionary", click on that
    - Search for "All pages, current versions only" and download that one
- Install bzip2 if you don't have it already.
- Extract using bzip2. The uncompressed .xml file will be something like 8x the size of the archive, so if the .xml.bz2 file is 1 GB, the extracted .xml file will be about 8 GB. Ensure there is plenty of free storage wherever you are extracting to.
    - `bzip2 -d /path/to/enwiktionary-dump.xml.bz2`
    - The .xml file will be extracted to the same directory as the .xml.bz2 file. You'll need the path to this .xml file in the next step.

### Optional: dry run/count the pages in the dump

The [./src/count-pages.py](./src/count-pages.py) file can be run to see how many pages are in the dump. This count can come in handy when running the main program to see its progress.

`DUMP_XML_PATH` is required and should be the full path to the extracted .xml file.

Run the file. The total page count will be displayed in the console when it is complete. On my machine as of this writing, this takes about 17 minutes to process.


## Main program

The [.wiktionary-to-db.py](.wiktionary-to-db.py) file contains the main parser program.

There are some configuration vars at the top of the `main` function. `DUMP_XML_PATH` is required and should be the full path to the extracted .xml file. The other vars are for debugging and are detailed in the "Debugging configuration" section below.

Run the `wiktionary-to-db.py` file. On my machine as of this writing, it takes about 20 minutes to process 8.35MM wiktionary pages.

At the end of the run, assuming the options were set, a number of report files will be generated. Look at those for more detailed info on what happened during the run. The data will be inserted to the `enwiktionary.pronuns` MongoDB collection.

### Debugging configuration

The other config vars are for debugging purposes. They should not be needed for a typical run, but are useful when figuring out why pronunciations for a particular page were not parsed. They are as follows:

- `NUM_PAGES_TO_SKIP` (int) - how many pages to skip from the beginning of the dump. Useful when the index of a page in question is known.
- `NUM_PAGES_TO_PARSE` (int) - how many pages should be parsed (not counting skipped pages). Set to a number greater than the total number of pages in the dump to parse all pages (default behavior).
- `TARGET_WORDS` (string[]) - if defined, only pages with titles that match one of the strings in this array will be parsed.
- `SHOULD_CLEAR_REPORT_FILES` (Boolean) - when `True`, any existing report files will be deleted on startup.
- `SHOULD_WRITE_MEDIAWIKI_PAGES` (Boolean) - when `True`, the contents of each page will be written out to the "./out/mediawiki" directory.
- `SHOULD_CLEAR_MEDIAWIKI_PAGES` (Boolean) - when `True`, any existing mediawiki pages in "./out/mediawiki" will be deleted on startup.
- `SHOULD_CLEAR_FAILED_PAGES` (Boolean) - when `True`, any existing failed pages in "./out/failed-pages" will be deleted on startup.
- `SHOULD_CLEAR_WORDS_IN_DB` (Boolean) - when `True`, all documents in the target database/collection will be deleted immediately before inserting the parsed data.
- `SHOULD_INSERT_WORDS_TO_DB` (Boolean) - when `True`, parsed data will be inserted to the target database/collection.


## Database structure

There are often multiple documents/rows in the database for any one English word. This is because:

- there might be multiple wiktionary pages with the same title
- there might be multiple words spelled the same way (homonyms)
- the word might have multiple parts of speech
- the word might have multiple accents for its listed pronunciations

One document/row per valid IPA line will be inserted into the database.
The normalized page title (lowercase), accents, and IPAs will be stored, as well as the original page title, page ID, and dump index.

TODO should the documents be flattened by IPA? 

```js
// each document in the collection:
{
    _id <ObjectId>,
    pageTitle <String>,  // the original page title
    pageIndex <Int32>,   // the page's index in the dumpfile
    pageId <Int32>,      // the actual page ID 
    title <String>,      // the normalized page title (lowercase)
    ipaLine <String>,    // the line of text containing one or more IPAs
    accents <String[]>,  // [optional] one or more accents parsed from the ipaLine
    ipas <String[]>      // one or more IPAs parsed from the ipaLine
}
```


## Content warning

There are many obscene and profane words defined on wiktionary which will end up in the dataset produced by this app. You may want to filter those words out, perhaps by using a package like [profanity-check](https://pypi.org/project/profanity-check/) that can detect profanity in a given string.

I take no responsibility for the words defined on wiktionary or included in the dataset.


## Performance

Once the `enwiktionary.pronuns` collection has been populated with data, an index on the `title` field should be created to *greatly* improve lookup times.


## Support/Maintenance

I probably won't be maintaining or updating this project. However, if you've got an question or idea, create an issue or pull request here on Github and I'll take a look.


## License

TODO probably MIT
