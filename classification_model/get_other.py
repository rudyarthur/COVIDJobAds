import re
import sys
import glob
import json
import logging
import string
import gensim
from zipfile import ZipFile
from collections import Counter
import numpy as np

from clean import *
from gensim.models import Phrases
from gensim import corpora
from gensim.models import TfidfModel
from six import iteritems
from gensim.similarities import Similarity

import matplotlib.pyplot as plt

def docs(fname=False):
	with open("seeds.txt", 'r') as infile:
		for i,line in enumerate(infile):
			ls = line.split()			
			if fname:
				yield ls[0], ls[1], ls[2], ls[3:]; 
			else:
				yield ls[3:]; 
	return 
	
##make dict
dictionary = corpora.Dictionary()
for d in docs(): dictionary.add_documents([d])
# remove  words that appear <= 3
dictionary.filter_tokens([tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq <= 1])  
# Filter out words that occur less than X documents, or more than 50% of the documents.
dictionary.filter_extremes(no_below=1, no_above=0.5)
dictionary.compactify()  # remove gaps in id sequence after words that were removed
dictionary.save('seed.dict')  # store the dictionary, for future reference
len_dict = len(dictionary)
print(len_dict, "unique tokens")
	
##tfidf
class MyCorpus(object):
	def __iter__(self):
		with open("seeds.txt", 'r') as infile:
			for i,line in enumerate(infile):			
				yield dictionary.doc2bow( line.split()[3:] ); 
		return 

print("Training tfidf model")
corpus_memory_friendly = MyCorpus()  # doesn't load the corpus into memory!           	
model = TfidfModel(corpus_memory_friendly)
model.save("seed.model")

#similarity
sectors = ['graduate', 'marketing', 'buyer', 'retail', 'surveyor', 'assistant', 'physio', 'construction', 'electrician', 
'plumber', 'security', 
'hr', 'vehicle', 'recruitment', 
'solicitor', 'project', 'storemanager', 'customer', 'garage', 'sale', 'property', 'teacher', 'nursery', 'nurse', 'care', 'software', 
'engineer', 
'data', 'delivery', 'warehouse', 'hotel', 'cleaner', 'server', 'kitchen', 'support', 'hgv', 'production', 'machine',
'productionmanager', 
'accountant', 
'finance', 'account', 
'receptionist', 'business', 'administrator', 'welsh']
sim_topic = {}
topic_files = set([])
print("Calculating Similarity Objects")
for sector in sectors:
	seedcorpus = []
	with open("seeds.txt", 'r') as infile:
			for i,line in enumerate(infile):			
				ls = line.split();
				if sector == ls[1]:
					seedcorpus.append( dictionary.doc2bow( ls[3:] ) ); 
					topic_files.add(ls[0])

	sim_topic[sector] = Similarity('sim.' + sector, model[seedcorpus], len_dict)
	#index.save('tfidf.' + sector + '.index')

print("Computing Similarities")
vals = []
others = []	
zip_file = ZipFile("/path/to/data.zip")
for k,f in enumerate(zip_file.namelist()):
	if k % 100 == 0: print(k)			
	with zip_file.open(f) as infile:  
		if f.split(".")[-1] != "json": continue;
		if f in topic_files: continue; ##in the seed set!
		js = infile.read().decode('utf8')
		job = json.loads(js)
		if 'jobTitle' in job and job['jobTitle'] is not None:
			clean_doc = tokenise(job['jobTitle']  + " " +  str_or_none(job['jobDescription']))
			docbow = dictionary.doc2bow( clean_doc )
			tfidf_vec = model[docbow]
			
			max_val = -np.inf				
			max_sector = None
			for sector in sectors:
				sims = sim_topic[sector][ tfidf_vec ]
				msims = np.mean(sims)
				if msims > max_val: 
					max_val = msims;		
					max_sector = sector;
			vals.append(max_val)
			#print(max_val, job['jobTitle'] )
			if max_val < 0.04:
				others.append( f + " other " + "_".join(tokenise(job['jobTitle'])) + " " + " ".join(clean_doc) + "\n" )

print(min(vals), max(vals), np.median(vals), np.mean(vals), sorted(vals)[ int(0.95*len(vals) ) ], sorted(vals)[ int(0.05*len(vals) ) ] )						
plt.hist(vals, bins=100)
plt.show();

print("Appending", len(others), "dissimilar job ads to seeds")
with open("seeds.txt", 'a') as outfile:
	for a in others:
		outfile.write( a );

