import sqlite3
from lookup import *

class nuts_lookup(lookup):
	"""Look up places in FGS database"""
	def __init__(self, database, use_biggest=True, tolerance=0, unbounded=True):
		
		lookup.__init__(self, database, use_biggest, tolerance, unbounded)
		self.dbname = "nuts"
		self.key = "name"
		self.qstring = "SELECT poly FROM nuts WHERE name = :name"

	def load_all(self):
		lookup.load_all(self, 0);

	def load_all_names(self):
		return lookup.load_all_names(self, 0);
