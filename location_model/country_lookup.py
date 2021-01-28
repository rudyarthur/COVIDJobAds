import sqlite3
from lookup import *

class country_lookup(lookup):
	"""Look up places in country database"""
	def __init__(self, database, use_biggest=False, tolerance=0, unbounded=True):
		
		lookup.__init__(self, database, use_biggest, tolerance, unbounded)
		self.dbname = "country"
		self.key = "name"
		self.qstring = "SELECT poly FROM country WHERE name = :name"
		self.pstring = "SELECT population FROM country WHERE name = :name"

		self.countrypop_dict = {}

	def load_all(self):
		lookup.load_all(self, 0);
				
	def load_all_names(self):
		return lookup.load_all_names(self, 0);
				
	def lookup_population(self, name):

		name = name.lower()
		if self.cache and name in self.countrypop_dict:
			return self.countrypop_dict[name];
		else:
			self.c.execute(self.pstring, { self.key : name })
			result = self.c.fetchall();
			
			if( len(result) > 0 ):
				tmp = result[0][0];
				if self.cache: self.countrypop_dict[name] = tmp;
				return tmp;
					
		return None;
		
