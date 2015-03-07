import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy import log #todo find out this import syntax
import scraping.items as items
import lxml.html

class TestSpider(scrapy.Spider):
  name = "test"
  allowed_domains = ["scores.collegesailing.org/"]
  start_urls = [
    "http://scores.collegesailing.org/f14/navy-fall-women/",
  ]
  
  def parse(self, response):
    regattaItem = items.RegattaItem()
    regattaItem['name'] = response.xpath('//*[@id="content-header"]/h1/span[2]/text()').extract()[0]
    print regattaItem['name']
    fullScoresLink = LinkExtractor(restrict_xpaths = ('//*[@id="menu"]'), allow = ('.*/full-scores/') ).extract_links(response)[0]
    lxmlResponse = lxml.html.parse(fullScoresLink.url)
    htmlbody = lxml.html.tostring(lxmlResponse)
    fullScoresResponse = scrapy.http.HtmlResponse(url = fullScoresLink.url, body = htmlbody)
    regattaItem['fullScores'] = self.parse_full_scores(fullScoresResponse)


    #populate competitorsItem
    competitorsLinks = LinkExtractor(restrict_xpaths = ('//*[@id="menu"]'), allow = ('.*/[A-E]/') ).extract_links(response)
    competitors = dict()
    #singlehanded regatta
    if (len(competitorsLinks) == 0):
      regattaItem['competitors'] = self.parse_singlehanded_competitors(response)

    #division regattas, could be single division
    else:
      for divisionLink in competitorsLinks:
        lxmlResponse = lxml.html.parse(divisionLink.url)
        htmlbody = lxml.html.tostring(lxmlResponse)
        divisionCompetitorsResponse = scrapy.http.HtmlResponse(url = divisionLink.url, body = htmlbody)
        divisionCompetitors = self.parse_competitors_division(divisionCompetitorsResponse)
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
    divisionsText = response.xpath('//*[@id="page-info"]/li[5]/span[2]/text()').extract()[0]
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
    print response.url
    for row in response.xpath('//*[contains(@class,"results coordinate")]/tbody/tr'):
      rowClass = row.xpath('@class').extract()[0]
      if ('topborder' in rowClass): 
        schoolCompetitors = dict({'skipper':dict(),'crew':dict()})
        currentSchool = row.xpath('*[contains(@class,"schoolname")]/a/text()').extract()[0]
        schoolCompetitors['school'] = currentSchool
      positionXpath = row.xpath("*[contains(@class,'sailor-name')]/@class").extract()
      if (len(positionXpath) == 0):
        continue
      else:
        position = positionXpath[0][12:]
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
