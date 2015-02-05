# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class RegattaItem(scrapy.Item):
	fullScores = dict()
	competitors = dict()

class DivisionItem(scrapy.Item):
	skippers = dict()
	crews = dict()