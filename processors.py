import sqlalchemy
import scrapers
import populateRegatta
import ratingsAdjuster
import argparse
from dbinit import Base

parser = argparse.ArgumentParser()
parser.add_argument("db_name")
parser.add_argument("regatta")
args = parser.parse_args()

DB_DOMAIN = "mysql+pymysql://root:password@localhost/"
REGATTA_DOMAIN = "http://scores.collegesailing.org/"

def main():
  test_run(args.db_name, args.regatta)
  # ratingsAdjuster.process_regatta_ratings()

def test_run(db_name, regatta_name):
  # create_test_db(db_name)
  reset_test0_db()
  db_url = DB_DOMAIN+db_name
  engine = sqlalchemy.create_engine(db_url, echo=False)
  Base.metadata.create_all(engine)

  session_class = sqlalchemy.orm.sessionmaker(bind=engine)
  session = session_class()
  process_regatta(REGATTA_DOMAIN+regatta_name, session)

def create_test_db(new_db_name):
  create_db_engine = sqlalchemy.create_engine(DB_DOMAIN+'mysql', echo=True)
  conn = create_db_engine.connect()
  conn.execute("commit")
  conn.execute("create database "+new_db_name)
  conn.close()

def reset_test0_db():
  create_db_engine = sqlalchemy.create_engine(DB_DOMAIN+'mysql', echo=True)
  conn = create_db_engine.connect()
  conn.execute("commit")
  conn.execute("drop database test0")
  conn.execute("create database test0")
  conn.close()

def process_regatta(regatta_url, session):
  regatta_dict = scrapers.scrape_regatta(regatta_url)

  regatta_object = populateRegatta.populate_regatta(regatta_dict, session)
  session.commit()

  ratingsAdjuster.process_regatta_ratings(regatta_object, session)
  session.commit()


if __name__ == "__main__":
  main()