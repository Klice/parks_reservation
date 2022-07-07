import requests
import urllib.parse

from datetime import timedelta, datetime, date
from flask import Flask, make_response, jsonify
from flask_cors import CORS

api_url = "https://reservations.ontarioparks.com/api"

AVAILABILITY = {
	0: "Available",
	1: "Unavailable",
	6: "Restrictions",
	7: "Partial Availability",
}


exclude_parks = [
	-2147483540,
	-2147483531,
	-2147483572,
]

include_parks = [
	-2147483408,
	-2147483334
]

MAPS_DATA = None
ROOT_MAPS = None
WEEKENDS = None

api = Flask(__name__)
CORS(api)


def make_get_request(endpoint, params=None, headers=None):
	if params is None:
		params = {}
	if headers is None:
		headers = {}
	default_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"}
	default_headers.update(headers)

	ret = requests.get(f"{api_url}/{endpoint}", params=params, headers=default_headers)
	ret.raise_for_status()
	return ret.json()

def get_map_new(start_date, end_date, map_id):
	headers = {'Content-Type': 'application/json'}
	data = {
		"mapId": int(map_id),
		"bookingCategoryId":0,
		"startDate": date(start_date.year, start_date.month, start_date.day).isoformat(),
		"endDate": date(end_date.year, end_date.month, end_date.day).isoformat(),
		"isReserving":True,
		"getDailyAvailability":False,
		"partySize": 3,
		"equipmentCategoryId":-32768,
		"subEquipmentCategoryId":-32768,
		"generateBreadcrumbs": False,
		"resourceAccessPointId": None,
		"filterData": "[{\"attributeDefinitionId\":-32736,\"enumValues\":[1],\"attributeDefinitionDecimalValue\":0,\"filterStrategy\":1},{\"attributeDefinitionId\":-32726,\"enumValues\":[1],\"attributeDefinitionDecimalValue\":0,\"filterStrategy\":1}]"
	}

	return make_get_request('availability/map', data, headers)

def get_root_maps():
	ret = make_get_request('resourcelocation/rootmaps')
	return { str(r["mapId"]): r["resourceLocationLocalizedValues"]["en-CA"] for r in ret }

def get_res_cat():
	ret = make_get_request('resourcecategory')
	return { str(r["resourceLocationId"]): r["resourceLocationLocalizedValues"]["en-CA"] for r in ret }

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)


def get_holidays():
	ret = requests.get("https://canada-holidays.ca/api/v1/holidays")
	ret.raise_for_status()
	ret = ret.json()
	result = []
	for h in ret["holidays"]:
		for province in h["provinces"]:
			if province["id"] == "ON":
				result.append(datetime.fromisoformat(h["observedDate"]))
	return result

def get_weekends():
	holidays = get_holidays()
	start_date = next_weekday(date.today(), 4)
	result = []
	for i in range(5):
		result.append((
			start_date + timedelta(weeks=i),
			start_date + timedelta(weeks=i) + timedelta(days=2),			
		))
		if start_date + timedelta(weeks=i) + timedelta(days=3) in holidays:
			result.append((
				start_date + timedelta(weeks=i) + timedelta(days=1),
				start_date + timedelta(weeks=i) + timedelta(days=3),			
			))
	return result

def get_res_loc():
	ret = make_get_request('resourceLocation')
	results = {}
	for r in ret:
		short_name = ""
		for l in r["localizedValues"]:
			if l["cultureName"] ==  "en-CA":
				short_name = l["shortName"]
		results[str(r["resourceLocationId"])] = short_name

	return results

def get_from_map(mid, maps):
	mid = int(mid)
	for m in maps:
		if m["mapId"] == mid:
			return m["localizedValues"][0]["title"]

def get_maps():
	return make_get_request('maps')



def get_res_name(rid, data):
	for d in data:
		if rid in d:
			return d[str(rid)]
	print("Not found:"+ rid)
	return "Unknown"


def build_url(pid, cid, start_date, end_date):
	url = "https://reservations.ontarioparks.com/create-booking/results?"
	data = {
		"searchTabGroupId": 0,
		"mapId": int(pid),
		"bookingCategoryId": 0,
		"startDate": start_date.isoformat(),
		"endDate": end_date.isoformat(),
		"nights": 3,
		"isReserving": True,
		"equipmentId": -32768,
		"subEquipmentId": -32768,
		"partySize": 3,
		"searchTime": datetime.now().isoformat() + ".000",
		"resourceLocationId": int(cid),
	}
	return url + urllib.parse.urlencode(data)

@api.route('/', methods=['GET'])
def get_aval():
	result = []
	for start_date, end_date in WEEKENDS:
		weekend = {"start_date": start_date.isoformat(), "end_date": end_date.isoformat(), "parks": []}
		print(weekend) 
		parks = [ r for r, aval in get_map_new(start_date, end_date, -2147483461)["mapLinkAvailabilities"].items() if aval[0] == 0]
		for park_id in parks:
			if (int(park_id) in exclude_parks) or (include_parks and int(park_id) not in include_parks):
				continue
			park_to_add = {"name": ROOT_MAPS[park_id], "campgrounds": []}
			park_info = get_map_new(start_date, end_date, park_id)
			campgrounds = [p for p, a in park_info["mapLinkAvailabilities"].items() if a[0] == 0]
			for c in campgrounds:
				campground_to_add = {"name": get_from_map(c, MAPS_DATA), "url": build_url(c, c, start_date, end_date), "spots": []}
				spots_map = [s for s, aval in get_map_new(start_date, end_date, c)["resourceAvailabilities"].items() if aval[0]["availability"] == 0]
				for s in spots_map:
					campground_to_add["spots"].append(s)
				park_to_add["campgrounds"].append(campground_to_add)
			weekend["parks"].append(park_to_add)
		result.append(weekend)
	return make_response(jsonify(result), 200)


if __name__ == "__main__":
	MAPS_DATA = get_maps()
	ROOT_MAPS = get_root_maps()
	WEEKENDS = get_weekends()
	api.run(host="0.0.0.0", port=8111)
