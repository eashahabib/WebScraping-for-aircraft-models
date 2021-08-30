import unittest
import sys
sys.path.insert(0, "C:\\Users\\easha\\AiCore Folders\\Project\\Scraper")

from functions import Airliners
from functions import Aircraftbluebook
from functions import Contentzone

"""The following tests make sure all classes are returning dictionaries. """

class AirlinersTestCase(unittest.TestCase):
    def setUp(self):
        self.scraper = Airliners()

    def test_get_data(self):
        test_dict = self.scraper.get_data()
        self.assertTrue(type(test_dict)==dict)

    def tearDown(self):
        self.scraper.housekeeping()

class AircraftbluebookTestCase(unittest.TestCase):
    def setUp(self):
        self.scraper = Aircraftbluebook()

    def test_get_data(self):
        test_dict = self.scraper.get_data()
        self.assertTrue(type(test_dict)==dict)

    def tearDown(self):
        self.scraper.housekeeping()


class ContentzoneTestCase(unittest.TestCase):
    def setUp(self):
        self.scraper = Contentzone()

    def test_get_data(self):
        test_dict = self.scraper.get_data()
        self.assertTrue(type(test_dict)==dict)

    def tearDown(self):
        self.scraper.housekeeping()