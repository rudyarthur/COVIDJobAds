import re
import sys
import glob
import json
import logging
import string
import gensim
from zipfile import ZipFile
import nltk
from nltk.corpus import stopwords
from collections import Counter

cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});'); ##issues with spaces
tokenizer = nltk.RegexpTokenizer(r'[a-z]+')
lemmatizer = nltk.WordNetLemmatizer()


stopwords = set([
'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 
'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', "it's", 'its', 'itself', 
'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 
'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 
'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 
'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off',
 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 
 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 
 'very', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'll','re', 've', 'ain', 'aren', "aren't", 
 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 
 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', 
 "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't",
 'candidate', 'available', 'ideal', 'apply', 'applicant', 'position', 'per', 'annum', 'required', 'require', 'role'
])


def str_or_none(s):
	if s is None: return ""
	return s;

def strip_html(line):
	return re.sub(cleanr, ' ', line.lower().strip() )
		
def tokenise(line):
	#html, lower, alpha only
	tokens = tokenizer.tokenize( re.sub(cleanr, ' ', line.lower().strip() ) ); #.translate(str.maketrans('', '', string.punctuation)) )
	tokens = [ lemmatizer.lemmatize(token) for token in tokens if (len(token) > 1 and token not in stopwords) ]
	return tokens

	
	
def ngram(words, n):
	if len(words) >= n:
		ngrams = []
		for g in range(0,len(words)-n+1):
			yield  " ".join(words[g:g+n])	

def skipgrams(words, skips=2, ngrams=4):
	
	for n in range(ngrams,1,-1):
		for ng in ngram(words,n):
			yield (0,n,ng)
	
	lw = len(words)
	for skip in range(1,skips+1):
		for n in range(ngrams,1,-1):
			if lw >= n + skip:
				for s in range(lw-skip+1):
					swords = words[:s] + words[s+skip:]
					for ng in ngram(swords,n):
						yield (skip,n,ng)
						
def clean_title(t, common_jobs):

	t = re.sub( r'[-/\\\:]', " ", t.strip().lower()	)	

	if t in common_jobs:
		return ("exact", t)

	words = t.split()
	for s, n, name in skipgrams(words, skips=3, ngrams=4):
		if name in common_jobs:
			return ("{}-{}gram".format(s,n), name)

	for w in words:
		if w in common_jobs:
			return ("0-1gram", w)
		
	return ("unique", t)

