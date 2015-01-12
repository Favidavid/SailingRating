# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class SeasonItem(scrapy.Item):

class WeekItem(scrapy.Item):

class RegattaItem(scrapy.Item):
	fullScores = scrapy.field()
	competitors = scrapy.field()

class FullScoresItem(scrapy.Item):


class ComptetitorsItem(scrapy.Item):
	