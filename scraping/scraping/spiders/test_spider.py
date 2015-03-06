import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy import log #todo find out this import syntax
import scraping.items as items
import urllib2

class TestSpider(scrapy.Spider):
    name = "test"
    allowed_domains = ["scores.collegesailing.org/"]
    start_urls = [
        "http://scores.collegesailing.org/f14/navy-fall-women/",
    ]
    
    def parse(self, response):
        regattaItem = items.RegattaItem()
        regattaItem['name']=response.xpath('//*[@id="content-header"]/h1/span[2]/text()').extract()[0]
        print regattaItem['name']
        #populate fullScoresItem
        fullScoresLink = LinkExtractor(restrict_xpaths=('//*[@id="menu"]'), allow=('.*/full-scores/') ).extract_links(response)[0]
        # fullScoresRequest = scrapy.Request(fullScoresLink.url,self.parse_full_scores)
        # print fullScoresRequest.body
        html = urllib2.urlopen(fullScoresLink.url).read()
        # print html
        fullScoresResponse = scrapy.http.HtmlResponse(url=fullScoresLink.url, body=html)
        print fullScoresResponse
        regattaItem['fullScores'] = []


        #populate competitorsItem
        competitorsLinks = LinkExtractor(restrict_xpaths=('//*[@id="menu"]'), allow=('.*/[A-E]/') ).extract_links(response)
        competitors = dict()
        #singlehanded regatta
        if (len(competitorsLinks) == 0):
            regattaItem['competitors'] = parse_singlehanded_competitors(response)

        #division regattas, could be single division
        else:
            for divisionLink in competitorsLinks:
                divisionCompetitors = scrapy.Request(divisionLink.url,callback=self.parse_competitors_division)
                #divisionLink.text[-1] gets the division letter from link text. Used as keys for competitors item
                div = 'div'+divisionLink.text[-1]
                competitors[div] = divisionCompetitors
        regattaItem['competitors'] = competitors

        yield regattaItem

    def parse_full_scores(self, response):
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
        return fullScores

    def parse_division_score(self, row):
        results = []
        columns = row.xpath('td[contains(@class,"right")]')
        for column in columns:
            results.append(column.xpath('text()').extract()[0])
        return results

    def lastDivision(self, response):
        divisionsText = response.xpath('//*[@id="page-info"]/li[5]/span[2]/text()').extract()
        print divisionsText
        if (divisionsText == '2 Divisions'):
            return 'divB'
        elif (divisionsText == '3 Divisions'):
            return 'divC'
        elif (divisionsText == 'Singlehanded' or divisionsText == '1 Division'):
            return 'divA'
        elif (divisionsText == '4 Divisions'):
            return 'divD'
        else:
            return 'divB'

    def parse_competitors_division(self, response):
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
        competitors = dict()
        for row in response.xpath('//*[contains(@class,"results coordinate")]/tbody/tr'):
            sailorName = row.xpath('*[contains(@class,"teamname")]/text()').extract()[0]
            currentSchool = row.xpath('*[contains(@class,"schoolname")]/a/span/text()').extract()[0]
            competitor = dict()
            competitor['name'] = sailorName
            competitor['school'] = currentSchool
            competitors[sailorName] = competitor
        return competitors

    def parse_singlehanded_results():
        fullScores = dict()
        lastdivision = self.lastDivision(response)
        currentSchool = None
        for row in response.xpath('//*[contains(@class,"results coordinate")]/tbody/tr'):
            divClass = row.xpath('@class').extract()[0]
            print divClass
            if (divClass == 'divA'):
                schoolScore = dict()
                currentSailor = row.xpath('td[3]/text()').extract()[0]
                currentSchool = row.xpath('td[3]/a/text()').extract()[0]
                schoolScore['school'] = currentSchool
                schoolScore[ 'scores' ] = self.parse_division_score(row)## list of A division results
                fullScores[currentSailor] = schoolScore
        return fullScores
