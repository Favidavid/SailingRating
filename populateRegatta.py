from dbinit import School, Sailor, Regatta, Race, RaceResult
import datetime

START_RATING = 1000



def populate_regatta(regatta_dict, session):


  competitor_divisions = regatta_dict['competitor_divisions']
  scores = regatta_dict['full_scores']
  # places = regatta_dict['places']
  number_of_races = scores['number_of_races']
  number_of_teams = len(competitor_divisions['divA'])
  summary = ''
  for text in regatta_dict['summary']:
    add_string = ' '+text
    summary+=add_string

  ##########SESSION CREATED###########

  def races_sailed_parser(races):
    """Return list of integers representing the races sailed by a sailor"""
    if len(races) == 0:
      return list(range(0,int(number_of_races)))
    else:
      races_list = list()
      for ran in races.split(','):
        beginEnd = ran.split('-')
        if len(beginEnd) == 1:
          races_list += [int(beginEnd[0])-1]
        else:
          races_list += range( int(beginEnd[0])-1, int(beginEnd[1]) )
      return races_list

  def get_sailor_or_create(name_and_year,sailor_school):
    """Return sailor object from db. If it does not exist, create one"""
    sailor_objects = session.query(Sailor).filter(Sailor.name_and_year == name_and_year).all()
    if len(sailor_objects) == 0:
      return_sailor = new_sailor(name_and_year, sailor_school)
      session.add(return_sailor)
    else: 
      return_sailor = sailor_objects[0]
    if len(sailor_objects) > 1:
      print "more than one sailor"
    return return_sailor

  def new_sailor(name_and_year, school_object):
    return Sailor(clean_name_and_year(name_and_year), school_object, START_RATING)

  def clean_name_and_year(name_and_year):
    last = name_and_year[-1]
    if last == '*':
      return name_and_year[:-2]
    else:
      return name_and_year


  def get_school_or_create(school_name):
    """Return school object from db. If it does not exist, create one"""
    school_objects = session.query(School).filter(School.name == school_name).all()
    if len(school_objects) == 0:
      school_object = new_school(school_name)
      session.add(school_object)
    else:
      school_object = school_objects[0]
    if len(school_objects) > 1:
      print "more than one school"
    return school_object

  def new_school(school_name):
    return School(school_name)

  def finish_value(finish_string):
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
    month = datetime.datetime.strptime(fields[0],'%B').month
    day = int(fields[1].split('-')[-1][:-1])
    return datetime.date(year ,month, day)

  def create_race_result(skipper,race_number,finish_place,division):
    race_result = RaceResult(skipper,race_number,finish_place,finish_value(finish_place),
      division,race_objects[race_number])
    print finish_place
    print finish_value(finish_place)
    return race_result

  regatta_object = Regatta(regatta_dict['name'],regatta_dict['url'],regatta_dict['host'],parse_date(regatta_dict['date']),regatta_dict['tier'],
    regatta_dict['boat'],regatta_dict['scoring'],regatta_dict['summary'])
  sailor_objects = []
  school_objects = []

  for div_key, div in competitor_divisions.iteritems():
    race_objects = []
    for i in range(int(number_of_races)):
      race_number = i
      new_race = Race(race_number,regatta_object,div_key)
      race_objects.append(new_race)
      session.add(new_race)
    for team_key, team in div.iteritems():
      school_object = get_school_or_create(team['school'])
      if school_object not in school_objects:
        school_objects.append(school_object)
      # team_finish_place = places[team_key] # team['place']
      race_result_objects = {}
      for sailor_key, sailor in team['skipper'].iteritems():
        sailor_object = get_sailor_or_create(sailor_key,school_object)
        if sailor_object not in sailor_objects:
          sailor_objects.append(sailor_object)
        races_sailed = races_sailed_parser(sailor)
        for race_number in races_sailed:
          race_result_object = create_race_result(sailor_object,race_number,scores[team_key][div_key][race_number],div_key)
          race_result_objects[race_number] = race_result_object
          race_objects[race_number].sailors.append(sailor_object)
      for sailor_key, sailor in team['crew'].iteritems():
        sailor_object = get_sailor_or_create(sailor_key,school_object)
        if sailor_object not in sailor_objects:
          sailor_objects.append(sailor_object)
        races_sailed = races_sailed_parser(sailor)
        for race_number in races_sailed:
          race_result_objects[race_number].crewsailors = sailor_object
          race_objects[race_number].sailors.append(sailor_object)
  for sailor_object in sailor_objects:
    regatta_object.sailors.append(sailor_object)
  for school_object in school_objects:
    regatta_object.schools.append(school_object)
  session.add(regatta_object)
  return regatta_object
