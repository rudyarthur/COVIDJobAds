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

from clean import *


topics = ['graduate', 'marketing', 'buyer', 'retail', 'surveyor', 'assistant', 'physio', 'construction', 'electrician', 
'plumber', 'security', 'prison',
'hr', 'vehicle', 'recruitment', 
'solicitor', 'project', 'storemanager', 'customer', 'garage', 'sale', 'property', 'teacher', 'nursery', 'nurse', 'care', 
'software', 'itsupport'
'engineer', 
'data', 'delivery', 'warehouse', 'hotel', 'cleaner', 'server', 'kitchen', 'support', 'hgv', 'production', 'machine',
'productionmanager', 
'accountant', 
'finance', 'account', 
'receptionist', 'business', 'administrator', 'charity', 'welsh']
unclassified = Counter()
topiccount = Counter()
word_counter = {};
with open("seeds.txt", 'w') as outfile:
	
	zip_file = ZipFile("/path/to/data.zip")
	for k,f in enumerate(zip_file.namelist()):
		if k % 1000 == 0: print(k);
		with zip_file.open(f) as infile:  
			if f.split(".")[-1] != "json": continue;
			js = infile.read().decode('utf8')
			job = json.loads(js)
			if 'jobTitle' in job and job['jobTitle'] is not None:
				title_tokens = tokenise(job['jobTitle'])
				clean_title = " ".join(title_tokens)
				clean_descr = " ".join(tokenise(job['jobDescription']))
				employer_name = job["employerName"].lower().split() 
				topic = None

					
				if 'graduate' in clean_title:
					topic = 'graduate'
				elif "marketing" in clean_title:
					topic = 'marketing'; 
				elif 'buying' in clean_title or 'buyer' == clean_title or 'merchandiser' == clean_title:
					topic = 'buyer'
				elif 'order picker' in clean_title or 'shop supervisor' in clean_title or 'retail assistant' in clean_title or 'picker packer' in clean_title:
					topic = 'retail'
				elif 'quantity surveyor' in clean_title:
					topic = 'surveyor'
				elif 'pa' == clean_title or ('assistant' in clean_title and ('executive' in clean_title or 'personal' in clean_title)):
					topic = 'assistant'
				elif 'physiotherapist' in clean_title or 'occupational therapist' in clean_title:
					topic = 'physio'; 
				elif 'building surveyor' in clean_title or 'groundworker' in clean_title or 'estimator' in clean_title or 'joiner' in clean_title or 'site manager' in clean_title or 'labourer' in clean_title:
					topic = 'construction'; 
				elif 'electrician' in clean_title:
					topic = 'electrician'; 
				elif 'plumber' in clean_title:
					topic = 'plumber'
				elif 'security officer' in clean_title and 'it' not in title_tokens:
					topic = 'security';
				elif 'probation officer' in clean_title or 'prison officer' in clean_title or 'police officer' in clean_title:
					topic = 'prison'
				elif 'hr' in title_tokens or "human resources" in clean_title:
					topic = 'hr'; 
				elif 'mot tester' in clean_title or 'vehicle technician' in clean_title or 'hgv technician' in clean_title or 'part advisor' == clean_title:
					topic = 'vehicle'; 
				elif 'recruitment consultant' in clean_title:
					topic = 'recruitment'; 
				elif 'paralegal' in clean_title or 'solicitor' in clean_title or 'legal secretary' in clean_title:
					topic = 'solicitor'
				elif 'project manager' in clean_title or 'product manager' in clean_title:
					topic = 'project'
				elif 'store manager' in clean_title or 'assistant manager' in clean_title:
					topic = 'storemanager';
				elif 'customer service assistant' in clean_title or 'customer service advisor' in clean_title or 'customer service' == clean_title:
					topic = 'customer'; 
				elif 'service advisor' in clean_title or 'panel beater' in clean_title or 'paint sprayer' in clean_title:
					topic = 'garage'; 			
				elif 'sale advisor' in clean_title or 'sale assistant' in clean_title or 'sale consultant' in clean_title or 'telesales' in clean_title or 'sale executive' in clean_title or 'brand ambassador' in clean_title:
					topic = "sale"; 
				elif 'property manager' in clean_title or 'letting negotiator' in clean_title:
					topic = "property"; 
				elif "supply teacher" in clean_title or "year teacher" in clean_title or "teaching assistant" in clean_title or "secondary teacher" == clean_title or "math teacher" == clean_title or "primary teacher" == clean_title or "sen teacher" in clean_title or "science teacher" in clean_title or "music teacher" in clean_title or "english teacher" in clean_title or "sen" in title_tokens: 
					topic = "teacher";
				elif 'nursery' in clean_title:
					topic = 'nursery' 
				elif 'healthcare assistant' in clean_title or 'nurse' == clean_title or 'registered general nurse' == clean_title or 'rgn' in title_tokens or 'agency nurse' in clean_title or "registered nurse" in clean_title or "rnm" in clean_title or "rnld" in clean_title:
					topic = "nurse";				
				elif 'care coordinator' in clean_title or 'caregiver' in clean_title or 'care worker' == clean_title or 'registered manager' in clean_title or "care assistant" == clean_title:
					topic = "care";
				elif 'devops engineer' in clean_title or 'solution architect' == clean_title or 'ux designer' in clean_title or 'php developer' in clean_title or 'web developer' == clean_title or "java developer" in clean_title or "front end developer" in clean_title or 'net developer' == clean_title or "normal automation" in clean_title or "software developer" in clean_title or "software engineer" in clean_title:
					topic = "software"; 
				elif 'it support' in clean_title or 'service desk' in clean_title:
					topic = 'itsupport'
				elif ("engineer" in clean_title and ("electrical" in clean_title or "service" in clean_title or "mechanical" in clean_title or "project" in clean_title or "design" in clean_title or "maintenance" in clean_title)) or ('mechanical fitter' in clean_title):
					topic = "engineer"; 
				elif 'data analyst' in clean_title or 'data scien' in clean_title:
					topic = 'data'
				elif "delivery driver" in clean_title:
					topic = "delivery"; 
				elif "warehouse manager" in clean_title or "warehouse operative" in clean_title or 'packer' == clean_title:
					topic = 'warehouse'; 
				elif "hotel" in clean_title or "hotel" in employer_name or (("housekeep" in clean_title or 'receptionist' in clean_title or 'front of house' in clean_title or "chef" in clean_title or "cleaner" in clean_title) and 'hotel' in clean_descr):
					topic = "hotel"; 
				elif 'caretaker' in clean_title or 'cleaner' in clean_title:
					topic = 'cleaner'; 
				elif "barista" in clean_title or "waiter" in clean_title or "waitress" in clean_title or "restaurant" in clean_title or "bar staff" in clean_title or "bar person" in clean_title or "bar host" in clean_title:
					topic = 'server'; 
				elif 'cook' == clean_title or 'catering assistant' in clean_title or 'kitchen assistant' in clean_title or "chef" == clean_title:
					topic = 'kitchen' 
				elif 'support worker' == clean_title:
					topic = 'support'; 
				elif 'hgv' in clean_title and 'driver' in clean_title or 'class driver' in clean_title:
					topic = 'hgv'; 
				elif 'factory operative' in clean_title or 'quality inspector' in clean_title or 'assembly operative' in clean_title or ('production operative' in clean_title and 'driver' not in clean_title):
					topic = 'production'; 
				elif ('machine' in clean_title and 'learning' not in clean_title) or ('machinist' in clean_title and 'sewing' not in clean_title) or 'cnc miller' in clean_title:
					topic = 'machine'
				elif 'facility manager' in clean_title or 'quality manager' == clean_title or 'supervisor' == clean_title or 'production planner' in clean_title or 'production manager' in clean_title or 'operation manager' in clean_title:
					topic = 'productionmanager'
				elif 'accountant' in clean_title or 'bookkeeper' in clean_title:
					topic = 'accountant'; 
				elif 'finance analyst' in clean_title or 'paraplanner' in clean_title or 'payroll' in clean_title or 'finance manager' in clean_title or 'credit controller' in clean_title or 'finance assistant' in clean_title or 'accountant' in clean_title or 'financial controller' in clean_title or 'purchase ledger' in clean_title:
					topic = 'finance'; 
				elif 'contract manager' in clean_title or 'account assistant' in clean_title or 'account manager' in clean_title:
					topic = "account"; 
				elif 'receptionist' in clean_title or 'front of house' in clean_title:
					topic = "receptionist"; 
				elif 'scrum master' in clean_title or 'business development' in clean_title or 'business analyst' in clean_title or ('business' in clean_title and ('analyst' in clean_title or 'manager' in clean_title) ):
					topic = "business"; 
				elif 'administrative assistant' in clean_title or 'office assistant' in clean_title or 'administration assistant' in clean_title or 'admin assistant' in clean_title or 'office manager' == clean_title or ('administrator' in clean_title and 'database' not in clean_title and 'it' not in title_tokens):
					topic = 'administrator'; 
				elif 'charity' in clean_title:
					topic = 'charity'
				elif 'gwaith' in clean_descr or 'swydd'	in clean_descr or 'amser' in clean_descr:
					topic = 'welsh'
				
	
				if topic:
					topiccount[topic] += 1
					outfile.write( f + " " + topic + " " + "_".join(clean_title.split()) + " " + " ".join( tokenise(job['jobTitle']  + " " +  str_or_none(job['jobDescription'])) ) + "\n" )
				else:
					unclassified[ clean_title ] += 1

print( topiccount, sum(topiccount.values()), len(topics), len(topiccount) )
print( unclassified.most_common(40), sum(unclassified.values()) )

