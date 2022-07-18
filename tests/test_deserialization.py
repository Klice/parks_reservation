import json
import unittest

from models.maps_data import Map
from models.root_maps import RootMap


class TestDeserialization(unittest.TestCase):

    def test_maps_deserializtion(self):
        with open('tests/fixtures/maps.json') as f:
            s = json.load(f)
        maps = Map.schema().load(s, many=True)
        print(maps)

    def test_root_maps_deserializtion(self):
        with open('tests/fixtures/root_maps.json') as f:
            s = json.load(f)
        maps = RootMap.schema().load(s, many=True)
        print(maps)


if __name__ == '__main__':
    unittest.main()
