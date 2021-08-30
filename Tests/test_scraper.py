import unittest

from ..Scraper.functions import Airliners

class AirlinersTestCase(unittest.TestCase):
    def setUp(self):
        # self.scraper = Airliners()
        pass

    def test_lower_than(self):
        self.assertLess(5, 4)

    def tearDown(self):
        pass
        # del self.scraper