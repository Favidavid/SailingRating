import parsers
from parsers import getResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from dbinit import School, Sailor, RatingStamp, Season, Regatta, RaceResult, Base

def testRegatta():
  return parsers.parse_regatta(getResponse("http://scores.collegesailing.org/f14/navy-fall-women/full-scores/"))

def populateRegatta(regattaUrl,dbUrl):
  engine = create_engine(dbUrl, echo=True)
  Base.metadata.bind = engine
  Session = sessionmaker(bind=engine)

  regatta = parsers.parse_regatta(getResponse(regattaUrl))
  divisions = regatta['competitors']
  scores = regatta['fullScores']
  places = regatta['places']
  numberOfRaces = scores['numberOfRaces']

  session = Session()
  def racesSailedParser(races):
    """Return list of integers representing the races sailed by a sailor"""
    if (len(races) == 0):
      return list(range(0,int(numberOfRaces)))
    else:
      racesList = list()
      for ran in races.split(','):
        beginEnd = ran.split('-')
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

  def createRaceResult(sailor,raceNumber,finishPlace,division,sailingPosition):
    raceResult = RaceResult(sailor=sailor,racenumber=raceNumber,finishplace=finishPlace,
      division=division,sailingposition=sailingPosition,race=raceObjects[raceNumber])

  regattaObject = Regatta(name=regatta['name'],url=regattaUrl,host=regatta['host'],tier=regatta['tier'],
    boat=regatta['boat'],scoring=regatta['scoring'],summary=regatta['summary'])
  racesObjects = []
  sailorObjects = []
  schoolObjects = []
  for i in range(numberOfRaces):
    newRace = Race(racenumber=i,regatta=regattaObject)
    raceObjects.append(newRace)
    session.add(newRace)

  for div in divisions:
    for school in divisions[div]:
      schoolObject = getSchoolOrCreate(school)
      if schoolObject not in schoolObjects:
        schoolObjects.append(schoolObject)
      schoolFinishPlace = places[school]
      for sailingPosition in divisions[div][school]:           #each position in this division (skippers or crews)
        for sailor in divisions[div][school][sailingPosition]: #each sailor that sailed in this schools division position (eg A division crews)
          sailorObject = getSailorOrCreate(sailor,schoolObject,regattaObject)
          if sailorObject not in sailorObjects:
            sailorObjects.append(sailorObject)
          racesSailed = racesSailedParser(divisions[div][school][sailingPosition][sailor])
          for race in racesSailed:
            createRaceResult(sailorObject,race,scores[schoolFinishPlace][div][race],div,sailingPosition)
            raceObjects[race].sailors.append(sailorObject)
  regattaObject.sailors.append(sailorObjects)
  regattaObject.schools.append(schoolObjects)
  session.add(regattaObject)
  session.commit()
  return regatta

populateRegatta('http://scores.collegesailing.org/f14/icsa-singlehanded-champs-full/','mysql+pymysql://root:password@localhost/test4')
  
