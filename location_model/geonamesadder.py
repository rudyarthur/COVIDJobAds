import sqlite3
import sys
import urllib.request
import os
import zipfile
from utils import *
 


if len(sys.argv) < 2:
	print("usage: geonamesadder.py filepath minpop");
	print("Downloads geonames database from", url )
	print("and creates an SQL database in filepath + local_geonames_populatedminpop.db")
	sys.exit(1);
	
url = 'http://download.geonames.org/export/dump/allCountries.zip'
filepath = sys.argv[1]
min_pop = int(sys.argv[2])
ewonly = False;
getdata(url, filepath, full_name='allCountries.txt')
filename = "local_geonames_populated" + str(min_pop) + ".db"

if not os.path.isfile(filepath + filename):
	print("Writing db to", filepath+filename );

	##load country codes
	cc_dict = { None : '', '' : '' }
	with open('data/countryInfo.txt', 'r') as cfile:
		for line in cfile:
			if line[0] != '#':
				words = line.split('\t');
				cc_dict[ words[0].lower() ] = words[4];
				

	feature_class = {
			'a' : 'country, state, region,...',
			'h' : 'stream, lake, ...',
			'l' : 'parks,area, ...',
			'p' : 'city, village,...',
			'r' : 'road, railroad',
			's' : 'spot, building, farm',
			't' : 'mountain,hill,rock,...',
			'u' : 'undersea',
			'v' : 'forest,heath,...',
			'' : ''
			}
			
	conn = sqlite3.connect(filepath+filename)
	c = conn.cursor()

	#small table (no alternative names, too long)
	c.execute('''CREATE TABLE geonames (
		name TEXT,
		latitude TEXT,
		longitude TEXT,
		fclName TEXT,
		feature_code TEXT,
		countryName TEXT,
		population INTEGER
		)
	''');
		
	c.execute('CREATE INDEX geonames_name_idx ON geonames (name)')
	conn.commit()

	count = 0
	num = 0
	with open(filepath + 'allCountries.txt', 'r') as datafile:
		for line in datafile:
			count += 1;
			if count % 10000 == 0:
				print (count, "/ 11395855" )
				
			words = line.split('\t')
			if int_or_zero(words[14]) <= min_pop: continue;			

			num += 1
			
			c.execute("INSERT INTO geonames VALUES (:name, :latitude, :longitude, :fclName, :feature_code, :countryName, :population)", {
					'name' : str_or_none(words[1]),
					'latitude': str_or_none(words[4]),
					'longitude' : str_or_none(words[5]),
					'fclName'  : feature_class[ str_or_none(words[6]) ],
					'feature_code'  : str_or_none(words[7]),
					'countryName'   : cc_dict[ str_or_none(words[8]) ],
					'population' : int_or_zero(words[14])
				})

	print("added", num)
	conn.commit()


