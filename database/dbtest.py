import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
print sqlalchemy.__version__

engine = create_engine('mysql+pymysql://root:password@localhost/test', echo=True)
Base = declarative_base()

class School(Base):
  __tablename__ = 'schools'
  id = Column(Integer, primary_key=True)
  sailors = relationship("Sailor", backref="school", order_by="id")
  name = Column(String(100))
  shortname = Column(String(100))
  division = Column(String(100))



class Sailor(Base):
  __tablename__ = 'sailors'
  id = Column(Integer, primary_key=True)
  school_id = Column(Integer, ForeignKey('schools.id'))
  ratinghistory = relationship("RatingStamp", backref="sailor", order_by="id")
  raceresults = relationship("RaceResult", backref="sailor", order_by="id")
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
  regattas = relationship("Regatta", backref="season", order_by="id")
  name = Column(String(50))


class Regatta(Base):
  __tablename__ = 'regattas'
  id = Column(Integer, primary_key=True)
  raceresults = relationship("RaceResult", backref="regatta", order_by="id")
  date = Column(Date)


class RaceResult(Base):
  __tablename__ = 'raceresults'
  id = Column(Integer, primary_key=True)
  sailor_id = Column(Integer, ForeignKey('sailors.id'))
  regatta_id = Column(Integer, ForeignKey('regattas.id'))
  racenumber = Column(Integer)
  placement = Column(Integer)
  position = Column(String(10))

Base.metadata.create_all(engine)
# Session = sessionmaker(bind=engine)
