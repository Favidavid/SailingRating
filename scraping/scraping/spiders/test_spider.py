import scrapy
from scrapy import log
from scrapy.contrib.linkextractors import LinkExtractor
import scraping.items

class TestSpider(scrapy.Spider):
	name = "test"
	allowed_domains = ["scores.collegesailing.org/"]
	start_urls = [
		"http://scores.collegesailing.org/f14/icsa-singlehanded-champs-full/",
    ]
	def parse(self, response):
		log.msg(response, level=log.INFO)
		competitorsUrlLinkExtractor = LinkExtractor(restrict_xpaths=('//*[@id="menu"]'), allow=('.*/[A-E]/'))
		log.msg(competitorsUrlLinkExtractor, level=log.INFO)
		log.msg(competitorsUrlLinkExtractor.extract_links(response),level=log.INFO)
		print competitorsUrlLinkExtractor.extract_links(response)[0].text[-1]
		print response.xpath('//*[@id="page-content"]/div[2]/table/tbody/tr')[0].xpath('@class').extract()[0]
		print response.xpath('//*[@id="page-content"]/div[2]/table/tbody/tr[1]/td[contains(@class,"right")][5]/text()').extract()[0]
		print response.xpath('//*[@id="page-info"]/li[5]/span[2]/text()').extract()[0]
		competitorsLinksExtractor = LinkExtractor(restrict_xpaths=('//*[@id="menu"]'), allow=('.*/[A-E]/') )
		print competitorsLinksExtractor.extract_links(response)
		a = SchoolItem()
		yield a
		# log.msg(LinkExtractor(restrict_xpaths=('//*[@id="menu"]'), allow=('.*/[A-E]/'))[0], level=log.DEBUG)
		# log.msg(LinkExtractor(restrict_xpaths=('//*[@id="menu"]'), allow=('.*/[A-E]/').extract_links(), level=log.DEBUG)
		# log.msg(LinkExtractor(restrict_xpaths=('//*[@id="menu"]'), allow=('.*/[A-E]/')).extract_links()[0], level=log.DEBUG)

		# for division in LinkExtractor.extract_links(restrict_xpaths=('//*[@id="menu"]'), allow=('.*/[A-E]/')):
		# 	log.msg(division, level=log.DEBUG)

		# for sel in response.xpath('//tr[@class="divA"]'):
		# 	item = SchoolItem()
		# 	item['name'] = sel.xpath('td/a/text()').extract()
		# 	item['division'] = sel.xpath('td[4]/text()').extract()
		# 	yield item
