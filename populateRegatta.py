import parsers
from parsers import getResponse
from dbinit import *

def test_response():
  return getResponse("http://www.google.com")

def populate_regatta(regatta_url,db_url):
  engine = create_engine(db_url, echo=True)
  Base.metadata.bind = engine
  session_maker = sessionmaker(bind=engine)

  regatta = parsers.parse_regatta(getResponse(regatta_url))
  divisions = regatta['competitors']
  scores = regatta['fullScores']
  places = regatta['places']
  number_of_races = scores['numberOfRaces']
  number_of_schools = len(divisions['divA'])
  summary = ''
  for text in regatta['summary']:
    add_string = ' '+text
    summary+=add_string
  session = session_maker()
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
    return Sailor(name_and_year,school_object,name_and_year[:-4],
      int(name_and_year[-2:])+2000,-999)

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
          return number_of_schools+1
      else:
        return int(finish_string)

  def create_race_result(skipper,race_number,finish_place,division):
    race_result = RaceResult(skipper,race_number,finish_place,finish_value(finish_place),
      division,race_objects[race_number])
    return race_result

  regatta_object = Regatta(regatta['name'],regatta_url,regatta['host'],regatta['tier'],
    regatta['boat'],regatta['scoring'],regatta['summary'])
  sailor_objects = []
  school_objects = []

  for div in divisions:
    race_objects = []
    for i in range(int(number_of_races)):
      num = i
      new_race = Race(num,regatta_object,div)
      race_objects.append(new_race)
      session.add(new_race)
    for school in divisions[div]:
      school_object = get_school_or_create(school)
      if school_object not in school_objects:
        school_objects.append(school_object)
      school_finish_place = places[school]
      race_result_objects = {}
      for sailor in divisions[div][school]['skipper']: 
        sailor_object = get_sailor_or_create(sailor,school_object)
        if sailor_object not in sailor_objects:
          sailor_objects.append(sailor_object)
        races_sailed = races_sailed_parser(divisions[div][school]['skipper'][sailor])
        for race in races_sailed:
          race_result_object = create_race_result(sailor_object,race,scores[school_finish_place][div][race],div)
          race_result_objects[race] = race_result_object
          race_objects[race].sailors.append(sailor_object)
      for sailor in divisions[div][school]['crew']:
        sailor_object = get_sailor_or_create(sailor,school_object)
        if sailor_object not in sailor_objects:
          sailor_objects.append(sailor_object)
        races_sailed = races_sailed_parser(divisions[div][school]['crew'][sailor])
        for race in races_sailed:
          race_result_objects[race].crewsailors = sailor_object
          race_objects[race].sailors.append(sailor_object)
  for sailor_object in sailor_objects:
    regatta_object.sailors.append(sailor_object)
  for school_object in school_objects:
    regatta_object.schools.append(school_object)
  session.add(regatta_object)
  session.commit()
  return regatta

populate_regatta("http://scores.collegesailing.org/f14/atlantic-coast-tournament/",'mysql+pymysql://root:password@localhost/test6')
  
