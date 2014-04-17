README
======================================================

OVERVIEW
------------------------------------------------------

WikiSummaryConjoiner is a small Python script,
designed to randomly concatenate Wikipedia summary paragraphs
into a text file. As of currently, the script requires
use of the WikiExtractor python script. In the future, it
may pull directly from HTML.

WikiExtractor:
	http://medialab.di.unipi.it/wiki/Wikipedia_Extractor

This program is intended to help in validating a topic-evolution
algorithm (TEvA).



CONTACT INFO
-------------------------------------------------------

WikiSummaryConjoiner
* Charles Bean
	* beanchar@msu.edu

TEvA 
* J. Introne
	* jintrone@msu.edu
	

PARAMETERS
--------------------------------------------------------

*The root directory in which the bz2 file was unzipped*
* rootdir = "/Users/charlesbean/Code/WikiSummaryConjoiner/extracted"

*Out file*
* out_filename = "summaries.txt"

*Reference file*
* ref_filename = "ref.txt"

*Number of total summary paragraphs concatenated [30]*
* num_parags = 5

*Maximum number of summary paragraphs pulled per article [2]*
* num_summaries = 2

*Minimum number of sentences per paragraph [2]*
* minsentences = 3

*Maximum number of sentences per paragraph [10]*
* maxsentences = 10

*Random selection of summaries [True]*
* randomselect = True

*Random selection of articles (from dictionary) [False]*
* randomart = False

*Random selection of file (affects the order of the list of files, not currently useful) [False]*
* randomfile = False


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
	
