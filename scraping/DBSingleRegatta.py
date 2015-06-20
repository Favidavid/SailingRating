import parsers
from parsers import getResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def testRegatta():
  return parsers.parse_regatta(getResponse("http://scores.collegesailing.org/f14/navy-fall-women/full-scores/"))

def regatta():
  engine = create_engine('mysql+pymysql://root:password@localhost/test', echo=True)
  Session = sessionmaker(bind=engine)

  regatta = parsers.parse_regatta(getResponse("http://scores.collegesailing.org/f14/navy-fall-women/full-scores/"))
  divisions = regatta['competitors']
  scores = regatta['fullScores']
  places = regatta['places']
  numberOfRaces = scores['numberOfRaces']

  for div in divisions:
    for school in divisions[div]:
      schoolObject = getSchoolOrCreate(school)
      schoolFinishPlace = places[school]
      for sailingPosition in divisions[div][school]:           #each position in this division (skippers or crews)
        for sailor in divisions[div][school][sailingPosition]: #each sailor that sailed in this schools division position (eg A division crews)
          sailorObject = getSailorOrCreate(sailor)
          racesSailed = racesSailedParser(divisions[div][school][position][sailor])
          for race in racesSailed:
            createRaceResult(sailorObject,race+1,scores[schoolFinishPlace][div][race],div,sailingPosition)

  def racesSailedParser(races):
    """Return list of integers representing the races sailed by a sailor"""
    if (len(races) == 0):
      return list(range(0,numberOfRaces))
    else:
      racesList = list()
      for ran in races.split(','):
        beginEnd = ran.split('-')
        racesList += range( int(beginEnd[0])-1, int(beginEnd[1]) )
      return racesList

  def getSailorOrCreate(nameAndYear,school):
    """Return sailor object from db. If it does not exist, create one"""
    try:
      sailor = session.query(Sailor).filter(Sailor.school.name == school).filter(Sailor.nameandyear == nameAndYear).one()
      return sailor
    except NoResultFound, e:
      sailor = newSailor(nameAndYear, school)
      return sailor

  def newSailor(nameAndYear, school):
    return Sailor(nameandyear=nameAndYear,name=nameAndYear[:-4],year=int(nameAndYear[-2:])+2000)

  def getSchoolOrCreate(schoolName):
    """Return school object from db. If it does not exist, create one"""
    try:
      schoolObject = session.query(School).filter(School.name == schoolName).filter(Sailor.nameandyear == nameAndYear).one()
      return schoolObject
    except NoResultFound, e:
      schoolObject = newSchool(schoolName)

  def createRaceResult(sailor,raceNumber,finishPlace,division,position):
    """Create RaceResult for sailor and regatta.

    Keyword arguments:
    sailor -- sailor object
    raceNumber
    finishPlace --
    position -- skipper or crew etc.
    """