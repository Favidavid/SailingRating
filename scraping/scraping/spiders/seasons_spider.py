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

        #populate fullScoresItem
        fullScoresUrl = response.xpath('//*[@id="menu"]/li[4]/a/text()')
        regattaItem['fullScores'] = scrapy.Request(fullScoresUrl,callback=self.parse_full_scores)


        #populate competitorsItem
        competitorsLinks = LinkExtractor(restrict_xpaths=('//*[@id="menu"]'), allow=('.*/[A-E]/') ).extractLinks(response)
        competitors = dict()
        #singlehanded regatta
        if (len(competitorsLinks) == 0):
            regattaItem['competitors'] = parse_singlehanded_competitors(response)
        
        #division regattas, could be single division
        else:
            for divisionLink in competitorsLinks:
                divisionCompetitors = scrapy.Request(divisionLink.url,callback=self.parse_division)
                #divisionLink.text[-1] gets the division letter from link text. Used as keys for competitors item
                div = 'div'+divisionLink.text[-1]
                competitors[div] = divisionCompetitors
        regattaItem['competitors'] = competitorsItem

        yield regattaItem
    
    def parse_full_scores(self, response):
        regatta = items.RegattaItem()
        regatta['name']=response.xpath('//*[@id="content-header"]/h1/span[2]/text()').extract()[0]
        fullScores = dict()
        lastdivision = self.lastDivision(response)
        currentSchool = None
        for row in response.xpath('//*[contains(@class,"results coordinate")]/tbody/tr'):
            divClass = row.xpath('@class').extract()[0]
            if ('div' in divClass):
                if (divClass == 'divA'): 
                    schoolScore = dict()
                    currentSchool = row.xpath('td[3]/a/text()').extract()[0]
                    schoolScore['school'] = currentSchool
                    schoolScore[ divClass ] = self.parse_division_score(row)## list of A division results
                else:
                    schoolScore[ divClass ] = self.parse_division_score(row)
                if (row.xpath('@class').extract()[0]==lastdivision ): 
                    fullScores[currentSchool] = schoolScore
        regatta['fullScores']=fullScores
        regatta['competitors']=dict()
        return fullScores

    def parse_division_score(self, row):
        results = []
        columns = row.xpath('td[contains(@class,"right")]')
        for column in columns:
            results.append(column.xpath('text()').extract()[0])
        return results

    def lastDivision(self, response):
        divisionsText = response.xpath('//*[@id="page-info"]/li[5]/span[2]/text()').extract()[0]
        if (divisionsText == '2 Divisions' or divionsText == 'combined'):
            return 'divB'
        elif (divisionsText == '3 Divisions'):
            return 'divC'
        elif (divisionsText == 'Singlehanded' or divisionsText == '1 Division'):
            return 'divA'
        elif (divisionsText == '4 Divisions'):
            return 'divD'
        else:
            return 'divB'

    def parse_division(self, response):
        competitors = dict()
        currentSchool = None
        for row in response.xpath('//*[contains(@class,"results coordinate")]/tbody/tr'):
            rowClass = row.xpath('@class').extract()[0]
            if ('topborder' in rowClass): 
                schoolCompetitors = dict({'skipper':dict(),'crew':dict()})
                currentSchool = row.xpath('*[contains(@class,"schoolname")]/a/text()').extract()[0]
                schoolCompetitors['school'] = currentSchool
            position = row.xpath('*[contains(@class,"sailor-name")]/@class').extract()[0][12:]
            racesSailed = row.xpath('*[contains(@class,"races")]/text()').extract()
            sailorName = row.xpath('*[contains(@class,"sailor-name")]/text()').extract()[0]
            if (len(racesSailed) == 0):
                schoolCompetitors[position][sailorName] = u''
            else:
                schoolCompetitors[position][sailorName] = racesSailed[0]
            ## if last row of competitors (no following siblings)
            if (len(row.xpath('following-sibling::tr[1]').extract() ) == 0):
                competitors[currentSchool] = schoolCompetitors
            elif ('topborder' in row.xpath('following-sibling::tr[1]/@class').extract()[0]): 
                competitors[currentSchool] = schoolCompetitors
        return competitors

    def parse_singlehanded_division():
        print ''