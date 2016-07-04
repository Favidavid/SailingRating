from scrapy.http import HtmlResponse
from scrapy.linkextractors import LinkExtractor
import lxml.html

base_url = 'http://scores.collegesailing.org'
xpathRegattaName = '//*[@id="content-header"]/h1/span[2]/text()'
xpathRegattaHost = '//*[@id="page-info"]/li[1]/span[2]/span/text()'
xpathRegattaDate = '//*[@id="page-info"]/li[2]/span[2]/time/text()'
xpathRegattaTier = '//*[@id="page-info"]/li[3]/span[2]/span/text()'
xpathRegattaBoat = '//*[@id="page-info"]/li[4]/span[2]/text()'
xpathRegattaScoring = '//*[@id="page-info"]/li[5]/span[2]/text()'
xpathRegattaSummary = '//*[@id="summary"]/descendant::*/text()'
xpath_full_scores_url = '//*[@id="menu"]'
xpath_report_school_row = '//*[@id="page-content"]/div[3]/table[1]/tbody/tr'
xpath_report_school_team_name = 'td[@class="teamname"]/text()'
xpath_report_single_sailor_name = 'td[@class="teamname"]/span/a/text()'
xpathReportSchoolFinishPlace = 'td[2]/text()'


def scrape_seasons_ordered():
    response = get_response('http://scores.collegesailing.org/seasons')
    seasons_response = response.xpath('//*[@id="page-info"]/li')
    seasons = []
    for season in seasons_response:
        season_dict = dict()
        season_url = base_url + season.xpath('span[2]/a/@href').extract()[0]
        season_name = season.xpath('span[1]/text()').extract()[0]
        season_dict['name'] = season_name
        season_dict['url'] = season_url
        seasons.append(season_dict)
    seasons.reverse()
    return seasons


def scrape_weeks_ordered(season_url):
    response = get_response(season_url)
    weeks = []
    for week in response.xpath('//*[contains(text(),"Week ")]/text()').extract():
        week_number = int(week[5:])
        week_dict = scrape_week(season_url, week_number)
        weeks.append(week_dict)
    weeks.reverse()
    return weeks


def scrape_week(season_url, week_num):
    week = dict()
    response = get_response(season_url)
    regatta_urls = dict()
    week_response = response.xpath('//*[text()="Week '+str(week_num)+'"]/parent::tr')
    week['number'] = week_num
    for row in week_response.xpath('following-sibling::tr'):
        row_class = row.xpath('@class').extract()
        if len(row_class) == 0:
            break
        else:
            regatta_url = response.url + row.xpath('td[1]/a/@href').extract()[0]
            regatta_name = row.xpath('td[1]/a/text()').extract()[0]
            regatta_status = row.xpath('td[6]/strong/text()').extract()[0]
            regatta_scoring = row.xpath('td[4]/text()').extract()[0]
            regatta_urls[regatta_name] = {'url': regatta_url, 'status': regatta_status, 'scoring': regatta_scoring}
    week['regatta_urls'] = regatta_urls
    return week


def scrape_regatta(regatta_url):
    response = get_response(regatta_url)
    regatta = dict()

    set_regatta_data(regatta, regatta_url, response)

    # populate fullScores (works for singlehanded as well)
    regatta['full_scores'] = scrape_full_scores(response, regatta['scoring'])

    # populate competitors
    regatta['competitor_divisions'] = scrape_competitors(response, regatta['scoring'])

    return regatta


def set_regatta_data(regatta, regatta_url, response):
    regatta['url'] = regatta_url
    regatta['name'] = response.xpath(xpathRegattaName).extract()[0]
    regatta['date'] = response.xpath(xpathRegattaDate).extract()[0]
    regatta['scoring'] = response.xpath(xpathRegattaScoring).extract()[0]
    try:
        regatta['host'] = response.xpath(xpathRegattaHost).extract()[0]
        regatta['tier'] = response.xpath(xpathRegattaTier).extract()[0]
        regatta['boat'] = response.xpath(xpathRegattaBoat).extract()[0]
        regatta['summary'] = response.xpath(xpathRegattaSummary).extract()[0]
    except:
        pass


def scrape_full_scores(response, scoring):
    full_scores_link = LinkExtractor(restrict_xpaths=(xpath_full_scores_url),
                                     allow=('.*/full-scores/')).extract_links(response)[0]
    full_scores_response = get_response(full_scores_link.url)
    full_scores = dict()
    last_div = last_division(full_scores_response)
    # current_place = '1'k
    number_of_races = full_scores_response.xpath(
        '//*[contains(@class,"results coordinate")]/thead/tr/th[last()-2]/text()').extract()[0]
    full_scores['number_of_races'] = int(number_of_races)
    for row in full_scores_response.xpath('//*[contains(@class,"results coordinate")]/tbody/tr'):
        div_class = row.xpath('@class').extract()[0]
        if 'div' in div_class:
            if div_class == 'divA':
                school_score = dict()
                current_school = row.xpath('td[3]/a/text()').extract()[0]
                if scoring == 'Singlehanded':
                    current_school_team_array = row.xpath('td[3]/span/a/text()').extract()
                    if len(current_school_team_array) == 0:
                        current_school_team_array = row.xpath('td[3]/span/text()').extract()
                elif scoring == '1 Division':
                    current_school_team_array = row.xpath('td[3]/text()').extract()
                    current_school_team_array[0] = current_school_team_array[0]
                else:
                    current_school_team_array = row.xpath('following-sibling::tr[1]/td[3]/text()').extract()
                current_school_team = current_school_team_array[0]
                current_place = row.xpath('td[2]/text()').extract()[0]
                school_score['school'] = current_school
                school_score['place'] = current_place
                school_score['school_team'] = current_school_team
                school_score[div_class] = scrape_division_score(row)  # list of A division results
            else:
                school_score[div_class] = scrape_division_score(row)
            if row.xpath('@class').extract()[0] == last_div:
                full_scores[current_school_team] = school_score
    return full_scores


def scrape_division_score(row):
    results = []
    columns = row.xpath('td[contains(@class,"right")]')
    for column in columns:
        title_actual_score = column.xpath('@title').extract()
        if title_actual_score:
            column_text = column.xpath('text()').extract()[0]
            if title_actual_score[0]:
                column_text += ':letters:'+title_actual_score[0]
            results.append(column_text)
    return results


def scrape_competitors(response, scoring):
    if scoring == 'Singlehanded':
        return scrape_singlehanded_competitors(response)
    else:
        return scrape_normal_competitors(response)


def scrape_normal_competitors(response):
    competitors_links = LinkExtractor(restrict_xpaths=('//*[@id="menu"]'), allow=('.*/[A-E]/')).extract_links(response)
    # division regattas, could be single division
    competitors = dict()
    for divisionLink in competitors_links:
        division_competitors_response = get_response(divisionLink.url)
        division_competitors = scrape_normal_competitors_division(division_competitors_response)
        # divisionLink.text[-1] gets the division letter from link text. Used as keys for competitors item
        div = 'div' + divisionLink.text[-1]
        competitors[div] = division_competitors
    return competitors


def scrape_normal_competitors_division(response):
    competitors_division = dict()
    current_school = None
    for row in response.xpath('//*[contains(@class,"results coordinate")]/tbody/tr'):
        row_class = row.xpath('@class').extract()[0]
        if 'topborder' in row_class:
            school_competitors = {'skipper': dict(), 'crew': dict()}
            current_school_team = row.xpath('following-sibling::tr/td[contains(@class,"teamname")]/text()').extract()[0]
            current_school = row.xpath('*[contains(@class,"schoolname")]/a/text()').extract()[0]
        position_xpath_class = row.xpath("*[contains(@class,'sailor-name')]/@class").extract()
        if len(position_xpath_class) > 0:
            position = position_xpath_class[0][12:]
            races_sailed = row.xpath('*[contains(@class,"races")]/text()').extract()
            sailor_name_array = row.xpath('*[contains(@class,"sailor-name")]/a/text()').extract()
            if len(sailor_name_array) == 0:  # not a link because sailor has not registered
                sailor_name_array = row.xpath('*[contains(@class,"sailor-name")]/text()').extract()
            sailor_name = sailor_name_array[0]
            if len(races_sailed) == 0:
                school_competitors[position][sailor_name] = u''
            else:
                school_competitors[position][sailor_name] = races_sailed[0]
        # if last row of competitors (no following siblings) or next row is new school
        if len(row.xpath('following-sibling::tr[1]').extract()) == 0:
            competitors_division[current_school_team] = school_competitors
            competitors_division[current_school_team]['school'] = current_school
        elif 'topborder' in row.xpath('following-sibling::tr[1]/@class').extract()[0]:
            competitors_division[current_school_team] = school_competitors
            competitors_division[current_school_team]['school'] = current_school
    return competitors_division


def scrape_singlehanded_competitors(response):
    competitors = dict()
    competitors_division = dict()
    for row in response.xpath('//*[contains(@class,"results coordinate")]/tbody/tr[contains(@class,"divA")]'):
        sailor_name_array = row.xpath('*[contains(@class,"teamname")]/span/a/text()').extract()
        if len(sailor_name_array) == 0:  # not a link because sailor has not registered
            sailor_name_array = row.xpath('*[contains(@class,"teamname")]/text()').extract()
        sailor_name = sailor_name_array[0]
        current_school = row.xpath('*[contains(@class,"schoolname")]/a/span/text()').extract()[0]
        competitors_division[sailor_name] = {'skipper': dict(), 'crew': dict()}
        competitors_division[sailor_name]['skipper'][sailor_name] = u''
        competitors_division[sailor_name]['school'] = current_school
    competitors['divA'] = competitors_division
    return competitors


def last_division(response):
    divisions_text = response.xpath('//*[@id="page-info"]/li[5]/span[2]/text()').extract()[0]
    if divisions_text == '2 Divisions':
        return 'divB'
    elif divisions_text == '3 Divisions':
        return 'divC'
    elif divisions_text == 'Singlehanded' or divisions_text == '1 Division':
        return 'divA'
    elif divisions_text == '4 Divisions':
        return 'divD'
    else:
        return 'divB'


def get_response(url):
    lxml_response = lxml.html.parse(url)
    html_body = lxml.html.tostring(lxml_response)
    response = HtmlResponse(url=url, body=html_body)
    return response
