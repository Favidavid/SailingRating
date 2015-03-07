# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class RootItem(scrapy.Item):
	seasons = scrapy.Field()

class SeasonItem(scrapy.Item):
	season = scrapy.Field()

class RegattaItem(scrapy.Item):
  name = scrapy.Field()
  fullScores = scrapy.Field()
  competitors = scrapy.Field()

class DivisionItem(scrapy.Item):
  skippers = scrapy.Field()
  crews = scrapy.Field()