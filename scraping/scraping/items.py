# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class RegattaItem(scrapy.Item):
    name = scrapy.Field()
    fullScores = scrapy.Field()
    competitors = scrapy.Field()

class DivisionItem(scrapy.Item):
    skippers = scrapy.Field()
    crews = scrapy.Field()