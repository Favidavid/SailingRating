import requests
import parsers
import dbtest
from parsers import getResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def regatta():
  engine = create_engine('mysql+pymysql://root:password@localhost/test', echo=True)
  Session = sessionmaker(bind=engine)

  regatta = parsers.parse_regatta(getResponse("http://scores.collegesailing.org/f14/navy-fall-women/full-scores/"))
  divisions = regatta['competitors']
  scores = regatta['fullScores']

  for div in divisions:
    for school in divisions[div]:
      schoolObject = getSchoolOrCreate(school)
      shortSchoolName = schoolObject.shortname
      for position in divisions[div][school]:
        for sailor in divisions[div][school][position]:
          sailorObject = getSailorOrCreate(sailor)
          racesSailed = racesSailedParser(divisions[div][school][position][sailor])
          for race in racesSailed:
            createRaceResult(sailorObject,race,scores[shortSchoolName][div][race],position)

  def racesSailedParser(races):
    """Return list of integers representing the races sailed by a sailor"""

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

  def createRaceResult(sailor,raceNumber,finishPlace,position):
    """Create RaceResult for sailor and regatta.

    Keyword arguments:
    sailor -- sailor object
    raceNumber
    finishPlace --
    position -- skipper or crew etc.
    """