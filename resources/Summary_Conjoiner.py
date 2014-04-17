################# Wikipedia Summary Conjoiner ##################
## Charles Bean
## 1/4/14
## For use with the Wikipedia Extractor (http://medialab.di.unipi.it/wiki/Wikipedia_Extractor)
##
## Extracts the summaries from wikipedia XML dumps via WikiExtractor, and conjoins them into one text file.
## Must keep the section headers to work (the -s option in WikiExtractor), as each file contains multiple articles.
##
#################################################################

""" Unzip command below places all extracted articles in folder named "extracted", in default directory of script. """

########################### Use #################################


"""
    > mkdir extracted
    > bzip2 -dc (wiki dump here) | python WikiExtractor.py -so extracted
    > python Summary_Conjoiner.py

"""

from types import *
import os
import sys
import getopt
import string
from random import choice, shuffle

####################### Fixes Required ###########################

# Abreviations cause improper sentences splits ( no carriage returns, so split at periods)
# Need to change parameters mid-run
# Error checking <-----
# Output filesize checking, etc.
# Required number of files checking (for the number of paragraphs requested)
# Finish commenting


######################### Parameters #############################



## Directories ##

# The root directory in which the bz2 file was unzipped
rootdir = "/Users/charlesbean/Code/TEvA/WikiSummaryConjoiner/extracted"

# Out file
out_filename = "summaries.txt"

# Reference file
ref_filename = "ref.txt"

# Random selection of file (affects the order of the list of files, not currently useful) [False]
randomfile = False

# Number of total summary paragraphs concatenated [100]
num_parags = 100




## Articles ##

# Random selection of articles (from dictionary)[True]
randomart = True




## Summaries ##

# Maximum number of summary paragraphs pulled per article [3]
num_summaries = 3

# Random selection of summaries [True]
randomselect = True




## Paragraphs ##

# Minimum number of sentences per paragraph[4]
minsentences = 4

# Maximum number of sentences per paragraph[10]
maxsentences = 10

# Paragraph separator
separator = "\n====================\n"




####################################################################



class Summaries(object):

    def __init__ (self):
        self.filename_set = []      #Set of filenames (strings)
        self.articles_list = []     #Resetting article list
        self.article_titles = []    #List of the titles of articles, for use with dict
        self.summaries = []         #Summary list
        self.articles_dict = {}     #Dictionary of {Titles:Summaries}
        self.chosen_file = ""       #Current file
        self.final_string = ""      #Final string of summaries
        self.ref_string = ""        #Reference string
        self.summary_count = 0      #Number of summaries (counted)


    def __directory_check__(self, rootdir):
        """ Algorithm:
                1. Used for error checking
                2. Iterates through folders/files in directory, prints out
        """
        print "\n==========================\nDirectory: %s\nFiles taken:\n" % rootdir
        article_count = 0
        for subdir, dirs, files in os.walk(rootdir):
                for file in files:
                    if file != ".DS_Store":
                        print " " + subdir + "/" + file
                        article_count += 1
        print "\nNumber of files: %s \n==========================\n" % article_count


    def create_filenames_list(self, rootdir):
        """ Algorithm:
                1. Iterates through each directory and its subsequent subdirectory
                2. Stores the files in a list object
        """
        for subdir, dirs, files in os.walk(rootdir):
            for file in files:
                if file != ".DS_Store":
                    self.filename_set.append(subdir + "/" + file)


    def add_summary_to_dict(self):
        """ Algorithm:
                1. Remove first index (whitespace)
                2. Iterate through the list of articles (complete articles, not just titles)
                3.
        """
        self.articles_list.pop(0) #Removing the whitespace caused by previous split
        for article in self.articles_list:

            #Further splitting of article to eliminate first line and Title
            art_spl = article.split('\n\n')
            title = art_spl[0].split('\n')[1]   #Storing Title
            art_spl.pop(0)                      #Removing article Title

            #Splitting to extract summary
            summary = art_spl[0].split('<h2>')[0]
            para_list = summary.splitlines()  #List of paragraphs in summary of article

            #Iterating through paragraphs to check line length, if ok, adds. Keeps count
            for paragraph in para_list:
                sentences = paragraph.split('. ')
                sentences.pop(-1)  #Removing whitespace at end
                if (len(sentences) >= minsentences) and (len(sentences) <= maxsentences): #minsections/maxsections checking

                    #Adding to dictionary
                    if not title in self.articles_dict:
                        self.articles_dict[title] = [paragraph]
                        self.article_titles.append(title)
                    else:
                        self.articles_dict[title].append(paragraph)
                        self.article_titles.append(title)
                    para_list.remove(paragraph)


    def select_summaries(self):
        while (self.summary_count < num_parags) and self.articles_dict:
            if randomart:
                title = choice(self.article_titles)
            else:
                title = self.article_titles[0]
            print title

            count_sum = 0
            while count_sum < num_summaries and self.articles_dict[title] and self.summary_count < num_parags:
                if randomselect:
                    summary = choice(self.articles_dict[title])
                else:
                    summary = self.articles_dict[title][0]

                self.summaries.append((summary, title))
                count_sum += 1
                self.summary_count += 1
                self.articles_dict[title].remove(summary)

            print "--%s summary/summaries taken" % (count_sum+1)

        shuffle(self.summaries)
        print "\nTotal summaries taken: %s \n========================== \n" % self.summary_count

    def concatenate(self):
        for tuple in self.summaries:
            #Creating reference string
            self.ref_string += "Paragraph %s: %s \n" % (self.summaries.index(tuple) + 1, tuple[1])

            #Creating final string
            self.final_string += tuple[0] + separator


    def create_summaries_dict(self):
        """ Algorithm:
            1. Creates a list of summaries
        """
        with open(self.chosen_file, "r") as open_file:
            opf_str = open_file.read()
            self.articles_list = opf_str.split('<doc id=')
            self.add_summary_to_dict()


    def file_selector(self):
        """ Algorithm:
            1. While-loop
            2. Chooses index
            3. Creates list of summaries from articles in file
            4. Removes the index from the list (self.filename_set)
        """
        print ("Thinking... \n")
        for filename in self.filename_set:
            self.chosen_file = filename
            self.create_summaries_dict()
            self.filename_set.remove(self.chosen_file)


    def write_to_file(self, outfile):
        """ Algorithm:
            1. Opens outfile with param
            2. Writes the final string of all summary paragraphs to file
        """
        out_file = open(outfile, "w")
        out_file.write(self.final_string)
        ref_file = open(ref_filename, "w")
        ref_file.write(self.ref_string)
        out_file.close()
        ref_file.close()



def show_help():
    init_msg = """
    * For use in combining paragraphs of parsed Wikipedia dump
    files. Currently conjoins the summaries of different Wiki pages
    into one text file. *

    COMMANDS
    ----------
    'q' - quit
    'h' - help
    'c' - create text of summaries
    'p' - change parameters (incomplete)

    """
    print (init_msg)

def show_params():
    para_msg = """

    PARAMETER OPTIONS
    ----------
    'q' - exit parameter options
    'r' - root directory for the unzipped files
    'x' - reference filename
    'o' - out filename
    'p' - total number of paragraphs
    's' - number of summaries taken per article
    'min' - minimum number of sentences per summary
    'max' - maximum number of sentences per summary
    'ra' - random selection of articles (boolean)
    'rs' - random selection of summaries (boolean)

    """
    print para_msg


def get_input():
    summaries = Summaries()
    while True:
        usr_inpt = raw_input(">>")
        if (usr_inpt == "q"):
            break
        elif (usr_inpt == "h"):
            show_help()
        elif (usr_inpt == "c"):
            summaries = Summaries()
            summaries.create_filenames_list(rootdir)
            summaries.__directory_check__(rootdir)
            summaries.file_selector()
            summaries.select_summaries()
            summaries.concatenate()
            summaries.write_to_file(out_filename)
        elif (usr_inpt == "p"):
            show_params()
            #summary changer
        elif (usr_inpt == "dc"):
            summaries.__directory_check__(rootdir)
        else:
            print ("Please give a valid input.")


def main():
    show_help()
    get_input()

if __name__ == '__main__':
    main()
