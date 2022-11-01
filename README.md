# WikiSearchEngine
Search Engine on Wikipedia dump.\
\
Developed the command line based search engine on entire Wikipedia English dump which is around 92GB using the external merge sort and multi-level indexing with query time less than 5 seconds which supports text and fields. Retrieved results are ranked by calculating tf-idf scores.

## Indexing:
+ Parsing: SAX Parser is used to parse the XML corpus.
+ Casefolding: Converting Upper Case to Lower Case.
+ Tokenisation: It is done using regex.
+ Stop Word Removal: Stop words are removed by referring to the stop word list returned by nltk.
+ Stemming: A python library PyStemmer is used for this purpose.
+ Creating various index files with word to field postings.

## Searching:
+ The query given is parsed, processed and given to the respective query handler(simple or field).
+ One by one word is searched in vocabulary and the file number is noted.
+ The respective field files are opened and the document ids along with the frequencies are noted.
+ The documents are ranked on the basis of TF-IDF scores.
+ The title of the documents are extracted using title.txt

## Files Produced:
Output folder contains the following output after Indexing.
 * indexId.txt \
 » This file is created for every 5000 files parsed and stored. These files are deleted after merging the index files.
 * finalIndexId.txt \
 » This file is created after parsing all the docs completed and k way merge done.
 * titles.txt \
 »  This file contains all the titles and assigned doc_id’s in each line.
 * title_offset.txt \
 » This contains file pointers for the titles in titles.txt
 * secondary_index.txt \
 » This contains the secondary index, meaning finalIndex doc_id and start word and last word of every finalIndex.txt
 * stat.txt \
 »  This contains the stats of index created, which will be used by search.py in the searching phase.
 
## Format Of Final Index Created:
Eg: school:5426t2b3i1c4l3r1;4578t3b2l4r2; and so on…
Here school is the word indexed and it has been occurred in two docs with id’s 5426 and 4578 with there count in doc 5426 is 14(2 in title, 3 in body, 1 in infobox, 4 in category, 3 in links and 1 in reference) and similarly in the next doc also. \
indexer.py and search.py are the only code files

## To run the code:
1.create a folder named 'output' in the pwd folder. \
2. command for Indexing creation and merging: \
 »  ```python "./indexer.py" "data.xml"```
3.command for Searching from a text file with queries: \
 »  ```python "./search.py" "queries.txt"```
queries_output.txt file is created in the output folder only in specified format which includes search time.
