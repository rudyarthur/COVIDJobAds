import sqlite3
import sys
import urllib.request
import os
import zipfile
import csv
from fastkml import kml
from utils import *
import json
import re
from shapely.geometry import Polygon
from shapely.geometry import Point
from shapely.geometry import box
from shapely.geometry import MultiPolygon
from shapely.geometry import shape
from shapely.ops import cascaded_union
from shapely.geometry import mapping
import string

if len(sys.argv) < 2:
	print("usage: nutsadder.py filepath");
	print("and creates an SQL database in filepath+nuts?.db")
	sys.exit(1);

filepath = sys.argv[1]

for level in [1,2,3]:

	if not os.path.isfile(filepath+"nuts{}.db".format(level) ):
	
		print("reading level", level, "...")
		with open(filepath + "NUTS_Level_{}__January_2018__Boundaries.kml".format(level), 'rt', encoding="utf-8") as myfile:
			doc="".join( myfile.readlines()[1:] )
		k = kml.KML()	
		k.from_string(doc)	

		document = list(k.features())
		folder = list(document[0].features())
		places = list(folder[0].features())


		print("Writing db to", filepath+"nuts{}.db".format(level) );

		conn = sqlite3.connect(filepath+"nuts{}.db".format(level))
		c = conn.cursor()
		c.execute('''CREATE TABLE nuts (
			name TEXT COLLATE NOCASE,
			id INT,
			poly BLOB)''')
		c.execute('CREATE INDEX IF NOT EXISTS nutsname ON nuts (name)')
		conn.commit()

		for p in places:
			
			poly = p.geometry;
			for d in p.extended_data.elements[0].data:
				if re.match(r"nuts[0-9]{3}cd", d['name']):
					id_code = d['value'];
				if re.match(r"nuts[0-9]{3}nm", d['name']):
					name = d['value'];
			
			di = {}
			di["id"] = id_code
			di["name"] = name.lower().replace(", city of","").replace(" cc","")
			di["name"] = di["name"].translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
			di["poly"] = str(mapping(poly))	
			print(di["name"])
			c.execute("INSERT INTO nuts VALUES (:name, :id, :poly)", di)
		
		conn.commit()
	
