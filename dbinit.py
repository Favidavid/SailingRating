import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Date, Text, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
print sqlalchemy.__version__

engine = create_engine('mysql+pymysql://root:password@localhost/test4', echo=True)
Base = declarative_base()

class School(Base):
  __tablename__ = 'schools'
  id = Column(Integer, primary_key=True)
  sailors = relationship("Sailor", backref="school")
  name = Column(String(100))

sailors_regattas = Table('sailors_regattas', Base.metadata,
  Column('sailor_id', Integer, ForeignKey('sailors.id')),
  Column('regatta_id', Integer, ForeignKey('regattas.id'))
)

schools_regattas = Table('schools_regattas', Base.metadata,
  Column('sailor_id', Integer, ForeignKey('sailors.id')),
  Column('regatta_id', Integer, ForeignKey('regattas.id'))
)

sailors_races = Table('sailors_races', Base.metadata,
  Column('sailor_id', Integer, ForeignKey('sailors.id')),
  Column('race_id', Integer, ForeignKey('races.id'))
)

class Sailor(Base):
  __tablename__ = 'sailors'
  id = Column(Integer, primary_key=True)
  school_id = Column(Integer, ForeignKey('schools.id'))
  ratinghistory = relationship("RatingStamp", backref="sailor")
  raceresults = relationship("RaceResult", backref="sailor")
  regattas = relationship("Regatta", secondary=sailors_regattas, backref="sailors")
  nameandyear = Column(String(100))
  name = Column(String(100))
  year = Column(Integer)
  currentrating = Column(Integer)
  currentrank = Column(Integer)


class RatingStamp(Base):
  __tablename__ = 'ratingstamps'
  id = Column(Integer, primary_key=True)
  sailor_id = Column(Integer, ForeignKey('sailors.id'))
  rating = Column(Integer)
  rank = Column(Integer)
  date = Column(Date)


class Season(Base):
  __tablename__ = 'seasons'
  id = Column(Integer, primary_key=True)
  weeks = relationship("Week", backref="season")
  name = Column(String(50))

class Week(Base):
  __tablename__ = 'weeks'
  id = Column(Integer, primary_key=True)
  season_id = Column(Integer, ForeignKey('seasons.id'))
  regattas = relationship("Regatta", backref="week")
  number = Column(Integer)
  date = Column(Date)

class Regatta(Base):
  __tablename__ = 'regattas'
  id = Column(Integer, primary_key=True)
  week_id = Column(Integer, ForeignKey('weeks.id'))
  races = relationship("Race", backref="regatta")
  sailors = relationship('Sailor', secondary=sailors_regattas, backref='regattas')
  schools = relationship('School', secondary=schoos_regattas, backref='regattas')
  name = Column(String(200))
  url = Column(String(200))
  host = Column(String(200))
  tier = Column(String(100))
  boat = Column(String(50))
  scoring = Column(String(50))
  summary = Column(Text)

class Race(Base):
  __tablename__ = 'races'
  id = Column(Integer, primary_key=True)
  regatta_id = Column(Integer, ForeignKey('regattas.id'))
  raceresults = relationship("RaceResult", backref="race")
  sailors = relationship('Sailor', secondary=sailors_races, backref='races')
  racenumber = Column(Integer)

class RaceResult(Base):
  __tablename__ = 'raceresults'
  id = Column(Integer, primary_key=True)
  sailor_id = Column(Integer, ForeignKey('sailors.id'))
  race_id = Column(Integer, ForeignKey('races.id'))
  racenumber = Column(Integer)
  finishplace = Column(String(10))
  division = Column(String(20))
  sailingposition = Column(String(20))

Base.metadata.create_all(engine)
