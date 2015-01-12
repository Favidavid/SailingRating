import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy import log #todo find out this import syntax
import scraping.items

class seasons(CrawlSpider):
    name = 'seasons'
    allowed_domains = ['scores.collegesailing.org']
    start_urls = ['scores.collegesailing.org/seasons']

##todo: group regattas into weeks, and then into seasons, to keep things chronological. probably getting rid of crawl spider
##because we can define the rules and have more freedom with extracted links, like in parse_regatta with competitorsLinksExtractor
    rules = (
        # and follow links from them (since no callback means follow=True by default).
        Rule(LinkExtractor(restrict_xpaths=('//*[@id="page-info"]') ) ),

        # Extract links within xpath and parse them with the spider's method parse_item
        Rule(LinkExtractor(restrict_xpaths=('//*[@id="page-content"]/div[2]/table/tbody') ), callback='parse_regatta'),
    )

    def parse_regatta(self, response):
        regattaItem = RegattaItem()

        
        fullScoresUrl = response.xpath('//*[@id="menu"]/li[4]/a/text()')
        fullScoresItem = scrapy.Request(fullScoresUrl,callback=self.parse_full_scores)
        retattaItem['fullScores'] = fullScoresItem


        #extract competitors division links, parse them, and add them to regattaItem as a competitorsItem
        competitorsItem = CompetitorsItem()
        competitorsLinksExtractor = LinkExtractor(restrict_xpaths=('//*[@id="menu"]'), allow=('.*/[A-E]/') )
        for divisionLink in competitorsLinksExtractor.extract_links(response):
            divisionItem = scrapy.Request(divisionLink.url,callback=self.parse_division)
            #divisionLink.text[-1] gets the division letter from link text. Used as keys for competitors item
            competitorsItem[divisionLink.text[-1]] = divisionItem
        regattaItem['competitors'] = competitorsItem


        yield regattaItem

    
    def parse_full_scores(self, response):
        fullScores = FullScoresItem()
        currentSchool = None
        for row in response.xpath('//*[@id="page-content"]/div[2]/table/tbody/tr'):
            if (row.xpath('@class').extract()[0].equals('divA') ): 
                currentSchool = row.xpath('td[3]/a/text()')
                scoreSchool = scoreSchoolItem()
                scoreSchool['school'] = currentSchool
                scoreSchool['divA'] = ## list of A division results
            if (row.xpath('@class').extract()[0].equals(lastDivision) ): ############todo: last division
                fullScores[currentSchool] = scoreSchool ##have to decide if using team placing (ie 1 or 2 or 3 etc) or schoolname as key
        yield fullScores



    def parse_school_score(self, response):

    def parse_division(self, response):


