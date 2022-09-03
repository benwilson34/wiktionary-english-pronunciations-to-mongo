## Instructions

- Download latest English wiktionary dump, latest revisions only
    - Go to [this page](https://dumps.wikimedia.org/backup-index.html), search for "enwiktionary", click on that
    - Search for "All pages, current versions only" and download that one
- Extract using bzip2
- Specify `DUMP_PATH` to extracted file
- Set other controls as desired. It's not recommended to write pages out when you're processing a lot of them.
- Run the `wiktionary-to-db.py` file. On my machine as of this writing, it takes about 28 minutes to process 8.19MM wiktionary pages.
    - At the end of the run, assuming the options were set, a number of report files will be generated. Look at those for more detailed info on what happened during the run.


## Database structure

One document per valid IPA line will be inserted into the database.
The normalized page title (lowercase), accents, and IPAs will be stored, as well as the original page title, page ID, and dump index.

```js
// each document in butchr.pronunciations collection:
{
    _id <ObjectId>,
    pageTitle <String>,
    pageIndex <Int32>,
    pageId <Int32>,
    title <String>,
    ipaLine <String>,
    accents <Array<String>>,
    ipas <Array<String>>
}
```

An index on the `title` field should be created to *greatly* improve lookup times.
