import scrapy
from scrapy import log
from scrapy.contrib.linkextractors import LinkExtractor
import scraping.items as items
from scrapy.http import HtmlResponse

class TestSpider(scrapy.Spider):
    name = "test"
    allowed_domains = ["scores.collegesailing.org/"]
    start_urls = [
        "http://scores.collegesailing.org/f14/",
    ]
    
    def parse(self, response):
        regatta = items.RegattaItem()
        currentWeek = None
        for row in response.xpath('//*[@id="page-content"]/div[2]/table/tbody/tr'):
            if (len(row.xpath('@class').extract()) == 0):
                ##weekName = row.xpath('th/text()').extract()[0]

            else:
                ##season[weekName] = ''#parse_week(week)
        print '---------------------------------------------------------------------------------'
        regatta['competitors']=dict()
        regatta['fullScores']=dict()
        return regatta

    def parse_division_score(self, row):
        results = []
        columns = row.xpath('td[contains(@class,"right")]')
        for column in columns:
            results.append(column.xpath('text()').extract()[0])
        return results

    def lastDivision(self, response):
        divisionsText = response.xpath('//*[@id="page-info"]/li[5]/span[2]/text()').extract()[0]
        if (divisionsText == '2 Divisions' or divisionsText == 'combined'):
            return 'divB'
        elif (divisionsText == '3 Divisions'):
            return 'divC'
        elif (divisionsText == 'Singlehanded' or divisionsText == '1 Division'):
            return 'divA'
        elif (divisionsText == '4 Divisions'):
            return 'divD'
        else:
            return 'divB'



    def parse_season(self, response):
        season = dict()
        return season





    def parse_dude(self, response):
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
        #     log.msg(division, level=log.DEBUG)

        # for sel in response.xpath('//tr[@class="divA"]'):
        #     item = SchoolItem()
        #     item['name'] = sel.xpath('td/a/text()').extract()
        #     item['division'] = sel.xpath('td[4]/text()').extract()
        #     yield item
