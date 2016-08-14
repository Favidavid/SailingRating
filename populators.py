from dbinit import School, Sailor, Regatta, Race, RaceResult, Week, Season
import datetime

START_RATING = 1000


def populate_season(season, week_objects, session):
    season = Season(season['name'], week_objects, season['url'])
    session.add(season)
    return season


def populate_week(season_id, week_num, regattas_dicts, session):
    regatta_objects = []
    for regatta_dict in regattas_dicts:
        try:
            regatta_object = populate_regatta(regatta_dict, session)
            session.commit()
            regatta_objects.append(regatta_object)
        except:
            print(print('regatta with url: ' + regatta_dict['url'] + ', was not persisted'))
    week_object = Week(regattas=regatta_objects, number=week_num, season_id=season_id)
    session.add(week_object)
    session.commit()
    return week_object


def populate_regatta(regatta_dict, session):
    competitor_divisions = regatta_dict['competitor_divisions']
    scores = regatta_dict['full_scores']
    # places = regatta_dict['places']
    number_of_races = scores['number_of_races']
    number_of_teams = len(competitor_divisions['divA'])
    summary = ''
    if 'summary' in regatta_dict:
        for text in regatta_dict['summary']:
            add_string = ' '+text
            summary += add_string

    regatta_object = Regatta(
        name=regatta_dict['name'], url=regatta_dict['url'], host=regatta_dict['host'],
        date=parse_date(regatta_dict['date']), tier=regatta_dict['tier'], boat=regatta_dict['boat'],
        scoring=regatta_dict['scoring'], summary=regatta_dict['summary'])
    sailor_objects = []
    school_objects = []

    for div_key, div in competitor_divisions.iteritems():
        race_objects = []
        for i in range(number_of_races):
            race_number = i
            new_race = Race(race_number=race_number, regatta=regatta_object, division=div_key)
            race_objects.append(new_race)
            session.add(new_race)
        for team_key, team in div.iteritems():
            school_object = get_school_or_create(team['school'], session)
            if school_object not in school_objects:
                school_objects.append(school_object)
            # team_finish_place = places[team_key] # team['place']
            race_result_objects = {}
            for sailor_key, sailor in team['skipper'].iteritems():
                sailor_object = get_sailor_or_create(sailor_key, school_object, session)
                if sailor_object not in sailor_objects:
                    sailor_objects.append(sailor_object)
                races_sailed = races_sailed_parser(sailor, number_of_races)
                for race_number in races_sailed:
                    if race_number < number_of_races:
                        race_result_object = create_race_result(
                            skipper=sailor_object, race_number=race_number,
                            finish_place=scores[team_key][div_key][race_number],
                            division=div_key, number_of_teams=number_of_teams,
                            race_objects=race_objects)
                        race_result_objects[race_number] = race_result_object
                        race_objects[race_number].sailors.append(sailor_object)
            for sailor_key, sailor in team['crew'].iteritems():
                sailor_object = get_sailor_or_create(sailor_key, school_object, session)
                if sailor_object not in sailor_objects:
                    sailor_objects.append(sailor_object)
                races_sailed = races_sailed_parser(sailor, number_of_races)
                for race_number in races_sailed:
                    if race_number < number_of_races:
                        race_result_objects[race_number].crewsailors = sailor_object
                        race_objects[race_number].sailors.append(sailor_object)
    for sailor_object in sailor_objects:
        regatta_object.sailors.append(sailor_object)
    for school_object in school_objects:
        regatta_object.schools.append(school_object)
    session.add(regatta_object)
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
    sailor_objects = session.query(Sailor).filter(Sailor.name_and_year == name_and_year).all()
    if len(sailor_objects) == 0:
        return_sailor = new_sailor(name_and_year, sailor_school)
        session.add(return_sailor)
    else:
        return_sailor = sailor_objects[0]
    if len(sailor_objects) > 1:
        print("more than one sailor")
    return return_sailor


def new_sailor(name_and_year, school_object):
    return Sailor(clean_name_and_year(name_and_year), school_object, START_RATING)


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
        school_object = new_school(school_name)
        session.add(school_object)
    else:
        school_object = school_objects[0]
    if len(school_objects) > 1:
        print("more than one school")
    return school_object


def new_school(school_name):
    return School(school_name)


def finish_value(finish_string, number_of_teams):
    if ':letters:' in finish_string:
        if ('BKD' in finish_string) or ('RDG' in finish_string):
            return int(finish_string.split(':letters:')[1].split(':')[0][1:])
        else:
            return number_of_teams+1
    else:
        return int(finish_string)


def parse_date(date_string):
    # 'November 21-22, 2015'
    # datetime.date(2015,11,22)
    fields = date_string.split(' ')
    year = int(fields[2])
    month = datetime.datetime.strptime(fields[0], '%B').month
    day = int(fields[1].split('-')[-1][:-1])
    return datetime.date(year, month, day)


def create_race_result(skipper, race_number, finish_place, division, number_of_teams, race_objects):
    race_result = RaceResult(
        skipper=skipper, race_number=race_number, finish_place=finish_place,
        finish_value=finish_value(finish_place, number_of_teams=number_of_teams),
        division=division, race_object=race_objects[race_number])
    return race_result
