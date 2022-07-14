import unittest
import reservations_api

from unittest import mock


class TestCoreLogic(unittest.TestCase):

    @mock.patch('reservations_api.exclude_parks', [])
    @mock.patch('reservations_api.include_parks', [])
    def test_empty_exclude_include_list(self):
        self.assertTrue(reservations_api.OntarioReservations._is_park_include(1))
        self.assertTrue(reservations_api.OntarioReservations._is_park_include(2))

    @mock.patch('reservations_api.exclude_parks', [1])
    @mock.patch('reservations_api.include_parks', [])
    def test_exclude_list(self):
        self.assertFalse(reservations_api.OntarioReservations._is_park_include(1))
        self.assertTrue(reservations_api.OntarioReservations._is_park_include(2))

    @mock.patch('reservations_api.exclude_parks', [])
    @mock.patch('reservations_api.include_parks', [1])
    def test_include_list(self):
        self.assertTrue(reservations_api.OntarioReservations._is_park_include(1))
        self.assertFalse(reservations_api.OntarioReservations._is_park_include(2))


if __name__ == '__main__':
    unittest.main()
