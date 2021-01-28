import os
import sys
import urllib.request
import zipfile
import bz2
from shapely.geometry import Polygon
from shapely.ops import unary_union
import numpy as np
import sqlite3

def hasNumbers(inputString):
	return any(char.isdigit() for char in inputString)
	
def str_or_none(st):
	if st is None:
		return None
	return str(st).lower()

def int_or_zero(st):
	try: 
		return int(st)
	except ValueError:
		return 0
 
def float_or_zero(st):
	try: 
		return float(st)
	except ValueError:
		return 0 
        
def download(url, filepath, full_name=None):
	download_name = url.split("/")[-1];
	if (full_name is None) or (not os.path.isfile(filepath + full_name)):
		print("Downloading...", download_name);
		urllib.request.urlretrieve(url, filepath + download_name);
	return download_name;
	
def extract(download_name, filepath, full_name=None):
	compression_type = download_name.split(".")[-1]
	if (full_name is None) or (not os.path.isfile(filepath + full_name)):
		if compression_type == "zip":
			print("Unzipping...", download_name);
			with zipfile.ZipFile(filepath + download_name, 'r') as zip_ref:
				zip_ref.extractall(filepath)
		if compression_type == "bz2":
			print("Bunzip2...");
			os.system("bunzip2 "+ filepath + download_name);
		else:
			return False
	return True
	
def getdata(url, filepath, full_name=None):
	download_name = download(url, filepath, full_name=full_name);
	return extract(download_name , filepath, full_name=full_name)



##remove islands		
def remove_islands(input_poly):

	if input_poly.geom_type=="MultiPolygon":
		
		max_area = -np.inf;
		poly = None	
		
		for p in input_poly:
			if p.area > max_area:
				max_area = p.area;
				poly = p;
				
		islands = []
		for p in input_poly:
			if p.area != max_area:
				islands.append(p)
			
		return poly, islands
	
	return input_poly, []
	
##copy border of poly2 to poly1 
def copy_border(poly1, poly2):
	bp = Polygon( unary_union([poly1, poly2]).exterior ).buffer(0)
	diff = bp.difference(poly2)		
	big, islands = remove_islands(diff)
	return big


def smooth_join(simple_dict):
	print("...sort by area...")
	#sort by area
	aplaces = []
	apolys = []
	for place in sorted(simple_dict, key=lambda x: simple_dict[x].area, reverse = True):
		aplaces.append(place)
		apolys.append(simple_dict[place] )

	print("...neighbours...")
	##find neighbours	
	neighbours = []
	for i in range(len(aplaces)):
		print(aplaces[i], "has neighbours...")
		neighbours = []
		big_poly = simple_dict[ aplaces[i] ]

		for j in range(i+1,len(aplaces)):
			if big_poly.intersects( simple_dict[aplaces[j]] ):
				print(aplaces[j])
				big_poly = copy_border(big_poly, simple_dict[ aplaces[j]])
		simple_dict[ aplaces[i] ] = big_poly;
	
def write_to_fgs(filepath, simple_dict):
	conn = sqlite3.connect(filepath+"fgs.db")
	c = conn.cursor()
	
	for name in simple_dict:

		a = {'geometry':{}}
		if simple_dict[name].geom_type == "MultiPolygon":
			a['geometry']['type'] = "MultiPolygon"
			a['geometry']['coordinates'] = []
			for g in simple_dict[name]:
				lons, lats = g.exterior.coords.xy
				a['geometry']['coordinates'].append( list(zip(lons,lats)) )
		else:
			a['geometry']['type'] = "Polygon"
			lons, lats = simple_dict[name].exterior.coords.xy
			a['geometry']['coordinates'] = [list(zip(lons,lats))]
			
		c.execute("INSERT INTO fgs VALUES (:n1, :n2, :n3, :n4, :n5, :n6, :poly)", {
			'n1': str_or_none(name),
			'n2': str_or_none(None),
			'n3': str_or_none(None),
			'n4': str_or_none(None),
			'n5': str_or_none(None),
			'n6': str_or_none(None),
			'poly': str_or_none(a['geometry'])
		})

	conn.commit()
