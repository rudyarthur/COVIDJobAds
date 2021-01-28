import sqlite3
import fiona
import sys
import urllib.request
import os
import zipfile
import csv
from utils import *
import json

url = 'http://thematicmapping.org/downloads/TM_WORLD_BORDERS-0.3.zip'	

if len(sys.argv) < 2:
	print("usage: countryadder.py filepath");
	print("Downloads thematic mapping database from", url )
	print("and creates an SQL database in filepath+country.db")
	sys.exit(1);

filepath = sys.argv[1]
getdata(url, filepath, full_name='TM_WORLD_BORDERS-0.3.shp')

pops = {}
with open("data/country_population.csv", 'r') as csvfile:
	spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
	for row in spamreader:
		name = " ".join(row[:-1]).strip().lower()
		if name == "virgin islands  u.s.":
			name = "virgin islands, u.s." #stupid comma in place name!
		pops[name] = int(row[-1]);

##this is to match GADM
name_map =  {"cote d'ivoire" : "côte d'ivoire",
 "congo" : "republic of congo", 
 "wallis and futuna islands" : "wallis and futuna",
 "åland islands" : "åland",
 "sao tome and principe" : "são tomé and príncipe",
 "svalbard" : "svalbard and jan mayen",
 "saint martin" : "saint-martin",
 "palestine" : "palestina",
 "french southern and antarctic lands" : "french southern territories",
 "united states virgin islands" : "virgin islands, u.s.",
 "saint barthelemy" : "saint-barthélemy",
 "viet nam" : "vietnam",
 "falkland islands (malvinas)" : "falkland islands",
 "burma" : "myanmar",
 "libyan arab jamahiriya" : "libya",
 "brunei darussalam" : "brunei",
 "micronesia, federated states of" : "micronesia",
 "iran (islamic republic of)" : "iran",
 "republic of moldova" : "moldova",
 "syrian arab republic" : "syria",
 "united republic of tanzania" : "tanzania",
 "korea, democratic people's republic of" : "north korea",
 "korea, republic of" : "south korea",
 "lao people's democratic republic" : "laos",
 "the former yugoslav republic of macedonia" : "macedonia",
 "cocos (keeling) islands" : "cocos islands",
 "holy see (vatican city)" : "vatican city",
 "south georgia south sandwich islands" : "south georgia and the south sandwich islands"
}



				
if not os.path.isfile(filepath+"country.db"):
	print("Writing db to", filepath+"country.db" );

	conn = sqlite3.connect(filepath+"country.db")
	c = conn.cursor()
	c.execute('''CREATE TABLE country (
		name TEXT COLLATE NOCASE,
		poly BLOB,
		population INTEGER,
		fips TEXT,
		iso2 TEXT,
		iso3 TEXT,
		un INT,
		area INT,
		lon REAL,
		lat REAL)''')
	c.execute('CREATE INDEX IF NOT EXISTS countryname ON country (name)')
	conn.commit()

	fi = fiona.open(filepath + 'TM_WORLD_BORDERS-0.3.shp', 'r')

	count = 0
	while True:
		try:
			a = fi.next()
		except:
			break

		count += 1
		di = a['properties']
		di['poly'] = str(a['geometry'])

		di['NAME'] = (di['NAME'].lower() )
		if di['NAME'] in name_map:
			di['NAME'] = name_map[di['NAME']];
		if di['NAME'] in ["macau", "netherlands antilles"]: #these are not in GADM
			continue;

		
		di['population'] = 0
		if di['NAME'] in pops:
			di['population'] = pops[ di['NAME'] ] 
		else:
			print( "missing", di['NAME'] )
			
		count += 1
		c.execute("INSERT INTO country VALUES (:NAME, :poly, :population, :FIPS, :ISO2, :ISO3, :UN, :AREA, :LON, :LAT)", di)


	conn.commit()
