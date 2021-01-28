import sqlite3
from lookup import *

class local_geonames_lookup:
	"""Look up places in local geonames database"""
	def __init__(self, database, use_biggest=False, tolerance=0, unbounded=True):
		
		lookup.__init__(self, database, use_biggest, tolerance, unbounded)
		self.dbname = "geonames"
		self.qstring = "SELECT * FROM geonames WHERE name = :name ORDER BY population DESC";
		
		self.db_keys = ( 
			'name',
			'lat' ,
			'lng' ,
			'fclName' ,
			'feature_code' ,
			'countryName' ,
			'population'
		)
		
	def lookup(self, name):
		name = name.lower()
		if self.cache and name in self.lookup_dict:
			return self.lookup_dict[name];
		else:
			self.c.execute(self.qstring, { 'name' : name } );
			result = self.c.fetchall();
			output = { 'totalResultsCount' : 1, 'geonames' : [] };
			for r in result:
				tmp = {};
				for i,k in enumerate(self.db_keys):
					tmp[k] = r[i]
				tmp['score'] = 1;
				output['geonames'].append( tmp )
				if self.use_biggest:
					break;

			output['totalResultsCount']	= len( output['geonames'] )
			if self.cache: self.lookup_dict[name] = output;
			
		return output;
