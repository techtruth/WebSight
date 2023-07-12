#!/usr/bin/python3
###
# Analyze the internet!
#   - Crawl the internet and save data locally
#   - Condense crawled data into Top2Vec vectors
#   - Train SOM net on document vectors
###


import sys, getopt
from crawl import crawl
from train import train_top2vec, train_somoclu

url_file = ''

#Process command line args
opts, args = getopt.getopt(sys.argv[1:],"hu:o:",["urlfile=","outfile="])
for opt, arg in opts:
      if opt == '-h':
         print ('You have been helped!')
         sys.exit()
      elif opt in ("-u", "--urlfile"):
         url_file = arg
      elif opt in ("-o", "--outfile"):
         outputfile = arg


#crawled_data = crawl(url_file) #Collect content from webpages
crawled_data = crawl(None) #Collect content from cache
train_top2vec(crawled_data) #Train and save a Top2Vec model

train_somoclu("input.somoclu.names", "input.somoclu.docvec.lrn") #Train somoclu on top2vec document vectors

