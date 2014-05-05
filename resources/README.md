README
======================================================

OVERVIEW
------------------------------------------------------

WikiCorpus is a small Python script,
designed to randomly concatenate Wikipedia summary paragraphs
into a corpus. As of currently, the script requires
use of the WikiExtractor python script.

WikiExtractor:
	http://medialab.di.unipi.it/wiki/Wikipedia_Extractor

This program is intended to help in validating a topic-evolution
algorithm (TEvA). Currently, it also creates a series of
CSV and Reference files for this purpose, but this function
can be uncommented/removed (class ConvertedWiki).



CONTACT INFO
-------------------------------------------------------

WikiCorpus
* Charles Bean
	* beanchar@msu.edu

TEvA 
* J. Introne
	* jintrone@msu.edu
	

PARAMETERS
--------------------------------------------------------


Corpus Creation Directories

* The root directory in which the bz2 file was unzipped (location of all Wikipedia files)
    * rootdir = "/Volumes/Arthur/WikipediaFiles/extracted"

* Conjoined summaries output directory (Created corpus output directory)
    * condir = "/Users/charlesbean/Code/TEvA/Corpora/Wikipedia/FeaturedArticles/Conjoined"

* Directory for the matching title files (titles for each break)
    * titledir = "/Users/charlesbean/Code/TEvA/Corpora/Wikipedia/FeaturedArticles/Titles"




TEvA Creation Directories

* Corpus rootdirectory
    * tevarootdir = condir

* CSV output directory
    * outdir = "/Users/charlesbean/Code/TEvA/Corpora/Converted/FeaturedWikiArticles/Data/Extracted"

* Reference files output directory
    * refdir = "/Users/charlesbean/Code/TEvA/Corpora/Converted/FeaturedWikiArticles/Data/Ref Files"




Featured Articles Address

* Featured Articles Log WebAddresses
    * featuredList = ["January_2014", "February_2014", "March_2014", "April_2014"]




Specifications (Corpus creation)

* Number of paragraphs per file
    * numParags = 20

* Random selection of summaries [True]
    * randomselect = True

* Minimum number of sentences per paragraph [3]
    * minsentences = 3

* Maximum number of sentences per paragraph [10]
    * maxsentences = 10

* Paragraph separator (for the conjoined output) ["====================\n"]
    * separator = "====================\n"




USE
---------------------------------------------------------

Unix shell:

	> mkdir extracted
	> bzip2 -dc "your wiki dump here" | python WikiExtractor.py -so extracted
	> python Summary_Conjoiner.py

Extracts the document files using WikiExtractor (maintains the section titles) and
places them in *~/extracted*, then uses *Summary_Conjoiner.py* to pull and concatenate the
summaries. A reference file is also created, for topic checking.

**The *-so* specification is NECESSARY**
	
