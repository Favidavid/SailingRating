import unittest
import scrapers

ACTON_UP = "./test/acton_up.txt"


class TestScrapers(unittest.TestCase):
    def test_scrape_week(self):
        # Last Week
        preset_regatta_urls = {'Rose Bowl': {'url': 'http://scores.collegesailing.org/f15/rose-bowl',
                                             'status': 'Official', 'scoring': '2 Divisions'},
                               'Sugar Bowl': {'url': 'http://scores.collegesailing.org/f15/sugar-bowl',
                                              'status': 'Official', 'scoring': '2 Divisions'}}
        week = scrapers.scrape_week('http://scores.collegesailing.org/f15/', 18)
        print(week)
        self.assertEqual(18, week['number'], 'Week 18 Number incorrect')
        self.assertEqual(preset_regatta_urls, week['regatta_urls'], 'Week 18 regattas are wrong')

        # First Week
        preset_regatta_urls = {'Teach Memorial': {'url': 'http://scores.collegesailing.org/f15/teach',
                                                  'status': 'Official', 'scoring': 'Combined'}}
        week = scrapers.scrape_week('http://scores.collegesailing.org/f15/', 1)
        self.assertEqual(1, week['number'], 'Week 1 Number incorrect')
        self.assertEqual(preset_regatta_urls, week['regatta_urls'], 'Week 1 regattas are wrong')

    def test_scrape_acton_up(self):
        with open(ACTON_UP, 'r') as my_file:
            data = my_file.read()
        acton_up_dict = scrapers.scrape_regatta('http://scores.collegesailing.org/f15/acton-up')
        self.assertEqual(data, acton_up_dict)
if __name__ == '__main__':
    unittest.main()
