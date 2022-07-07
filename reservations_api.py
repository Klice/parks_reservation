import json
import logging
import requests
import urllib.parse

from datetime import timedelta, datetime, date
from enum import IntEnum

logger = logging.getLogger(__name__)


class Availability(IntEnum):
    AVAILABLE = 0
    UNAVAILABLE = 1
    RESTRICTIONS = 6
    PARTIAL_AVAILABILITY = 7


EQUIPMENT_ID = -32768
PARTY_SIZE = 3


class SubEquipment(IntEnum):
    SINGLE_TENT = -32768
    TWO_TENTS = -32767
    THREE_TENTS = -32766
    RV_TO_18FT = -32765
    RV_TO_25FT = -32764
    RV_TO_32FT = -32763
    RV_OVER_32FT = -32762


exclude_parks = [
    -2147483540,
    -2147483531,
    -2147483572,
]

# include_parks = []

include_parks = [
    -2147483408,  # Long Point
    -2147483334   # Pinary
]


class OntarioReservations():
    api_url = "https://reservations.ontarioparks.com/api"

    MAPS_DATA = None
    ROOT_MAPS = None
    WEEKENDS = None

    def __init__(self):
        self.MAPS_DATA = self._get_maps()
        self.ROOT_MAPS = self._get_root_maps()
        self.WEEKENDS = self._get_weekends()

    @classmethod
    def _make_get_request(cls, endpoint, params=None, headers=None):
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
        }
        default_headers.update(headers)

        ret = requests.get(f"{cls.api_url}/{endpoint}",
                           params=params, headers=default_headers)
        ret.raise_for_status()
        return ret.json()

    @classmethod
    def _get_map_new(cls, start_date, end_date, map_id):
        headers = {'Content-Type': 'application/json'}
        data = {
            "mapId": int(map_id),
            "bookingCategoryId": 0,
            "startDate": date(start_date.year, start_date.month, start_date.day).isoformat(),
            "endDate": date(end_date.year, end_date.month, end_date.day).isoformat(),
            "isReserving": True,
            "getDailyAvailability": False,
            "partySize": PARTY_SIZE,
            "equipmentCategoryId": EQUIPMENT_ID,
            "subEquipmentCategoryId": SubEquipment.SINGLE_TENT.value,
            "generateBreadcrumbs": False,
            "resourceAccessPointId": None,
            "filterData": json.dumps([{
                "attributeDefinitionId": -32736,
                "enumValues": [1],
                "attributeDefinitionDecimalValue": 0,
                "filterStrategy": 1
            }])
        }
        return cls._make_get_request('availability/map', data, headers)

    @classmethod
    def _get_root_maps(cls):
        ret = cls._make_get_request('resourcelocation/rootmaps')
        return {str(r["mapId"]): r["resourceLocationLocalizedValues"]["en-CA"] for r in ret}

    @staticmethod
    def _next_weekday(d, weekday):
        days_ahead = weekday - d.weekday()
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        return d + timedelta(days_ahead)

    @staticmethod
    def _get_holidays():
        ret = requests.get("https://canada-holidays.ca/api/v1/holidays")
        ret.raise_for_status()
        ret = ret.json()
        result = []
        for h in ret["holidays"]:
            for province in h["provinces"]:
                if province["id"] == "ON":
                    result.append(datetime.fromisoformat(h["observedDate"]))
        return result

    @classmethod
    def _get_weekends(cls):
        holidays = cls._get_holidays()
        start_date = cls._next_weekday(date.today(), 4)
        result = []
        for i in range(2):
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

    def _get_from_map(self, mid):
        mid = int(mid)
        for m in self.MAPS_DATA:
            if m["mapId"] == mid:
                return m["localizedValues"][0]["title"]

    @classmethod
    def _get_maps(cls):
        return cls._make_get_request('maps')

    @staticmethod
    def _build_url(pid, cid, start_date, end_date):
        url = "https://reservations.ontarioparks.com/create-booking/results?"
        data = {
            "searchTabGroupId": 0,
            "mapId": int(pid),
            "bookingCategoryId": 0,
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "nights": (end_date - start_date).days,
            "isReserving": True,
            "equipmentId": EQUIPMENT_ID,
            "subEquipmentId": SubEquipment.SINGLE_TENT.value,
            "partySize": PARTY_SIZE,
            "searchTime": datetime.now().isoformat() + ".000",
            "resourceLocationId": int(cid),
        }
        return url + urllib.parse.urlencode(data)

    def get_avail(self):
        result = []
        for start_date, end_date in self.WEEKENDS:
            weekend = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "parks": []
            }
            parks = self._get_park_availabilities(
                start_date,
                end_date,
                -2147483461  # Ontario South
            )
            for park_id in [p for p in parks if self._is_park_include(p)]:
                park_to_add = {
                    "name": self.ROOT_MAPS[park_id],
                    "campgrounds": []
                }
                campgrounds = self._get_park_availabilities(
                    start_date, end_date, park_id)
                for c in campgrounds:
                    park_to_add["campgrounds"].append(
                        self._get_campground(c, start_date, end_date))
                weekend["parks"].append(park_to_add)
            logger.info(weekend)
            result.append(weekend)
        return result

    @staticmethod
    def _is_park_include(park_id: int) -> bool:
        return (park_id not in exclude_parks) and (not include_parks or park_id in include_parks)

    def _get_campground(self, camp_id, start_date, end_date):
        campground = {
            "name": self._get_from_map(camp_id),
            "url": self._build_url(camp_id, camp_id, start_date, end_date),
            "spots": []
        }
        spots_map = self._get_park_availabilities(
            start_date,
            end_date,
            camp_id,
            "resourceAvailabilities"
        )
        for s in spots_map:
            campground["spots"].append(s)
        return campground

    def _get_park_availabilities(self, start_date, end_date, park_id, res_type="mapLinkAvailabilities"):
        res = []
        for r, avail in self._get_map_new(start_date, end_date, park_id)[res_type].items():
            if avail[0] == Availability.AVAILABLE:
                res.append(r)
        return res
