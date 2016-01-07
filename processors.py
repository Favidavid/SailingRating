import sqlalchemy
import scrapers
import populators
import ratings
import argparse
import traceback
import sys
from dbinit import Base

parser = argparse.ArgumentParser()
parser.add_argument("db_name")
parser.add_argument("season")
parser.add_argument("week")
args = parser.parse_args()

DB_DOMAIN = "mysql+pymysql://root:password@localhost/"
REGATTA_DOMAIN = "http://scores.collegesailing.org/"

def main():
  # test_run_regatta(args.db_name, args.regatta)
  # ratingsAdjuster.process_regatta_ratings()
  test_run_week(args.db_name, args.season, args.week)

def test_run_regatta(db_name, regatta_name):
  db_url = DB_DOMAIN+db_name
  # create_test_db(db_url)
  reset_test0_db()
  engine = sqlalchemy.create_engine(db_url, echo=False)
  Base.metadata.create_all(engine)
  session_class = sqlalchemy.orm.sessionmaker(bind=engine)

  session = session_class()
  try:
    process_regatta(REGATTA_DOMAIN+regatta_name, session)
    session.commit()
  except:
    session.rollback()
    print regatta_name + " was not persisted"
    traceback.print_exc(file=sys.stdout)
  finally:
    session.close()

def test_run_week(db_name, season, week_number):
  reset_test0_db()
  db_url = DB_DOMAIN+db_name
  engine = sqlalchemy.create_engine(db_url, echo=False)
  Base.metadata.create_all(engine)
  session_class = sqlalchemy.orm.sessionmaker(bind=engine)
  session = session_class()
  process_week(REGATTA_DOMAIN+season, week_number, session)


def create_test_db(new_db_name):
  create_db_engine = sqlalchemy.create_engine(DB_DOMAIN+'mysql', echo=False)
  conn = create_db_engine.connect()
  conn.execute("commit")
  conn.execute("create database "+new_db_name)
  conn.close()

def reset_test0_db():
  create_db_engine = sqlalchemy.create_engine(DB_DOMAIN+'mysql', echo=False)
  conn = create_db_engine.connect()
  conn.execute("commit")
  conn.execute("drop database test0")
  conn.execute("create database test0")
  conn.close()

def process_regatta(regatta_url, session):
  regatta_dict = scrapers.scrape_regatta(regatta_url)
  regatta_object = populators.populate_regatta(regatta_dict, session)
  ratings.process_regatta_ratings(regatta_object, session)

  return regatta_object

def process_week(season_url, week_num, session):
  week_dict = scrapers.scrape_week(season_url, week_num)

  #populate regatta objects
  regattas = []
  for regatta_key, regatta_info in week_dict['regatta_urls'].iteritems():
    if regatta_info['scoring'] != "Combined":
      try:
        regatta_object = process_regatta(regatta_info['url'],session)
        regattas.append(regatta_object)
        session.commit()
      except:
        session.rollback()
        print regatta_key + " was not persisted"
        traceback.print_exc(file=sys.stdout)
  #populate week object
  try:
    week_object = populators.populate_week(week_dict, regattas, session)
    session.commit()
  except Exception as e:
    session.rollback()
    print "week " + week_num + " was not persisted"
    traceback.print_exc(file=sys.stdout)
  finally:
    print "finished"
    session.close()

  ratings.adjust_rankings()
  return week_object

if __name__ == "__main__":
  main()