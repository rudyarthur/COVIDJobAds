import os
import sys
import json
import glob
from collections import Counter
import mysql.connector
from mysql.connector import errorcode
import joblib

from sklearn.tree import DecisionTreeClassifier
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer


FILE_DIR = os.path.dirname(os.path.abspath(__file__))
SYS_DIR = os.path.dirname(FILE_DIR)
sys.path.append(os.path.join(FILE_DIR, 'classification_model'))
sys.path.append(os.path.join(FILE_DIR, 'location_model'))


from db_utils import *
from clean import *
from locate import *


print( 'Setting up location databases' )
db_root = "/path/to/databases/"
dbs, london = setup_dbs(db_root)

print( 'Loading topic model...' )
pipe = joblib.load('classification_model/topic_model.sav')
print( 'Loaded' )

##location stats
nonuk_locations = set()	
db_hits = Counter()

counter = {
	"count" : 0, 
	"tot" : 0, 
	"empty" : 0, 
};

topic_hits = Counter()
db_hits = Counter()
nuts1_hits = Counter()


outfilename = "processed.json"
outfile = open(outfilename, 'w')

num = str(i)
print(num)
zip_file = ZipFile("/path/to/jobdata/data.zip")

nc = 0	
payload = {"jobs":None, "topics":None ,"locations":None}
for fn,f in enumerate(zip_file.namelist()):
	with zip_file.open(f) as infile:  

		if f.split(".")[-1] != "json": continue;
		idx = f.split(".")[0].split("b")[1]
		j = infile.read().decode('utf8')
		ad = json.loads(j)
			
		##dump to DB or file
		counter["tot"] += 1;
		if counter["tot"] % 100 == 0: print("read", counter["tot"], "ads");
		if not ad['jobId']:
			counter["empty"] += 1
			continue;
		else:
			counter["count"] += 1
		
			
						
		######################
		##save the job JSON
		######################
		ad['datePosted'] = date_or_none(ad['datePosted']); ##want to be a SQL date
		payload["jobs"]=ad
		
		######################		
		##figure out the topic
		######################
		clean_doc = " ".join(tokenise(ad['jobTitle']  + " " +  str_or_none(ad['jobDescription'])))
		topic = pipe.predict([clean_doc])
	
		job_topic = {
			'jobId': int(ad['jobId']),
			'topic': topic[0],
		}
		topic_hits[ topic[0] ] += 1
		payload["topics"]=job_topic

		
		#########################	
		##figure out the location
		#########################
		ad_location = ad_locator(ad, nonuk_locations, dbs, place_dict=london)				
		try:
			ad_location['jobId'] = int(ad['jobId'])
		except:
			print(ad)
			print(ad.keys())
			print(ad_location)
			break;

		if ad_location["db"]:
			db_hits[ ad_location["db"] ] += 1
			if ad_location["NUTS1"]:
				nuts1_hits[ad_location["NUTS1"]] += 1
		payload["locations"]=ad_location

		
		outfile.write( json.dumps(payload) + "\n" )
		payload = {"jobs":None, "topics":None ,"locations":None}
		

outfile.close();
	
print( counter["tot"], "total ads");
print( counter["empty"], "empty ads");					
print( counter["count"], "non-empty ads");					
print( nuts1_hits, sum(nuts1_hits.values())  )			
print( db_hits, sum(db_hits.values()) )			
print( topic_hits, sum(topic_hits.values()) )			



