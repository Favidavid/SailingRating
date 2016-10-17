import datetime
import logging
import re
import daterangeparser
import config

from objects import School, Sailor, Regatta, Race, RaceResult, Week

START_RATING = 1000


def populate_week(season_id, week_num, regattas_dicts, session):
    weeks = session.query(Week).filter(Week.season_id == season_id).filter(Week.week_number == week_num).all()
    if len(weeks) > 0:
        week_object = weeks[0]
        already_persisted_regatta_urls = [regatta.url for regatta in week_object.regattas]
    else:
        week_object = Week(week_number=week_num, season_id=season_id,
                           date=get_week_date(week_num, season_id))
        session.add(week_object)
        session.commit()
        already_persisted_regatta_urls = []

    for regatta_dict in regattas_dicts:
        print('    -' + regatta_dict['name'] + ' ' + regatta_dict['url'])
        if regatta_dict['url'] in already_persisted_regatta_urls:
            print('     already persisted')
            continue
        regatta_object = populate_regatta(regatta_dict, session)
        session.commit()
        print('     persisted')
        week_object.regattas.append(regatta_object)
        session.commit()
    return week_object


def populate_regatta(regatta_dict, session):
    competitor_divisions = regatta_dict['competitor_divisions']
    scores = regatta_dict['full_scores']
    # places = regatta_dict['places']
    real_number_of_races = scores['number_of_races']
    number_of_teams = len(competitor_divisions['divA'])
    summary = ''
    if 'summary' in regatta_dict:
        for text in regatta_dict['summary']:
            add_string = ' '+text
            summary += add_string

    regatta_object = Regatta(
        name=regatta_dict['name'], url=regatta_dict['url'], host=regatta_dict['host'],
        date=daterangeparser.parse(regatta_dict['date'])[0], tier=regatta_dict['tier'], boat=regatta_dict['boat'],
        scoring=regatta_dict['scoring'], summary=regatta_dict['summary'])
    session.add(regatta_object)
    sailor_objects = []
    school_objects = []

    for div_key, div in competitor_divisions.items():
        number_of_races = min(get_div_number_of_races(div_key, regatta_dict), real_number_of_races)
        race_objects = []
        for i in range(number_of_races):
            race_number = i
            new_race = Race(race_number=race_number, regatta=regatta_object, division=div_key)
            session.add(new_race)
            race_objects.append(new_race)
        for team_key, team in div.items():
            school_object = get_school_or_create(team['school'], session)
            if school_object not in school_objects:
                school_objects.append(school_object)
            # team_finish_place = places[team_key] # team['place']
            race_result_objects = {}
            for sailor_key, races_sailed_string in team['skipper'].items():
                if sailor_key == 'no one': continue
                sailor_object = get_sailor_or_create(sailor_key, school_object, session)
                if sailor_object not in sailor_objects:
                    sailor_objects.append(sailor_object)
                races_sailed = races_sailed_parser(races_sailed_string, number_of_races)
                for race_number in races_sailed:
                    if race_number < number_of_races:
                        race_result_object = RaceResult(
                            skipper=sailor_object, race_number=race_number,
                            finish_place=scores[team_key][div_key][race_number],
                            finish_value=finish_value(scores[team_key][div_key][race_number], number_of_teams=number_of_teams),
                            division=div_key, race_object=race_objects[race_number])
                        session.add(race_result_object)
                        race_result_objects[race_number] = race_result_object
                        race_objects[race_number].sailors.append(sailor_object)
            for sailor_key, races_sailed_string in team['crew'].items():
                if sailor_key == 'no one': continue
                sailor_object = get_sailor_or_create(sailor_key, school_object, session)
                if sailor_object not in sailor_objects:
                    sailor_objects.append(sailor_object)
                races_sailed = races_sailed_parser(races_sailed_string, number_of_races)
                for race_number in races_sailed:
                    if race_number < number_of_races:
                        if race_number not in race_result_objects:
                            # if a skipper wasn't recorded for this race result
                            race_result_object = RaceResult(
                                crew=sailor_object, race_number=race_number,
                                finish_place=scores[team_key][div_key][race_number],
                                finish_value=finish_value(scores[team_key][div_key][race_number], number_of_teams=number_of_teams),
                                division=div_key, race_object=race_objects[race_number])
                            race_result_objects[race_number] = race_result_object
                            session.add(race_result_object)
                        race_result_objects[race_number].crew_sailor = sailor_object
                        race_objects[race_number].sailors.append(sailor_object)
    regatta_object.sailors.extend(sailor_objects)
    regatta_object.schools.extend(school_objects)
    return regatta_object


def races_sailed_parser(races, number_of_races):
    """Return list of integers representing the races sailed by a sailor"""
    if len(races) == 0:
        return list(range(0, number_of_races))
    else:
        races_list = list()
        for ran in races.split(','):
            begin_end = ran.split('-')
            if len(begin_end) == 1:
                races_list += [int(begin_end[0])-1]
            else:
                races_list += range(int(begin_end[0])-1, int(begin_end[1]))
        return races_list


def get_sailor_or_create(name_and_year, sailor_school, session):
    """Return sailor object from db. If it does not exist, create one"""
    cleaned_name_and_year = clean_name_and_year(name_and_year)
    sailor_objects = session.query(Sailor).filter(
        Sailor.name_and_year == cleaned_name_and_year).filter(Sailor.school == sailor_school).all()
    if len(sailor_objects) == 0:
        return_sailor = Sailor(name_and_year=cleaned_name_and_year, school=sailor_school,
                               start_rating=START_RATING, href=get_sailor_href(cleaned_name_and_year))
        session.add(return_sailor)
        session.commit()
    else:
        return_sailor = sailor_objects[0]
    if len(sailor_objects) > 1:
        print("more than one sailor: ")
        for s_o in sailor_objects:
            print(s_o.name_and_year + ', ' + s_o.school.name)
    return return_sailor


def get_sailor_href(name_and_year):
    href = name_and_year.replace(' ', '-').replace("'", '')
    return href


def clean_name_and_year(name_and_year):
    last = name_and_year[-1]
    if last == '*':
        return name_and_year[:-2]
    else:
        return name_and_year


def get_school_or_create(school_name, session):
    """Return school object from db. If it does not exist, create one"""
    school_objects = session.query(School).filter(School.name == school_name).all()
    if len(school_objects) == 0:
        school_object = School(school_name)
        session.add(school_object)
        session.commit()
    else:
        school_object = school_objects[0]
    if len(school_objects) > 1:
        print("more than one school")
    return school_object


def finish_value(finish_string, number_of_teams):
    if ':letters:' in finish_string:
        letters_string = finish_string.split(':letters:')[1]
        if ('BKD' in finish_string) or ('RDG' in finish_string):
            return int(re.split('[,:]', letters_string)[0][1:])
        else:
            return number_of_teams + 1
    else:
        return int(finish_string)


def parse_date(date_string):
    start, end = daterangeparser.parse(date_string)
    return start


def get_div_number_of_races(div_key, regatta_dict):
    scores = regatta_dict['full_scores']
    for key, value in scores.items():
        if isinstance(value, dict) and div_key in value:
            return len(value[div_key])


def get_week_date(week_num, season_id):
    return config.season[season_id] + datetime.timedelta(weeks=week_num-1)


def create_race_result(skipper, race_number, finish_place, division, number_of_teams, race_objects):
    race_result = RaceResult(
        skipper=skipper, race_number=race_number, finish_place=finish_place,
        finish_value=finish_value(finish_place, number_of_teams=number_of_teams),
        division=division, race_object=race_objects[race_number])
    return race_result
