from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class School(Base):
    __tablename__ = 'schools'
    id = Column(Integer, primary_key=True)
    sailors = relationship("Sailor", backref="school")
    name = Column(String(100))

    def __init__(self, name):
        self.name = name

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
    rating_history = relationship("RatingStamp", backref="sailor", order_by="RatingStamp.date")
    name_and_year = Column(String(100))
    name = Column(String(100))
    year = Column(Integer)
    races_sailed = Column(Integer)
    provisional = Column(Boolean)
    current_rating = Column(Integer)
    current_rank = Column(Integer)

    def __init__(self, name_and_year, school, start_rating, provisional=True):
        self.name_and_year = name_and_year
        self.school = school
        self.name = name_and_year[:-4]
        self.year = int(name_and_year[-2:])+2000
        self.current_rating = start_rating
        self.provisional = provisional
        self.races_sailed = 0


class RatingStamp(Base):
    __tablename__ = 'ratingstamps'
    id = Column(Integer, primary_key=True)
    sailor_id = Column(Integer, ForeignKey('sailors.id'))
    rating = Column(Integer)
    rank = Column(Integer)
    date = Column(Date)

    def __init__(self, sailor, rating, rank, date):
        self.sailor = sailor
        self.rating = rating
        self.rank = rank
        self.date = date


class Season(Base):
    __tablename__ = 'seasons'
    id = Column(Integer, primary_key=True)
    weeks = relationship("Week", backref="season", order_by="Week.number")
    name = Column(String(50))
    url = Column(String(200))

    def __init__(self, name, weeks, url):
        self.name = name
        self.weeks = weeks
        self.url = url


class Week(Base):
    __tablename__ = 'weeks'
    id = Column(Integer, primary_key=True)
    season_id = Column(Integer, ForeignKey('seasons.id'))
    regattas = relationship("Regatta", backref="week")
    number = Column(Integer)

    def __init__(self, regattas, number, season_id):
        self.regattas = regattas
        self.number = number
        self.season_id = season_id


class Regatta(Base):
    __tablename__ = 'regattas'
    id = Column(Integer, primary_key=True)
    week_id = Column(Integer, ForeignKey('weeks.id'))
    # races will have races from many divisions, they are treated independently
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
    date = Column(Date)

    def __init__(self, name, url, host, date, tier, boat, scoring, summary):
        self.name = name
        self.url = url
        self.host = host
        self.tier = tier
        self.boat = boat
        self.scoring = scoring
        self.summary = summary
        self.date = date


class Race(Base):
    __tablename__ = 'races'
    id = Column(Integer, primary_key=True)
    regatta_id = Column(Integer, ForeignKey('regattas.id'))
    race_results = relationship("RaceResult", backref="race", order_by="RaceResult.finish_value")
    sailors = relationship('Sailor', secondary=sailors_races, backref='races')
    race_number = Column(Integer)
    division = Column(String(10))

    def __init__(self, race_number, regatta, division):
        self.race_number = race_number
        self.regatta = regatta
        self.division = division


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
    finish_place = Column(String(200))
    finish_value = Column(Integer)
    division = Column(String(20))

    def __init__(self, skipper, race_number, finish_place, finish_value, division, race_object):
        self.skipper_sailor = skipper
        self.race_number = race_number
        self.finish_place = finish_place
        self.finish_value = finish_value
        self.division = division
        self.race = race_object
