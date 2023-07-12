#!/usr/bin/python3
###
# Given a list of URLs,
# scrape and extract content with structure
# and organize it in a doc2vec
# so that it may be fed into somoclu
###

import sys
sys.path.insert(0, 'Top2Vec/top2vec')
#sys.path.insert(1, 'hdbscan/hdbscan')
from top2vec import Top2Vec
import pickle
import math
import asyncio
import aiohttp
from aiohttp.resolver import AsyncResolver
from throttler import Throttler
from bs4 import BeautifulSoup

#Save topic words
topic_words = model.topic_words
with open("words.txt", 'w') as f:
    for tag in range(len(topic_words)):
        line = str(tag) + "\t"
        line += ' '.join([str(dim) for dim in topic_words[tag]])
        f.write(line + '\n')

#Save topic vectors
topic_vectors = model.topic_vectors
with open("input.somoclu.topvec.lrn", 'w') as f:
    f.write("% " + str(len(topic_vectors)) + '\n') #Rows
    f.write("% " + str(len(topic_vectors[0])) + '\n') #Columns
    f.write("% " + "9")
    for i in range(len(topic_vectors[0])):
        f.write(" " + str(1))
    f.write('\n') # Training Mask
    f.write("% " + "Ignore me please!" + '\n') # Variable names (ignored)
    for tag in range(len(topic_vectors)):
        line = str(tag) + "\t"
        line += ' '.join([str(dim) for dim in topic_vectors[tag]])
        f.write(line + '\n')

#Save document vectors
document_vectors = model.document_vectors
print("Finished", document_vectors)

with open("input.somoclu.docvec.lrn", 'w') as f:
    f.write("% " + str(len(document_vectors)) + '\n') #Rows
    f.write("% " + str(len(document_vectors[0])) + '\n') #Columns
    f.write("% " + "9")
    for i in range(len(document_vectors[0])):
        f.write(" " + str(1))
    f.write('\n') # Training Mask
    f.write("% " + "Ignore me please!" + '\n') # Variable names (ignored)
    for tag in range(len(document_vectors)):
        line = str(tag) + "\t"
        line += ' '.join([str(dim) for dim in document_vectors[tag]])
        f.write(line + '\n')

print("Finished")
