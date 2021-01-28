from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from shapely.geometry import box
from shapely.geometry import shape
import sys

nuts_topdown = {}
nuts_topdown['north east  england '] = {
'tees valley and durham' : {'hartlepool and stockton on tees', 'south teesside', 'darlington', 'durham'},
'northumberland and tyne and wear' : {'sunderland', 'tyneside', 'northumberland'},
}
nuts_topdown['north west  england '] = {
'cumbria' : {'west cumbria','east cumbria'},
'cheshire' : {'cheshire west and chester','warrington','cheshire east'},
'greater manchester' : {'manchester','greater manchester north east','greater manchester north west','greater manchester south east','greater manchester south west'},
'lancashire' : {'chorley and west lancashire','east lancashire','lancaster and wyre','mid lancashire','blackburn with darwen','blackpool'},
'merseyside' : {'east merseyside','liverpool','sefton','wirral'},
}
nuts_topdown['yorkshire and the humber'] = {
'east yorkshire and northern lincolnshire' : {'north and north east lincolnshire','kingston upon hull','east riding of yorkshire'},
'north yorkshire' : {'york','north yorkshire'},
'south yorkshire' : {'barnsley  doncaster and rotherham','sheffield'},
'west yorkshire' : {'bradford','leeds','calderdale and kirklees','wakefield' },
}
nuts_topdown['east midlands  england '] = {
	'derbyshire and nottinghamshire' : {'derby','east derbyshire','south and west derbyshire','nottingham','north nottinghamshire','south nottinghamshire'},
	'leicestershire  rutland and northamptonshire' : {'leicester','leicestershire and rutland','west northamptonshire','north northamptonshire'},
	'lincolnshire' : {'lincolnshire'},
}	
nuts_topdown['west midlands  england '] = {
'herefordshire  worcestershire and warwickshire' : {'worcestershire','warwickshire','herefordshire  county of'},
'shropshire and staffordshire' : {'telford and wrekin','staffordshire','stoke on trent','shropshire'},
'west midlands' : {'walsall','wolverhampton','birmingham','solihull','coventry','dudley','sandwell'},
}
nuts_topdown['east of england'] = {
'east anglia' : {'breckland and south norfolk','suffolk','peterborough','cambridgeshire','norwich and east norfolk','north and west norfolk'},
'bedfordshire and hertfordshire' : {'bedford','luton','central bedfordshire','hertfordshire'},
'essex' : {'essex thames gateway','west essex','heart of essex','thurrock','southend on sea','essex haven gateway'},
}
nuts_topdown['london'] = {
'inner london   west' : {'wandsworth','kensington   chelsea and hammersmith   fulham','camden and city of london','westminster'},
'inner london   east' : {'lambeth','lewisham and southwark','haringey and islington','tower hamlets','hackney and newham'},
'outer london   east and north east' : {'enfield','barking   dagenham and havering','bexley and greenwich','redbridge and waltham forest'},
'outer london   south' : {'bromley','croydon','merton  kingston upon thames and sutton'},
'outer london   west and north west' : {'barnet','brent','ealing','hounslow and richmond upon thames','harrow and hillingdon'},
}
nuts_topdown['south east  england '] = {
'berkshire  buckinghamshire and oxfordshire' : {'berkshire','milton keynes','buckinghamshire','oxfordshire'},
'surrey  east and west sussex' : {'west sussex  north east ', 'west sussex  south west ', 'west surrey','east surrey','east sussex','brighton and hove' },
'hampshire and isle of wight' : { 'north hampshire', 'south hampshire','portsmouth','southampton','isle of wight','central hampshire'},
'kent' : {'west kent','medway','kent thames gateway','east kent','mid kent'},
}
nuts_topdown['south west  england '] = {
'gloucestershire  wiltshire and bath bristol area' : {'swindon','gloucestershire','wiltshire','bristol','bath and north east somerset  north somerset and south gloucestershire'},
'dorset and somerset' : {'bournemouth and poole','somerset', 'dorset'}, 
'cornwall and isles of scilly' : {'cornwall and isles of scilly'},
'devon' : {'plymouth','torbay', 'devon'}, 
}
nuts_topdown['wales'] = {
'west wales' : {'swansea','central valleys','bridgend and neath port talbot','gwent valleys','south west wales','conwy and denbighshire','gwynedd','isle of anglesey'},
'east wales' : {'powys','monmouthshire and newport','cardiff and vale of glamorgan','flintshire and wrexham'},
}
nuts_topdown['scotland'] = {
'eastern scotland' : {'west lothian','perth   kinross and stirling','falkirk','edinburgh','scottish borders','east lothian and midlothian','clackmannanshire and fife','angus and dundee city'},
'north eastern scotland' : {'aberdeen city and aberdeenshire'},
'southern scotland' : {'inverclyde  east renfrewshire and renfrewshire', 'south ayrshire', 'dumfries   galloway', 'east ayrshire and north ayrshire mainland', 'south lanarkshire'},
'west central scotland' : {'east dunbartonshire  west dunbartonshire and helensburgh   lomond','north lanarkshire','glasgow city'},
'highlands and islands' : {'orkney islands', 'shetland islands', 'na h eileanan siar  western isles ', 'lochaber  skye   lochalsh  arran   cumbrae and argyll   bute', 'inverness   nairn and moray  badenoch   strathspey', 'caithness   sutherland and ross   cromarty'}
}
nuts_topdown['northern ireland'] = {
'northern ireland' : {'causeway coast and glens','newry  mourne and down','mid ulster', 'mid and east antrim', 'lisburn and castlereagh', 'fermanagh and omagh', 'derry city and strabane', 'belfast', 'armagh city  banbridge and craigavon', 'antrim and newtownabbey', 'ards and north down'},
}


nuts2_bottomup = {}
nuts3_bottomup = {}
for n1 in nuts_topdown:
	for n2 in nuts_topdown[n1]:
		nuts2_bottomup[n2] = (n1)
		for n3 in nuts_topdown[n1][n2]:
			nuts3_bottomup[n3] = (n1, n2)

#s = {'causeway coast and glens','newry  mourne and down','mid ulster', 'mid and east antrim', 'lisburn and castlereagh', 'fermanagh and omagh', 'derry city and strabane', 'belfast', 'armagh city  banbridge and craigavon', 'antrim and newtownabbey', 'ards and north down'}
#for p in s:
#	poly = MultiPolygon( dbs.dbs["nuts3"].lookup(p) )
#	for n in dbs.dbs["nuts2"].names:
#		big = MultiPolygon( dbs.dbs["nuts2"].lookup(n) )
#		if big.intersects(poly):
#			print(p, n)
#			break;
#sys.exit(1);

def get_nuts(output, dbs):
	output["NUTS1"] = None
	output["NUTS2"] = None
	output["NUTS3"] = None
	if output["db"] == "nuts1":
		output["NUTS1"] = output["match_name"]
	elif output["db"] == "nuts2":
		output["NUTS1"] = nuts2_bottomup[ output["match_name"] ]
		output["NUTS2"] = output["match_name"]
	elif output["db"] == "nuts3":
		output["NUTS1"] = nuts3_bottomup[ output["match_name"] ][0]
		output["NUTS2"] = nuts3_bottomup[ output["match_name"] ][1]
		output["NUTS3"] = output["match_name"]
	elif output["db"] and output["db"] != "country":

		##Add something for bounding boxes one day, when we swap order of geonames with nominatim.
		pt = Point( output["lng"], output["lat"] )
		for n in dbs.dbs["nuts3"].names:
			if MultiPolygon( dbs.dbs["nuts3"].lookup(n) ).contains(pt):
				output["NUTS3"] = n
				break;
		if output["NUTS3"]:
			output["NUTS1"] = nuts3_bottomup[ output["NUTS3"] ][0]
			output["NUTS2"] = nuts3_bottomup[ output["NUTS3"] ][1]
		else:
			min_dist = None;
			output["NUTS3"] = None 
			for n in dbs.dbs["nuts3"].names:
				pn = MultiPolygon( dbs.dbs["nuts3"].lookup(n) )
				dist = pn.distance(pt)
				if not min_dist or dist < min_dist:
					min_dist = dist;
					output["NUTS3"] = n;
			output["NUTS1"] = nuts3_bottomup[ output["NUTS3"] ][0]
			output["NUTS2"] = nuts3_bottomup[ output["NUTS3"] ][1]
		
	
