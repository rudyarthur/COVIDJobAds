import string
import ast
import re
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from shapely.geometry import box
from shapely.geometry import shape
from shapely.ops import cascaded_union
import sys
import time
from db_container import *
from nuts_container import *

printable = set(string.printable)




def setup_dbs(db_root):
	country = country_lookup(db_root+"country.db");
	geo = local_geonames_lookup(db_root+"local_geonames_populated1000.db");
	nom = local_nominatim_lookup(db_root+"nominatim.db");



	dbs = db_container(db_root);
	dbs.add("country", country);
	dbs.add("geonames", geo);
	dbs.add("nominatim", nom);
	for i in range(1,4):
		ndb = "nuts{}".format(i)
		nuts = nuts_lookup(db_root+ndb+".db");
		nuts.load_all_names();
		dbs.add(ndb, nuts);

	london = {}
	london["west london"] = cascaded_union( [ MultiPolygon(  dbs.lookup_in(m, "nuts3") ) for m in ["brent", "harrow and hillingdon", "ealing", 'kensington   chelsea and hammersmith   fulham', 'hounslow and richmond upon thames']] )
	london["east london"] = cascaded_union( [ MultiPolygon(  dbs.lookup_in(m, "nuts3") ) for m in ['barking   dagenham and havering','hackney and newham','redbridge and waltham forest','tower hamlets']] )
	london["south london"] = cascaded_union( [ MultiPolygon(  dbs.lookup_in(m, "nuts3") ) for m in ['bexley and greenwich','bromley','croydon','merton  kingston upon thames and sutton','lambeth','lewisham and southwark','wandsworth']] )
	london["north london"] = cascaded_union( [ MultiPolygon(  dbs.lookup_in(m, "nuts3") ) for m in ['barnet','haringey and islington','enfield']] )
	london["central london"] = cascaded_union( [ MultiPolygon(  dbs.lookup_in(m, "nuts3") ) for m in ['camden and city of london','haringey and islington','kensington   chelsea and hammersmith   fulham','lambeth','lewisham and southwark','wandsworth','westminster']] )

	london["south east london"] = cascaded_union( [ MultiPolygon(  dbs.lookup_in(m, "nuts3") ) for m in ['bexley and greenwich' 'bromley','lewisham and southwark']] )
	london["south west london"] = cascaded_union( [ MultiPolygon(  dbs.lookup_in(m, "nuts3") ) for m in ['croydon','merton  kingston upon thames and sutton','lambeth', 'wandsworth', 'hounslow and richmond upon thames']])
	london["north east london"] = cascaded_union( [ MultiPolygon(  dbs.lookup_in(m, "nuts3") ) for m in ['barking   dagenham and havering','camden and city of london','hackney and newham','redbridge and waltham forest','tower hamlets']] )
	london["north west london"] = cascaded_union( [ MultiPolygon(  dbs.lookup_in(m, "nuts3") ) for m in ['barnet','camden and city of london','enfield','hackney and newham','haringey and islington','westminster',"brent","ealing", 'kensington   chelsea and hammersmith   fulham','hounslow and richmond upon thames',"harrow and hillingdon"]] )
	london["city of london"] = cascaded_union( [ MultiPolygon(  dbs.lookup_in(m, "nuts3") ) for m in ['camden and city of london']] )

	london["london"] = MultiPolygon(  dbs.lookup_in("london", "nuts1") )
	##kingston upon hull = Hull
	london["kingston"] = MultiPolygon(  dbs.lookup_in('merton  kingston upon thames and sutton', "nuts3") )

	return dbs, london
	
	
#uk_fullname = {};
#with open("uk_fullname.txt", 'r') as infile:
#	for line in infile:
#		words = ast.literal_eval(line)
#		uk_fullname[words[0]] = words[1]
uk_bbox = box(-11,49,3,61)		
		
def emoji_filter(text):
	"""
	removes emoji and weird chars from text
	"""
	return ''.join(filter(lambda x: x in printable, text));

def poly_to_boxstring(poly):
	return ",".join( [ str(p) for p in poly.bounds ] )

def poly_to_point(poly):
	return (poly.bounds[0] + poly.bounds[2])*0.5 , (poly.bounds[1] + poly.bounds[3])*0.5
		
def text_to_loc( place_name, db_container, place_dict, target_country="united kingdom"):

	#if place_name in uk_fullname: place_name = uk_fullname[place_name];

	output = {
		"db" : None,
		"match_name" : None,
		"box" : None,
		"lat" : None,
		"lng" : None,
	}

	if place_dict:
		for p in place_dict:
			if p == place_name:
				output["db"] = "place"
				output["match_name"] = p
				output["box"] = poly_to_boxstring( place_dict[p] )
				output["lng"] , output["lat"]  = poly_to_point( place_dict[p] )
				return output


	#check if place is a country!
	res = db_container.lookup_in(place_name, "country");
	if len(res) > 0:
		poly = MultiPolygon(res)
		output["db"] = "country"
		output["match_name"] = place_name
		output["box"] = poly_to_boxstring( poly )
		output["lng"] , output["lat"]  = poly_to_point( poly )
	
		return output


	#check if place is in NUTS
	for n in range(3,0,-1):	
		res = db_container.lookup_in(place_name, "nuts{}".format(n) );
		#in db as is
		if len(res) > 0:
			poly = MultiPolygon(res);
			output["db"] = "nuts{}".format(n)
			output["match_name"] = place_name
			output["box"] = poly_to_boxstring( poly )

			output["lng"] , output["lat"]  = poly_to_point( poly )
			return output;


	#inexact name match
	for n in range(3,0,-1):	
		matched = set()
		for i in db_container.dbs["nuts{}".format(n)].names:
			got = False;
			words = i.split()
			for k in words:
				if place_name == k: ##cambridge = cambridgeshire
					matched.add(i); got = True;
					output["match_name"] = i
					break;
				#if place_name == re.sub("shire", "", k): ##cambridge = cambridgeshire
				#	print("look", place_name)
				#	matched.add(i); got = True;
				#	output["match_name"] = i
				#	break;
			if not got: 
				#check n-grams
				pwords = place_name.split()
				lp = len(pwords)
				if len(pwords) > 1 and len(pwords) <= len(words): ##multiple words
					for g in range(0,len(words)-lp+1):
						ng = " ".join(words[g:g+lp])
						if ng == place_name:
							matched.add(i); got = True;
							output["match_name"] = i
							break;

		
		if len(matched) > 0:
			poly = cascaded_union( [ MultiPolygon(db_container.lookup_in(p, "nuts{}".format(n))) for p in matched ] )
			output["db"] = "nuts{}".format(n)
			output["box"] = poly_to_boxstring( poly )
			output["lng"] , output["lat"]  = poly_to_point( poly )
			return output;
	
	#check if place is in geonames!
	gr = db_container.lookup_in(place_name, "geonames");
	match_places = []
	outside_places = []
	for g in gr['geonames']: #sorted by population
		#in target?
		inside = True;
		if len(target_country) != 0:
			if g['countryName'].lower() not in target_country:
				inside = False;
		
		if inside:
			match_places.append( (g['population'], g['lng'], g['lat']) )
		else:
			outside_places.append( (g['population'], g['lng'], g['lat']) )
			
	
	if len(match_places) > 0:
		#use most populous
		output["db"] = "geonames"
		output["match_name"] = place_name
		output["box"] = str(match_places[0][1]+","+match_places[0][2]+","+match_places[0][1]+","+match_places[0][2])
		output["lng"] = float(match_places[0][1])
		output["lat"] = float(match_places[0][2])
		return output
	elif len(outside_places) > 0 and outside_places[0][0] > 1000000: ##a large city not in UK
		#place outside uk
		output["db"] = "geonames_nonuk"
		output["match_name"] = place_name
		output["box"] = str(outside_places[0][1]+","+outside_places[0][2]+","+outside_places[0][1]+","+outside_places[0][2])
		output["lng"] = float(outside_places[0][1])
		output["lat"] = float(outside_places[0][2])		
		

	nm = db_container.lookup_in(place_name, "nominatim");
	if len(nm) > 0 and nm['lon']:

		pt = nm['lon'] + "," + nm['lat']
		box = ast.literal_eval(nm['boundingbox'])['coordinates']
		box_string = str(box[0][0][0][0]) + "," + str(box[0][0][0][1]) + "," + str(box[0][0][2][0]) + "," + str(box[0][0][2][1])

		if uk_bbox.contains( Point(float(nm['lon']), float(nm['lat'])) ):
			

			output["db"] = "nominatim"
			output["match_name"] = place_name
			output["box"] = box_string
			output["lng"] = float(nm['lon'])
			output["lat"] = float(nm['lat'])
			return output
			
		else:	
			output["db"] = "nominatim_nonuk"
			output["match_name"] = place_name
			output["box"] = box_string
			output["lng"] = float(nm['lon'])
			output["lat"] = float(nm['lat'])
			return output
	
	return output;


def clean_location(line):
	return emoji_filter(line).replace("\n", " ").replace("\r", " ").strip().lower()

def ad_locator(ad, nonuk_locations, dbs, place_dict=None):
	
	##Tweet text
	loc_text = clean_location(ad['locationName'])
	
	##############################
	##Process words in loc field##
	##############################
	if loc_text not in nonuk_locations:
		output = text_to_loc( loc_text, dbs, place_dict )
		if not output["db"]: 
			for s in ["international", "industrial", "business", "investement", "trading", "rail", "distribution"]:
				np = loc_text.split(s)[0]
				if np != loc_text:
					output = text_to_loc( np, dbs, place_dict )	
	else:
		print("non uk", loc_text)

	if output["db"]: 
		get_nuts(output, dbs)
	
	return output;

	
	
