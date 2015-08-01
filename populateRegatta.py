import parsers
from parsers import getResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from dbinit import School, Sailor, RatingStamp, Season, Regatta, RaceResult, Base, Race

def testresponse():
  return getResponse("http://www.google.com")

def populateRegatta(regattaUrl,dbUrl):
  engine = create_engine(dbUrl, echo=True)
  Base.metadata.bind = engine
  Session = sessionmaker(bind=engine)

  regatta = parsers.parse_regatta(getResponse(regattaUrl))
  divisions = regatta['competitors']
  scores = regatta['fullScores']
  places = regatta['places']
  numberOfRaces = scores['numberOfRaces']
  numberOfSchools = len(divisions['divA'])
  summary = ''
  for text in regatta['summary']:
    addstring = ' '+text
    summary+=addstring
  session = Session()
  def racesSailedParser(races):
    """Return list of integers representing the races sailed by a sailor"""
    if (len(races) == 0):
      return list(range(0,int(numberOfRaces)))
    else:
      racesList = list()
      for ran in races.split(','):
        beginEnd = ran.split('-')
        if len(beginEnd) == 1:
          racesList += [int(beginEnd[0])-1]
        else:
          racesList += range( int(beginEnd[0])-1, int(beginEnd[1]) )
      return racesList

  def getSailorOrCreate(nameAndYear,school):
    """Return sailor object from db. If it does not exist, create one"""
    sailorObjects = session.query(Sailor).filter(Sailor.nameandyear == nameAndYear).all()
    if (len(sailorObjects) == 0):
      sailor = newSailor(nameAndYear, school)
      session.add(sailor)
    else: 
      sailor = sailorObjects[0]
    if (len(sailorObjects) > 1):
      print "more than one sailor"
    return sailor

  def newSailor(nameAndYear, schoolObject):
    return Sailor(nameandyear=nameAndYear,school=schoolObject,name=nameAndYear[:-4],
      year=int(nameAndYear[-2:])+2000,currentrating=-999)

  def getSchoolOrCreate(schoolName):
    """Return school object from db. If it does not exist, create one"""
    schoolObjects = session.query(School).filter(School.name == schoolName).all()
    if (len(schoolObjects) == 0):
      schoolObject = newSchool(schoolName)
      session.add(schoolObject)
    else:
      schoolObject = schoolObjects[0]
    if (len(schoolObjects) > 1):
      print "more than one school"
    return schoolObject

  def newSchool(schoolName):
    return School(name=schoolName)

  def finishValue(finishString):
      if ':letters:' in finishString:
        if ('BKD' in finishString) or ('RDG' in finishString):
          return int(finishString.split(':letters:')[1].split(':')[0][1:])
        else:
          return numberOfSchools+1
      else:
        return int(finishString)

  def createRaceResult(skipper,raceNumber,finishPlace,division):
    raceResult = RaceResult(skippersailor=skipper,racenumber=raceNumber,finish=finishPlace,finishvalue=finishValue(finishPlace)
      division=division,race=raceObjects[raceNumber])
    return raceResult

  regattaObject = Regatta(name=regatta['name'],url=regattaUrl,host=regatta['host'],tier=regatta['tier'],
    boat=regatta['boat'],scoring=regatta['scoring'],summary=regatta['summary'])
  sailorObjects = []
  schoolObjects = []

  for div in divisions:
    raceObjects = []
    for i in range(int(numberOfRaces)):
      num = i
      newRace = Race(racenumber=num,regatta=regattaObject,division=div)
      raceObjects.append(newRace)
      session.add(newRace)
    for school in divisions[div]:
      schoolObject = getSchoolOrCreate(school)
      if schoolObject not in schoolObjects:
        schoolObjects.append(schoolObject)
      schoolFinishPlace = places[school]
      raceResultObjects = {}
      for sailor in divisions[div][school]['skipper']: 
        sailorObject = getSailorOrCreate(sailor,schoolObject)
        if sailorObject not in sailorObjects:
          sailorObjects.append(sailorObject)
        racesSailed = racesSailedParser(divisions[div][school]['skipper'][sailor])
        for race in racesSailed:
          raceResultObject = createRaceResult(sailorObject,race,scores[schoolFinishPlace][div][race],div)
          raceResultObjects[race] = raceResultObject
          raceObjects[race].sailors.append(sailorObject)
      for sailor in divisions[div][school]['crew']:
        sailorObject = getSailorOrCreate(sailor,schoolObject)
        if sailorObject not in sailorObjects:
          sailorObjects.append(sailorObject)
        racesSailed = racesSailedParser(divisions[div][school]['crew'][sailor])
        for race in racesSailed:
          raceResultObjects[race].crewsailors = sailorObject
          raceObjects[race].sailors.append(sailorObject)
  for sailorObject in sailorObjects:
    regattaObject.sailors.append(sailorObject)
  for schoolObject in schoolObjects:
    regattaObject.schools.append(schoolObject)
  session.add(regattaObject)
  session.commit()
  return regatta

populateRegatta("http://scores.collegesailing.org/f14/atlantic-coast-tournament/",'mysql+pymysql://root:password@localhost/test6')
  
