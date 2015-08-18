import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Date, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
print sqlalchemy.__version__

engine = create_engine('mysql+pymysql://root:password@localhost/test6', echo=True)
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
  Column('school_id', Integer, ForeignKey('schools.id')),
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
  rating_history = relationship("RatingStamp", backref="sailor")
  name_and_year = Column(String(100))
  name = Column(String(100))
  year = Column(Integer)
  current_rating = Column(Integer)
  current_rank = Column(Integer)


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
  weeks = relationship("Week", backref="season", order_by="Week.number")
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
  #races will have races from many divisions, they are treated independently
  races = relationship("Race", backref="regatta", order_by="Race.race_number")
  sailors = relationship('Sailor', secondary=sailors_regattas, backref='regattas')
  schools = relationship('School', secondary=schools_regattas, backref='regattas')
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
  race_results = relationship("RaceResult", backref="race", order_by="RaceResult.finish_value")
  sailors = relationship('Sailor', secondary=sailors_races, backref='races')
  race_number = Column(Integer)
  division = Column(String(10))

class RaceResult(Base):
  """
  A race result will always have a skipper, and 0 or 1 crew
  """
  __tablename__ = 'raceresults'
  id = Column(Integer, primary_key=True)
  skipper_sailor_id = Column(Integer, ForeignKey('sailors.id'))
  crew_sailor_id = Column(Integer, ForeignKey('sailors.id'))
  race_id = Column(Integer, ForeignKey('races.id'))
  skipper_sailor = relationship("Sailor", foreign_keys=skipper_sailor_id, backref="skipper_race_results")
  crew_sailor = relationship("Sailor", foreign_keys=crew_sailor_id, backref="crew_race_results")
  race_number = Column(Integer)
  finish = Column(String(50))
  finish_value = Column(Integer)
  division = Column(String(20))

Base.metadata.create_all(engine)
