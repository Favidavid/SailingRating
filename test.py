import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy import log #todo find out this import syntax
import scraping.items as items
import lxml.html

class TestSpider(scrapy.Spider):
    name = "dbtest"
    allowed_domains = ["scores.collegesailing.org/"]
    start_urls = [
        "http://scores.collegesailing.org/s14/gill-national-finals/A/",
    ]
    
    def parse(self, response):
        for row in response.xpath('//*[@class="schoolname"]/a'):
            row.xpath('text()').extract()[0]
            
