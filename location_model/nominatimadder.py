import sqlite3
import sys
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import os
import bz2
import re
import json
import time
from utils import *


       
if len(sys.argv) < 2:
	print("usage: nominatimadder.py infile filepath");
	print("Creates an SQL database in filepath + nominatim.db")
	sys.exit(1);

url = 'https://nominatim.openstreetmap.org/search/'

filepath = sys.argv[1]
filename = "nominatim.db"
keys = set(["importance", "type", "display_name", "lat", "lon", "osm_type", "osm_id", "class", "boundingbox", "place_id"])
if not os.path.isfile(filepath + filename):
	
	print("Writing db to", filepath+filename );
	
	#with open(infilename, 'r') as infile: loc_data = json.loads(infile.read())


	"""	
	importance 0.5714689108613352
	type town
	display_name Shepherd's Bush, London Borough of Hammersmith and Fulham, London, Greater London, England, W12 8AW, United Kingdom
	place_id 115194
	lon -0.2229007
	osm_type node
	osm_id 21662002
	class place
	lat 51.505314
	boundingbox ['51.465314', '51.545314', '-0.2629007', '-0.1829007']
	"""

	conn = sqlite3.connect(filepath+filename)
	c = conn.cursor()

	c.execute('''CREATE TABLE nominatim (
		name1 TEXT,
		name2 TEXT,
		lat TEXT,
		lon TEXT,
		importance REAL,
		class TEXT,
		boundingbox BLOB
		)
	''');
		
	c.execute('CREATE INDEX nominatim_name1_idx ON nominatim (name1)')
	c.execute('CREATE INDEX nominatim_name2_idx ON nominatim (name2)')
	conn.commit()
		

	count = 0	
	for place in ["exeter"]:
		count += 1
		
		if hasNumbers(place): continue;
		
		print("blee", place)
		place="manchester"
		r = requests.get('https://nominatim.openstreetmap.org/search?q='+place+'&format=json&countrycodes=gb&limit=1')
		sys.exit(1);
		
		try:
			r = requests.get('https://nominatim.openstreetmap.org/search?q='+place+'&format=json&countrycodes=gb&limit=1')
			data = r.json()[0]			
			#for k in data: print(k, data[k])
		except:		
			continue;

		print(place, count )

		output = {
		'coordinates':[[[
			(float(data['boundingbox'][2]), float(data['boundingbox'][0])),
			(float(data['boundingbox'][2]), float(data['boundingbox'][1])),
			(float(data['boundingbox'][3]), float(data['boundingbox'][1])),
			(float(data['boundingbox'][3]), float(data['boundingbox'][0])),
			(float(data['boundingbox'][2]), float(data['boundingbox'][0]))
		]]]
		, 
		'type':'Polygon'
		}


		c.execute("INSERT INTO nominatim VALUES (:name1, :name2, :lat, :lon, :importance, :class, :boundingbox)", {
			'name1': str_or_none(place),
			'name2': str_or_none(data['display_name']),
			'lat': str_or_none(data['lat']),
			'lon': str_or_none(data['lon']),
			'importance': float(data['importance']),
			'class': str_or_none(data['class']),
			'boundingbox': str_or_none(output)
		})
		
		conn.commit()
		time.sleep(0.1); #be nice

else:
	print("nominatim.db already exists under", filepath)
