import sqlite3
import ast
from shapely.geometry import MultiPolygon
from shapely.geometry import box
from shapely.geometry import shape

class lookup:
	"""Look up places in a database
	@param dbloc: location of database
	@param use_biggest: when multiple polygons returned, only use the largest (useful to exclude islands)
	@param tolerance: Smooth polygons
	
	Attributes:
		unbounded: apply lat/lon filters
		llcrnrlat: min latitude
		llcrnrlon: min longitude
		urcrnrlat: max latitude
		urcrnrlon: max longitude
		dbname: database name
		key: name key
		
	Functions:
		set_bounds : set min/max lat/lng
		lookup : look up name in database
		load_all : look up all entries in database
		load_all_names : look up all names in database
		destroy : exit cleanly
	"""
	def __init__(self, database, use_biggest=False, tolerance=0, unbounded=True):
		self.dbloc = database
		self.conn = sqlite3.connect(self.dbloc)    
		self.c = self.conn.cursor()

		self.cache = True;
		self.cache_misses = False;
		self.mbox = True;
		self.lookup_dict = {};
		self.boxes = {};
		self.names = {};

		self.llcrnrlat=-180;
		self.llcrnrlon=-180;
		self.urcrnrlat=180;
		self.urcrnrlon=180;
		self.use_biggest=use_biggest;
		self.tolerance = tolerance;
		self.unbounded = unbounded;

	def set_bounds(self,xmin, ymin, xmax, ymax):
		self.llcrnrlat=xmin;
		self.llcrnrlon=ymin;
		self.urcrnrlat=xmax;
		self.urcrnrlon=ymax;
	
	def make_box(self, name):
		bxs = [];
		for p in self.lookup_dict[name]:
			bxs.append( box(p.bounds[0], p.bounds[1], p.bounds[2], p.bounds[3] ) );
		self.boxes[name] = MultiPolygon( bxs )
				
	#@classmethod	
	def lookup(self, name):
		name = name.lower()
		if self.cache and name in self.lookup_dict:
			return self.lookup_dict[name];
		else:
			self.c.execute(self.qstring, { self.key : name } )
			result = self.c.fetchall();		
			if( len(result) > 0 ):
				#tmp = proc_polystr(result, self.llcrnrlat, self.llcrnrlon, self.urcrnrlat, self.urcrnrlon, self.tolerance, self.unbounded);
				tmp = shape(ast.literal_eval(result[0][0]))
				if tmp.geom_type == "Polygon": tmp = MultiPolygon([tmp])
				
				if len(tmp) > 1:
					if self.use_biggest: 
						tmp = [ max(tmp, key=lambda x: x.area) ];
				if self.cache: 
					self.names[name] = 1;
					self.lookup_dict[name] = MultiPolygon(tmp);		
					if self.mbox: self.make_box(name);			
				return tmp;
			else:
				if self.cache_misses: self.lookup_dict[name] = [];						
				
		return [];

	def load_all_names(self, n):
		self.c.execute("SELECT DISTINCT " + self.key + " FROM " + self.dbname);
		self.names = {};
		while True:
			row = self.c.fetchone() ; 
			if row is not None:
				if row[0] != '':
					if row[0] in self.names:
						self.names[row[0]] += 1
					else:
						self.names[row[0]] = 1
			else:
				break;

	def load_all(self, n):
		lookup.load_all_names(self, n)
		self.cache = True;
		for i,name in enumerate(self.names): 
			if len(name) > 0:
				self.lookup(name);
				
	def destroy(self):
		self.conn.close()
