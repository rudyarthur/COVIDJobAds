from lookup import *
import requests
import time

def hasNumbers(inputString):
	return any(char.isdigit() for char in inputString)

def str_or_none(st):
	if st is None:
		return None
	return str(st).lower()


class local_nominatim_lookup(lookup):
	"""Look up places in local nominatim database"""
	def __init__(self, database, use_biggest=False, tolerance=0, unbounded=True):
		
		lookup.__init__(self, database, use_biggest, tolerance, unbounded)
		self.dbname = "nominatim"
		self.key = "name1";
		self.qstring = "SELECT DISTINCT * FROM nominatim WHERE name1 = :name1 ORDER BY importance DESC";
		self.db_keys = ("name1", "name2", "lat", "lon", "importance","class", "boundingbox")
		self.callapi = True
		self.min_importance = 0.25;
		
	def lookup(self, name):
		name = name.lower()


		if self.cache and name in self.lookup_dict:
			return self.lookup_dict[name];
		else:
			self.c.execute(self.qstring, { 'name1' : name } );
			result = self.c.fetchall();
			output = {};
			
			for r in sorted(result, key = lambda x: float(x[4]), reverse=True ):
				for i,k in enumerate(self.db_keys):
					output[k] = r[i]
				if self.use_biggest:
					break;

			if len(output) > 0:
				if self.cache: self.lookup_dict[name] = output;
				return output;

		if self.callapi and len(output) == 0:
	
			print("Looking up", name, "via nominatim api", flush=True);


			try:
				if hasNumbers(name):
					raise Exception("hasNumbers") 

				r = requests.get('https://nominatim.openstreetmap.org/search?q='+name+'&format=json&countrycodes=gb&limit=1')
				data = r.json()[0]			
				importance = float(data['importance']);
				
				if importance <= self.min_importance:
					time.sleep(0.1);
					try:
						r = requests.get('https://nominatim.openstreetmap.org/search?q='+name+'&format=json&limit=1')
						data2 = r.json()[0]
						importance2 = float(data2['importance'])
					except:
						print("request failed", name, r)
					
					if importance2 > 2*self.min_importance:
						data = data2
						print("Global nom lookup", name, importance2, data2['display_name'])
					else:
						print("GB nom lookup", name, importance, data['display_name'])


				poly = {
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

				self.c.execute("INSERT INTO nominatim VALUES (:name1, :name2, :lat, :lon, :importance, :class, :boundingbox)", {
					'name1': str_or_none(name),
					'name2': str_or_none(data['display_name']),
					'lat': str_or_none(data['lat']),
					'lon': str_or_none(data['lon']),
					'importance': float(data['importance']),
					'class': str_or_none(data['class']),
					'boundingbox': str_or_none(poly)
				})
				self.conn.commit();
				
				return self.lookup(name)


			except:		
				self.c.execute("INSERT INTO nominatim VALUES (:name1, :name2, :lat, :lon, :importance, :class, :boundingbox)", {
					'name1': str_or_none(name),
					'name2': str_or_none(None),
					'lat': str_or_none(None),
					'lon': str_or_none(None),
					'importance': 0,
					'class': str_or_none(None),
					'boundingbox': str_or_none(None)
				})
				self.conn.commit();
				#print("request failed", name, r)
				
			time.sleep(0.1);

		return {};
			
	def load_all_names(self):
		return lookup.load_all_names(self, 0);	
