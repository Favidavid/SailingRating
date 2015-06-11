from scrapy.contrib.linkextractors import LinkExtractor
import lxml.html
import scrapy



def parse_season(response):
  season = dict()
  currentWeek = None
  for row in response.xpath('//*[@id="page-content"]/div[2]/table/tbody/tr'):
    if (len(row.xpath('@class').extract()) == 0):
      weekName = row.xpath('th/text()').extract()[0]
      season[weekName] = dict()
      print weekName
    else:
      regattaType = row.xpath('td[4]/text()').extract()
      if (len(regattaType) != 0):
        if (regattaType[0] in allowedTypes):
          regattaName = row.xpath('td[1]/a/text()').extract()[0]
          href = row.xpath('td[1]/a/@href').extract()[0]
          regattaUrl = response.url + href
          season[weekName][regattaName] = parse_regatta(getResponse(regattaUrl))
  return season

def parse_week(response):
  week = dict()
  for regatta in response.xpath():
    week[regattaName] = parse_regatta(regatta)
  return week

def parse_regatta(response):
  print('parse regatta')
  regatta = dict()
  regatta['name'] = response.xpath('//*[@id="content-header"]/h1/span[2]/text()').extract()[0]
  print regatta['name']
  fullScoresLink = LinkExtractor(restrict_xpaths = ('//*[@id="menu"]'), allow = ('.*/full-scores/') ).extract_links(response)[0]
  fullScoresResponse = getResponse(fullScoresLink.url)
  regatta['fullScores'] = parse_full_scores(fullScoresResponse)

  #populate competitorsItem
  competitorsLinks = LinkExtractor(restrict_xpaths = ('//*[@id="menu"]'), allow = ('.*/[A-E]/') ).extract_links(response)
  competitors = dict()
  #singlehanded regatta
  if (len(competitorsLinks) == 0):
    regattaItem['competitors'] = parse_singlehanded_competitors(response)

  #division regattas, could be single division
  else:
    for divisionLink in competitorsLinks:
      divisionCompetitorsResponse = getResponse(divisionLink.url)
      divisionCompetitors = parse_competitors_division(divisionCompetitorsResponse)
      #divisionLink.text[-1] gets the division letter from link text. Used as keys for competitors item
      div = 'div'+divisionLink.text[-1]
      competitors[div] = divisionCompetitors
  regatta['competitors'] = competitors
  print(regatta['competitors'])
  return regatta

def parse_full_scores(response):
  fullScores = dict()
  lastdivision = lastDivision(response)
  currentSchool = None
  for row in response.xpath('//*[contains(@class,"results coordinate")]/tbody/tr'):
    divClass = row.xpath('@class').extract()[0]
    if ('div' in divClass):
      if (divClass == 'divA'):
        schoolScore = dict()
        currentSchool = row.xpath('td[3]/a/text()').extract()[0]
        schoolScore[ divClass ] = parse_division_score(row)## list of A division results
      else:
        schoolScore[ divClass ] = parse_division_score(row)
      if (row.xpath('@class').extract()[0]==lastdivision ):
        fullScores[currentSchool] = schoolScore
  return fullScores

def parse_division_score(row):
  results = []
  columns = row.xpath('td[contains(@class,"right")]')
  for column in columns:
    results.append(column.xpath('text()').extract()[0])
  return results

def lastDivision(response):
  divisionsText = response.xpath('//*[@id="page-info"]/li[5]/span[2]/text()').extract()[0]
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

def parse_competitors_division(response):
  competitors = dict()
  currentSchool = None
  for row in response.xpath('//*[contains(@class,"results coordinate")]/tbody/tr'):
    rowClass = row.xpath('@class').extract()[0]
    if ('topborder' in rowClass): 
      schoolCompetitors = dict({'skippers':dict(),'crews':dict()})
      currentSchool = row.xpath('*[contains(@class,"schoolname")]/a/text()').extract()[0]
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
  lastdivision = lastDivision(response)
  currentSchool = None
  for row in response.xpath('//*[contains(@class,"results coordinate")]/tbody/tr'):
    divClass = row.xpath('@class').extract()[0]
    print divClass
    if (divClass == 'divA'):
      schoolScore = dict()
      currentSailor = row.xpath('td[3]/text()').extract()[0]
      currentSchool = row.xpath('td[3]/a/text()').extract()[0]
      schoolScore['school'] = currentSchool
      schoolScore[ 'scores' ] = parse_division_score(row)## list of A division results
      fullScores[currentSailor] = schoolScore
  return fullScores

def getResponse(url):
  lxmlResponse = lxml.html.parse(url)
  htmlbody = lxml.html.tostring(lxmlResponse)
  response = scrapy.http.HtmlResponse(url = url, body = htmlbody)
  return response