__author__ = 'charlesbean'

################# Wikipedia Summary Conjoiner ##################
## Charles Bean
## 1/4/14
## For use with the Wikipedia Extractor (http://medialab.di.unipi.it/wiki/Wikipedia_Extractor)
##
## Extracts the summaries from wikipedia XML dumps via WikiExtractor, and conjoins them into one text file.
## Must keep the section headers to work (the -s option in WikiExtractor), as each file contains multiple articles.
##
#################################################################

"""
-----> PLEASE READ!!!

    Please run with Python 2.7.

    Be sure to see Note #2 !!!!!!! <----

    This script does two things:

        It creates a specifiable corpus of Wikipedia summary paragraphs. (Class Summaries)*

        It converts these corpus files into TEvA applicable CSV and Reference files. (Class ConvertedWiki)**

    Details:
        * It takes a series of desired articles from Wikipedia Featured Aritcles (log) web-addresses (subclass of
            FeaturedArticles), and searches the english dump for the matching summaries. It then creates a set of files,
            that are composed of miscellaneous paragraphs from the summaries in a random order.

        ** These files are converted into CSV and reference files.
                - CSV files are marked by [id, replyTo, start, author, data], that can be used to test the
                    Topic Evolution Algorithm (TEvA).
                - Ref files are marked with either a "0" or "1" per line, with a "0" denoting no topic break, and "1"
                    denoting a change in topic. A "1" at line (x) thus indicates a change in topic from line (x) of the
                    CSV file, to line (x + 1).

    Notes:

        1) You can create a custom corpus of articles by commenting out the call (self.artInstance.pullFromHTML) from
            Summaries::initialize(), and then typing the article titles into FeaturedArticles::self.desiredArticles.
            End result should look like:

                        self.desiredArticles = ["Title1", "Title2", "Title3", ...]

        2) By default, the script overwrites files, so if you wish to use more paragraphs per file on a second
            run-through (or simply use fewer articles), be sure to clean the directories (Conjoined and Titles,
            Extracted and Ref Files) of all files, so you don't have repeats. (It's best to CLEAN ALL DIRECTORIES
            before running again.)

        3) Also, if you want to run only a certain class, make sure only its instance is uncommented from the main()
            function.

"""


########################### Usage ################################


'''
From Terminal (OSX):

    > mkdir extracted
    > bzip2 -dc (wiki dump here) | python WikiExtractor.py -so extracted
    > python WikitoCSV.py

'''

###################################################################


from types import *
import time
import os
import sys
import getopt
import string
import urllib
import urllib2
import re
import random
from urllib2 import Request
from random import choice, shuffle


######################### Parameters #############################

### Corpus Creation Directories ###

# The root directory in which the bz2 file was unzipped (location of all Wikipedia files)
rootdir = "/Volumes/Arthur/WikipediaFiles/extracted"    # testing - "/Users/charlesbean/Code/TEvA/Corpora/Testbed"

#Conjoined summaries output directory (Created corpus output directory)
condir = "/Users/charlesbean/Code/TEvA/Corpora/Wikipedia/FeaturedArticles/Conjoined"

#Directory for the matching title files (titles for each break)
titledir = "/Users/charlesbean/Code/TEvA/Corpora/Wikipedia/FeaturedArticles/Titles"





### TEvA Creation Directories ###

#Corpus rootdirectory
tevarootdir = condir

#CSV output directory
outdir = "/Users/charlesbean/Code/TEvA/Corpora/Converted/FeaturedWikiArticles/Data/Extracted"

#Reference files output directory
refdir = "/Users/charlesbean/Code/TEvA/Corpora/Converted/FeaturedWikiArticles/Data/Ref Files"





### Featured Articles Address ###

## Featured Articles Log WebAddresses ##
featuredList = ["January_2014", "February_2014", "March_2014", "April_2014"]





### Specifications (Corpus creation) ###

# Number of paragraphs per file
numParags = 20

# Random selection of summaries [True]
randomselect = True

# Minimum number of sentences per paragraph [3]
minsentences = 3

# Maximum number of sentences per paragraph [10]
maxsentences = 10

# Paragraph separator (for the conjoined output)
separator = "====================\n"





####################################################################



class FeaturedArticles(object):
    """
        Pulls raw HTML data from the Featured Articles Log web address, and puts the article names into a list
    """
    def __init__(self):
        self.desiredArticles = []

    def pullFromHTML(self):
        """
            Pulls the list of article names from the "Content" section of the Featured Article Log page.
        """

        for article in featuredList:

            address = "http://en.wikipedia.org/wiki/Wikipedia:Featured_article_candidates/Featured_log/" + article

            #Open the URL and read
            try:
                response = urllib2.urlopen(address)
                html = response.read()
            except (urllib2.HTTPError, urllib2.URLError, IOError):
                print "Oops! URL/HTTP/IO error for address %s" % address
                raise


            #Split the URL to get the "CONTENT" section, then split that section by newlines
            lines = html.split("div id=\"toctitle\">")[1].split("<div class=")[0].split("\n") #Separate the content section


            # Match based on: <li class="toclevel-1"><a href="#Are_You_Experienced"><span class="tocnumber">10
            #                       </span> <span class="toctext"><i>Are You Experienced</i></span></a>
            # Optional <i> and </i>
            regex = re.compile("(?:<li class=\"toclevel-1\">.*<span class=\"toctext\">(?:<i>)?)(?P<title>.*?)(?:</i>)?(?:</span></a>.*)+")

            count = 0

            #Search each line for above regular expression; if found, add to list
            for item in lines:
                match = regex.search(item)

                #If there is a title in the line, append it to the list
                if match:
                    count += 1
                    self.desiredArticles.append(match.group("title"))


            #List length
            print "\tNumber of featured articles taken from %s: %d\n" % (address, count)

        print "\t\tTotal number of featured articles taken: %d\n" % len(self.desiredArticles)

        return self.desiredArticles


class Summaries(FeaturedArticles):
    """
        Inherits Articles.
        Finds the summaries from the desired articles, puts in a dictionary, and then writes to files.
    """
    def __init__(self):
        super(FeaturedArticles, self).__init__()
        self.artInstance = FeaturedArticles() #Desired articles - instance
        self.fileMap = {} # {File: {title: [summary paragraphs]}}
        self.fileCount = 0
        self.paragraphCount = 0

    def meetsCriteria(self, paragraph):

        sentenceRegex = re.compile("([A-Z][^\.!?]*[\.!?])") # Split by sentences

        numberSentences = len(sentenceRegex.findall(paragraph))

        if (numberSentences >= minsentences) and (numberSentences <= maxsentences):
            return True
        else:
            return False

    def writeFiles(self, outString, refString, filename):
        """ Algorithm:
            1. Opens outfile with param
            2. Writes the final string of all summary paragraphs to file
        """

        outFilename = condir + "/" + filename + ".con"
        refFilename = titledir + "/" + filename + ".titles"


        try:
            outFile = open(outFilename, "w")
            outFile.write(outString)
            refFile = open(refFilename, "w")
            refFile.write(refString)
            outFile.close()
            refFile.close()
        except:
            print "Failed to write files - %s\n" % filename

    def addToDictionary(self, key, value, dictionary):

        print "\t\t\t\tAdding title and summary to dictionary."

        if not key in dictionary:
            dictionary[key] = value
        else:
            try:
                dictionary[key].append(value)
            except (AttributeError):
                pass
            try:
                dictionary[key].update(value)
            except:
                print "********** Couldn't update dictionary for key %s **********" % key

    def getSummary(self, fileStream, title, filename):

        print "\t\tGetting summary for title - %s" % title

        finalParagraphs = []

        # Title included "(?:<doc id=.*title=\"TITLE.*\n.*\n\n)((.+\n)+?)(?:<h2>.*)"
        regex = "(?:<doc id=.*title=\"" + re.escape(title) + ".*\n.*\n\n)((.+\n)+?)(?:<h2>.*)"

        #FINDING SUMMARY
        try:
            matches = re.findall(regex, fileStream) # Find summary for passed title in file (returns list)

            for item in matches:

                #Splitting summary into paragraphs
                origParagraphs = item[0].split('\n')[:-1]

                #Checking parahgraph sentence length
                for paragraph in origParagraphs:
                    if self.meetsCriteria(paragraph):
                        finalParagraphs.append(paragraph)

                print "\t\t\tNumber of acceptable summary paragraphs - %d" % len(finalParagraphs)

                self.paragraphCount += len(finalParagraphs)

                #Adding the the list of summary paragraphs to below dictionaries
                if finalParagraphs:
                    self.addToDictionary(filename, {title: finalParagraphs}, self.fileMap)
                else:
                    print "\t\t\t\t** Paragraphs do not meet desired length. No paragraphs selected. **"

        except:
            print "Summary could not be found for %s, in file - %s" % (title, filename)

    def searchFile(self, filepath, filename):

        with open(filepath, "r") as WikiFile:

            fileStream = WikiFile.read()

            #FINDING TITLES
            try:
                matches = re.findall("(?:title=\"(?P<title>.*?)\">)", fileStream, re.DOTALL)

                for title in matches:

                    #If found title is in desired Articles, get it's summary
                    if title in self.artInstance.desiredArticles:
                        self.fileCount += 1

                        print "File count - %d" % self.fileCount
                        print "\tTitle found in file - %s" % filepath

                        self.getSummary(fileStream, title, filename)




            except:
                print "No titles found in - %s\n" % filename

            WikiFile.close()

    def selection(self, dictionary):
        """
            Returns list of chosen [file, title, paragraph]
        """
        while dictionary:
            if randomselect:
                selectedFile = choice(dictionary.keys())

                #If selected files value is empty - delete; else, select title
                if not dictionary[selectedFile]:
                    dictionary.pop(selectedFile, None)
                    continue
                else:
                    selectedTitle = choice(dictionary[selectedFile].keys())

                    #If selected titles value is empty - delete; else, select paragraph
                    if not dictionary[selectedFile][selectedTitle]:
                        dictionary[selectedFile].pop(selectedTitle, None)
                        continue
                    else:
                        selectedParagraph = choice(dictionary[selectedFile][selectedTitle])
                        dictionary[selectedFile][selectedTitle].remove(selectedParagraph)
                        return [selectedFile, selectedTitle, selectedParagraph]

            else:
                selectedFile = dictionary[0]

                #If value is empty...
                if not dictionary[selectedFile]:
                    dictionary.pop(selectedFile, None)
                    continue
                else:
                    selectedTitle = dictionary[selectedFile][0]

                    if not dictionary[selectedFile][selectedTitle]:
                        dictionary[selectedFile].pop(selectedTitle, None)
                        continue
                    else:
                        selectedParagraph = dictionary[selectedFile][selectedTitle][0]
                        dictionary[selectedFile][selectedTitle].remove(selectedParagraph)
                        return [selectedFile, selectedTitle, selectedParagraph]
        else:
            print "\n\n\t********** fileMap EMPTIED **********\n"

    def operate(self):

        print "Writing files from dictionary"

        count = 0 #Paragraph write count
        filenumber = 0
        outString = ""
        refString = ""

        sentenceRegex = re.compile("([A-Z][^\.!?]*[\.!?])") # Split by sentences

        while (self.fileMap):
            info = self.selection(self.fileMap)
            filename = str(filenumber) + "-Wiki"

            if info:
                #print info[1] #print title

                sentences = sentenceRegex.findall(info[2])

                if (count < numParags):

                    for sentence in sentences:
                        outString += sentence + "\n"

                    refString += info[1] + "\n"
                    outString += separator
                    count += 1

                    print "\tWriting one paragraph from title %s to file %s" % (info[1], filename)
                    self.writeFiles(outString, refString, filename)

                else:
                    print "\tWriting one paragraph from title %s to file %s" % (info[1], filename)
                    self.writeFiles(outString, refString, filename)

                    count = 0
                    filenumber += 1
                    outString = ""
                    refString = ""

                    ###############

                    for sentence in sentences:
                        outString += sentence + "\n"

                    refString += info[1] + "\n"
                    outString += separator
                    count += 1
                    filename = str(filenumber) + "-Wiki"

                    print "\tWriting one paragraph from title %s to file %s" % (info[1], filename)
                    self.writeFiles(outString, refString, filename)

        print "\tTotal pargraphs taken/written: %d\n" % self.paragraphCount
        print "********** PROCESS COMPLETE **********"

    def initialize(self, rootdir):
        """ Algorithm:
                1. Iterates through each directory and its subsequent subdirectory
        """
        print "Initializing dictionary from rootdirectory - %s\n" % rootdir

        self.artInstance.pullFromHTML() #COMMENT THIS OUT IF YOU WISH TO USE A CUSTOM LIST OF ARTICLES <----

        for subdir, dirs, files in os.walk(rootdir):
            if self.fileCount >= len(self.artInstance.desiredArticles):
                break
            else:
                for file in files:
                    if self.fileCount >= len(self.artInstance.desiredArticles):
                        break
                    else:
                        path = subdir + "/" + file

                        extension = re.compile("wiki.*")
                        isCorrect = extension.search(file)

                        if isCorrect:
                            self.searchFile(path, file)

    def run(self):

        print "\n====================\n\n"

        self.initialize(rootdir) #Create the fileMap ({filename: {title: [summary paragraph 1, summary paragraph 2], ..}, ...}

        self.operate()

        print "\n====================\n\n"


class ConvertedWiki(object):
    """
        Converts the conjoined summary files (corpus) into usable CSV and .ref files for TEvA.
    """

    def __init__(self):
        self.file = ""

    def __directory_check__(self, tevarootdir):
        """ Algorithm:
                1. Used for error checking
                2. Iterates through folders/files in directory, prints out
        """
        print "Creating TEvA data.\n\n==========================\nDirectory: %s\nFiles taken:\n" % tevarootdir
        article_count = 0
        for subdir, dirs, files in os.walk(tevarootdir):
            for file in files:
                if file != ".DS_Store":
                    print " " + subdir + "/" + file
                    article_count += 1
        print "\nNumber of files: %s \n==========================\n" % article_count

    def iterate(self):

        print "\tProcessing files into CSV and Reference files.."

        for subdir, dirs, files in os.walk(tevarootdir):
            for file in files:
                if file != ".DS_Store":
                    self.file = subdir + "/" + file
                    self.process(outdir + "/" + file + ".csv", refdir + "/" + file + ".ref")


        print "\tProcessing complete. \n\n==========================\n"

    def process(self, outFilename, refFilename):

        id = 0
        replyTo = -1
        start = 5 #Seconds
        author = "chucknorris"

        refFile = open(refFilename, "w")

        outFile = open(outFilename, "w")
        outFile.write("id\treplyTo\tstart\tauthor\ttext\n")

        with open(self.file, "r") as open_file:
            for line in open_file:
                if line != separator:
                    if (replyTo == -1):
                        text = str(id) + '\t' + "" + '\t' + str(start) + '\t' + author + '\t' + line
                        id += 1
                        replyTo += 1
                        start += 5


                        outFile.write(text)
                        refFile.write(str(0) + '\n')
                    else:
                        text = str(id) + '\t' + str(replyTo) + '\t' + str(start) + '\t' + author + '\t' + line
                        id += 1
                        replyTo += 1
                        start += 5


                        outFile.write(text)
                        refFile.write(str(0) + '\n')

                else:
                    refFile.write(str(1) + '\n')

        refFile.close()
        outFile.close()

def main():
    createCorpus = Summaries()
    createCorpus.run()

    TevaCorpus = ConvertedWiki()
    TevaCorpus.__directory_check__(tevarootdir)
    TevaCorpus.iterate()



if __name__ == '__main__':
    main()
