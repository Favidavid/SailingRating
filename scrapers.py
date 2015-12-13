from scrapy.contrib.linkextractors import LinkExtractor
import lxml.html

def scrape_season(response):
  season = dict()
  currentWeek = None
  for row in response.xpath('//*[@id="page-content"]/div[2]/table/tbody/tr'):
    if len(row.xpath('@class').extract()) == 0:
      weekName = row.xpath('th/text()').extract()[0]
      season[weekName] = dict()
      print weekName
    else:
      regattaType = row.xpath('td[4]/text()').extract()
      if len(regattaType) != 0:
        if regattaType[0] in allowedTypes:
          regattaName = row.xpath('td[1]/a/text()').extract()[0]
          href = row.xpath('td[1]/a/@href').extract()[0]
          regattaUrl = response.url + href
          season[weekName][regattaName] = scrape_regatta(getResponse(regattaUrl))
  return season

def scrape_week(response):
  week = dict()
  for regatta in response.xpath():
    week[regattaName] = scrape_regatta(regatta)
  return week

def scrape_regatta(regatta_url):
  response = getResponse(regatta_url)

  xpathRegattaName = '//*[@id="content-header"]/h1/span[2]/text()'
  xpathRegattaHost = '//*[@id="page-info"]/li[1]/span[2]/span/text()'
  xpathRegattaDate = '//*[@id="page-info"]/li[2]/span[2]/time/text()'
  xpathRegattaTier = '//*[@id="page-info"]/li[3]/span[2]/span/text()'
  xpathRegattaBoat = '//*[@id="page-info"]/li[4]/span[2]/text()'
  xpathRegattaScoring = '//*[@id="page-info"]/li[5]/span[2]/text()'
  xpathRegattaSummary = '//*[@id="summary"]/descendant::*/text()'
  xpathFullScoresUrl = '//*[@id="menu"]'
  xpathReportSchoolRow = '//*[@id="page-content"]/div[3]/table[1]/tbody/tr'
  xpathReportSchoolName = 'td[4]/a/span/text()'
  xpathReportSchoolFinishPlace = 'td[2]/text()'
  regatta = dict()
  regatta['url'] = regatta_url
  regatta['name'] = response.xpath( xpathRegattaName ).extract()[0]
  regatta['host'] = response.xpath( xpathRegattaHost ).extract()[0]
  regatta['date'] = response.xpath( xpathRegattaDate ).extract()[0]
  regatta['tier'] = response.xpath( xpathRegattaTier ).extract()[0]
  regatta['boat'] = response.xpath( xpathRegattaBoat ).extract()[0]
  regatta['scoring'] = response.xpath( xpathRegattaScoring ).extract()[0]
  regatta['summary'] = response.xpath( xpathRegattaSummary ).extract()[0]

  fullScoresLink = LinkExtractor(restrict_xpaths = ( xpathFullScoresUrl ), allow = ('.*/full-scores/') ).extract_links(response)[0]
  fullScoresResponse = getResponse(fullScoresLink.url)

  #mapping of places to school
  places = dict()
  for row in response.xpath( xpathReportSchoolRow ):
    school = row.xpath( xpathReportSchoolName ).extract()[0]
    place = row.xpath( xpathReportSchoolFinishPlace ).extract()[0]
    places[school] = place
  regatta['places'] = places

  #populate fullScores (works for singlehanded as well)
  regatta['fullScores'] = scrape_full_scores(fullScoresResponse)

  #populate competitors
  competitorsLinks = LinkExtractor(restrict_xpaths = ('//*[@id="menu"]'), allow = ('.*/[A-E]/') ).extract_links(response)
  #singlehanded regatta competitors
  if len(competitorsLinks) == 0:
    competitors = dict()
    competitors['divA'] = scrape_singlehanded_competitors_division(response)
    regatta['competitors'] = competitors
  #division regattas, could be single division
  else:
    competitors = dict()
    for divisionLink in competitorsLinks:
      divisionCompetitorsResponse = getResponse(divisionLink.url)
      divisionCompetitors = scrape_competitors_division(divisionCompetitorsResponse)
      #divisionLink.text[-1] gets the division letter from link text. Used as keys for competitors item
      div = 'div' + divisionLink.text[-1]
      competitors[div] = divisionCompetitors
    regatta['competitors'] = competitors
  return regatta

def scrape_full_scores(response):
  fullScores = dict()
  lastdivision = lastDivision(response)
  currentSchool = None
  currentPlace = '1'
  numberOfRaces = response.xpath('//*[contains(@class,"results coordinate")]/thead/tr/th[last()-2]/text()').extract()[0]
  fullScores['numberOfRaces'] = numberOfRaces
  for row in response.xpath('//*[contains(@class,"results coordinate")]/tbody/tr'):
    divClass = row.xpath('@class').extract()[0]
    if 'div' in divClass:
      if divClass == 'divA':
        schoolScore = dict()
        currentSchool = row.xpath('td[3]/a/text()').extract()[0]
        currentPlace = row.xpath('td[2]/text()').extract()[0]
        schoolScore[ 'name' ] = currentSchool
        schoolScore[ divClass ] = scrape_division_score(row)## list of A division results
      else:
        schoolScore[ divClass ] = scrape_division_score(row)
      if row.xpath('@class').extract()[0] == lastdivision:
        fullScores[currentPlace] = schoolScore
  return fullScores

def scrape_singlehanded_results(response):
  fullScores = dict()
  fullScores['divA'] = dict()
  lastdivision = lastDivision(response)
  currentSchool = None
  currentPlace = '1'
  numberOfRaces = response.xpath('//*[contains(@class,"results coordinate")]/thead/tr/th[last()-2]/text()').extract()[0]
  fullScores['numberOfRaces'] = numberOfRaces
  for row in response.xpath('//*[contains(@class,"results coordinate")]/tbody/tr'):
    divClass = row.xpath('@class').extract()[0]
    if divClass == 'divA':
      schoolScore = dict()
      currentSchool = row.xpath('td[3]/a/text()').extract()[0]
      currentPlace = row.xpath('td[2]/text()').extract()[0]
      schoolScore['name'] = currentSchool
      schoolScore[ 'divA' ] = scrape_division_score(row)## list of A division results
      fullScores[currentPlace] = schoolScore
  return fullScores

def scrape_division_score(row):
  results = []
  columns = row.xpath('td[contains(@class,"right")]')
  for column in columns:
    columnText = column.xpath('text()').extract()[0]
    letterScores = column.xpath('@title').extract()[0]
    if letterScores:
      columnText+=':letters:'+letterScores
    results.append(columnText)
  return results

def lastDivision(response):
  divisionsText = response.xpath('//*[@id="page-info"]/li[5]/span[2]/text()').extract()[0]
  if divisionsText == '2 Divisions':
    return 'divB'
  elif divisionsText == '3 Divisions':
    return 'divC'
  elif divisionsText == 'Singlehanded' or divisionsText == '1 Division':
    return 'divA'
  elif divisionsText == '4 Divisions':
    return 'divD'
  else:
    return 'divB'

def scrape_competitors_division(response):
  competitorsDivision = dict()
  currentSchool = None
  currentPlace = '1'
  for row in response.xpath('//*[contains(@class,"results coordinate")]/tbody/tr'):
    rowClass = row.xpath('@class').extract()[0]
    if 'topborder' in rowClass:
      schoolCompetitors = dict({'skipper':dict(),'crew':dict()})
      currentSchool = row.xpath('*[contains(@class,"schoolname")]/a/text()').extract()[0]
    positionXpath = row.xpath("*[contains(@class,'sailor-name')]/@class").extract()
    if len(positionXpath) > 0:
      position = positionXpath[0][12:]
      racesSailed = row.xpath('*[contains(@class,"races")]/text()').extract()
      sailorName = row.xpath('*[contains(@class,"sailor-name")]/text()').extract()[0]
      if len(racesSailed) == 0:
        schoolCompetitors[position][sailorName] = u''
      else:
        schoolCompetitors[position][sailorName] = racesSailed[0]
    ## if last row of competitors (no following siblings)
    if len(row.xpath('following-sibling::tr[1]').extract() ) == 0:
      competitorsDivision[currentSchool] = schoolCompetitors
    elif 'topborder' in row.xpath('following-sibling::tr[1]/@class').extract()[0]:
      competitorsDivision[currentSchool] = schoolCompetitors
  return competitorsDivision

def scrape_singlehanded_competitors_division(response):
  competitorsDivision = dict()
  for row in response.xpath('//*[contains(@class,"results coordinate")]/tbody/tr'):
    sailorName = row.xpath('*[contains(@class,"teamname")]/text()').extract()[0]
    currentSchool = row.xpath('*[contains(@class,"schoolname")]/a/span/text()').extract()[0]
    competitorsDivision[currentSchool] = dict({'skipper':dict(),'crew':dict()})
    competitorsDivision[currentSchool]['skipper'][sailorName] = u''
  return competitorsDivision



def getResponse(url):
  lxmlResponse = lxml.html.parse(url)
  htmlbody = lxml.html.tostring(lxmlResponse)
  response = scrapy.http.HtmlResponse(url = url, body = htmlbody)
  return response