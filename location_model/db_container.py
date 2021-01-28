from country_lookup import *
#from fgs_lookup import *
from nuts_lookup import *
#from gadm_lookup import *
#from box_lookup import *
#from local_dbpedia_lookup import *
from local_geonames_lookup import *
from local_nominatim_lookup import *

class db_container:

	def __init__(self, filepath, active=set(), use_biggest=False, tolerance=0, population=1000, admin=2):

		self.filepath = filepath
		self.use_biggest = use_biggest
		self.tolerance = tolerance
		self.population = population;
		self.admin = admin;
		self.active = active;
		self.dbs = {}
		self.nuts = {}
		
		if "country" in active:
			self.country = country_lookup(filepath+"country.db", use_biggest=use_biggest, tolerance=tolerance);
			self.dbs["country"] = self.country;
		for i in [1,2,3]:
			if "nuts{}".format(i) in active:
				self.nuts[0] = nuts_lookup( filepath + "nuts{}.db".format(i) );
				self.dbs["nuts{}".format(i)] = self.fgs;
		#if "fgs" in active:
		#	self.fgs = fgs_lookup(filepath + "fgs.db");
		#	self.dbs["fgs"] = self.fgs;
		#if "gadm" in active:
		#	self.gadm = gadm_lookup(filepath+"gadm.db", use_biggest=False, tolerance=tolerance);
		#	self.dbs["gadm"] = self.gadm;
		#if "gadmdata" in active:
		#	self.gadmdata = gadm_data(filepath+"gadm.json");
		#	self.dbs["gadmdata"] = self.gadmdata;
		#if "box" in active:
		#	self.box = box_lookup(filepath+"box_" + str(admin)+ ".db");
		#	self.dbs["box"] = self.box;
		if "geonames" in active:
			self.local_geonames = local_geonames_lookup(filepath + "local_geonames_populated" + str(population) + ".db");
			self.dbs["geonames"] = self.local_geonames;
		if "nomimatim" in active:
			self.local_nomimatim = local_nomimatim_lookup(filepath + "nomimatim.db");
			self.dbs["nomimatim"] = self.local_nomimatim;
		#if "dbpedia" in active:
		#	self.local_dbpedia = local_dbpedia_lookup(filepath + "dbpedia.db");
		#	self.dbs["dbpedia"] = self.local_dbpedia;

	def add(self,db_type, db):
		self.dbs[db_type] = db;
		self.active.add(db_type)
	def lookup(self,name):
		res = {}
		for a in self.dbs:
			res[a] = self.dbs[a].lookup(name);
		return res;

	def lookup_in(self,name, db_type):
		return self.dbs[db_type].lookup(name);
