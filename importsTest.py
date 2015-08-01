from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbinit import School, Sailor, RatingStamp, Season, Regatta, RaceResult, Base

engine = create_engine('mysql+pymysql://root:password@localhost/test6')
Session = sessionmaker()
Session.bind = engine
Base.metadata.bind = engine
session = Session()

regatta = session.query(Regatta)[0]

# test_school = School(name='testname2')

# session.add(test_school)
# session.commit()

# test_sailor = Sailor(nameandyear='testnameandyear2', school=test_school, name='testname2', year=2016, currentrating=1000, currentrank =10)
# session.add(test_sailor)
# session.commit()

# session.query(School)[0]