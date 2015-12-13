import sqlalchemy
import scrapers
import populateRegatta
import ratingsAdjuster
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("db_name")
args = parser.parse_args()

DB_DOMAIN = "mysql+pymysql://root:password@localhost/"
REGATTA_DOMAIN = "http://scores.collegesailing.org/"

def main():
  test_run(args.db_name)

def test_run(db_name):
  create_test_db(db_name)
  db_url = DB_DOMAIN+db_name
  engine = sqlalchemy.create_engine(db_url, echo=True)
  session_class = sqlalchemy.orm.sessionmaker(bind=engine)
  session = session_class()

  # from dbinit:
  #
  # Base = declarative_base()
  # Base.metadata.create_all(engine)

def create_test_db(new_db_name):
  engine = sqlalchemy.create_engine(DB_DOMAIN+'mysql', echo=True)
  conn = engine.connect()
  conn.execute("commit")
  conn.execute("create database "+new_db_name)
  conn.close()

def process_regatta(regatta_url, session):
  regatta_dict = scrapers.scrape_regatta(regatta_url)

  regatta_object = populateRegatta.populate_regatta(regatta_dict, session)
  session.commit()

  ratingsAdjuster.process_regatta_ratings(regatta_object, session)
  session.commit()


if __name__ == "__main__":
  main()