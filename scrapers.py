from scrapy.http import HtmlResponse
from scrapy.linkextractors import LinkExtractor
import lxml.html
from collections import OrderedDict
import config
import sys

base_url = 'http://scores.collegesailing.org'
xpath_regatta_name = '//*[@id="content-header"]/h1/span[2]/text()'
xpath_regatta_host = '//*[@id="page-info"]/li[1]/span[2]/span/text()'
xpath_regatta_date = '//*[@id="page-info"]/li[2]/span[2]/time/text()'
xpath_regatta_tier = '//*[@id="page-info"]/li[3]/span[2]/span/text()'
xpath_regatta_boat = '//*[@id="page-info"]/li[4]/span[2]/text()'
xpath_regatta_scoring = '//*[@id="page-info"]/li[5]/span[2]/text()'
xpath_regatta_summary = '//*[@id="summary"]/descendant::*/text()'
xpath_full_scores_url = '//*[@id="menu"]'
xpath_report_school_row = '//*[@id="page-content"]/div[3]/table[1]/tbody/tr'
xpath_report_school_team_name = 'td[@class="teamname"]/text()'
xpath_report_single_sailor_name = 'td[@class="teamname"]/span/a/text()'
xpath_report_school_finish_place = 'td[2]/text()'


def scrape_week(season_id, week_num):
    """
    Returns a list containing dictionaries of all the regattas corresponding to a week and season
    :param season_id: season id as it would appear on the url, example: f12 or s14
    :param week_num:
    :return week_regattas: list of regatta dictionaries
    """
    week_regattas = []
    for regatta_url in scrape_week_regatta_urls(season_id, week_num):
        try:
            regatta = scrape_regatta(regatta_url)
        except:
            print('regatta with url: ' + regatta_url + ', was not scraped correctly')
            print(sys.exc_info()[0])
            continue
        if regatta['scoring'] != 'Combined':
            week_regattas.append(regatta)
    return week_regattas


def scrape_week_regatta_urls(season_id, week_num):
    response = get_response(config.regatta_domain + season_id)
    week_response = response.xpath('//*[text()="Week '+str(week_num)+'"]/parent::tr')
    week_regatta_urls = []
    for row in week_response.xpath('following-sibling::tr'):
        row_class = row.xpath('@class').extract()
        if len(row_class) == 0:
            break
        else:
            regatta_url = response.url + '/' + row.xpath('td[1]/a/@href').extract()[0]
            if regatta_url not in config.regatta_url_blacklist:
                week_regatta_urls.append(regatta_url)
    return week_regatta_urls


def scrape_seasons_ordered_recent_first():
    response = get_response(config.regatta_domain + 'seasons')
    seasons_response = response.xpath('//*[@id="page-info"]/li')
    seasons = []
    for season in seasons_response:
        # season_dict = dict()
        season_url = base_url + season.xpath('span[2]/a/@href').extract()[0]
        season_id = season_url[-4:-1]
        # season_name = season.xpath('span[1]/text()').extract()[0]
        # season_dict['name'] = season_name
        # season_dict['url'] = season_url
        # season_dict['id'] = season_id
        seasons.append(season_id) # = season_dict
    return seasons


def scrape_weeks_ordered_recent_first(season_id):
    response = get_response(config.regatta_domain + season_id)
    weeks = []
    for week_text in response.xpath('//*[@id="page-content"]/div[2]/table/tbody/tr/*[contains(text(),"Week ")]/text()').extract():
        week_number = int(week_text[5:])
        weeks.append(week_number)
    # uncomment if youw ant to include preweeks
    # for week_text in response.xpath('//*[contains(text(),"Preweek ")]/text()').extract():
    #     week_number = -int(week_text[-1:]) + 1
    #     weeks.append(week_number)
    return weeks


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
    regatta['name'] = response.xpath(xpath_regatta_name).extract()[0]
    regatta['date'] = response.xpath(xpath_regatta_date).extract()[0]
    regatta['scoring'] = response.xpath(xpath_regatta_scoring).extract()[0]
    if response.xpath(xpath_regatta_host).extract():
        regatta['host'] = response.xpath(xpath_regatta_host).extract()[0]
    else:
        regatta['host'] = ''
    if response.xpath(xpath_regatta_tier).extract():
        regatta['tier'] = response.xpath(xpath_regatta_tier).extract()[0]
    else:
        regatta['tier'] = ''
    if response.xpath(xpath_regatta_boat).extract():
        regatta['boat'] = response.xpath(xpath_regatta_boat).extract()[0]
    else:
        regatta['boat'] = ''
    if response.xpath(xpath_regatta_summary).extract():
        regatta['summary'] = response.xpath(xpath_regatta_summary).extract()[0]
    else:
        regatta['summary'] = ''


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
                    if len(current_school_team_array) == 0:
                        current_school_team_array = row.xpath('td[3]/text()').extract()
                elif scoring == '1 Division':
                    current_school_team_array = row.xpath('td[3]/text()').extract()
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
                column_text += ':letters:'+title_actual_score[0][:150]
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
            if len(sailor_name_array) == 0:
                sailor_name_array = ['no one']
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
    for row in response.xpath('//*[contains(@class,"results coordinate")]/tbody/tr'):
        sailor_name_array = row.xpath('*[contains(@class,"teamname")]/span/a/text()').extract()
        if len(sailor_name_array) == 0:  # not a link because sailor has not registered
            sailor_name_array = row.xpath('*[contains(@class,"teamname")]/span/text()').extract()
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
