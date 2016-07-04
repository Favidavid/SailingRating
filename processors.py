import sqlalchemy
import scrapers
import populators
import ratings
import argparse
import traceback
import sys
from dbinit import Base

parser = argparse.ArgumentParser()
parser.add_argument("-db", nargs='?', dest='db_name')
parser.add_argument("-s", nargs='?', dest='season')
parser.add_argument("-w", nargs='?', dest='week')
parser.add_argument("-r", nargs='?', dest='regatta')
args = parser.parse_args()

DB_DOMAIN = "mysql+pymysql://root:password@localhost/"
REGATTA_DOMAIN = "http://scores.collegesailing.org/"


def main():
    # test_run_regatta(args.db_name, args.regatta)
    # ratingsAdjuster.process_regatta_ratings()
    # test_run_week(args.db_name, args.season, args.week)
    test_run_full(args.db_name)


def test_run_regatta(db_name, regatta_name):
    # create_test_db(db_name)
    reset_db()
    session_class = get_session_class(db_name)
    session = session_class()
    try:
        process_regatta(REGATTA_DOMAIN+regatta_name, session)
        session.commit()
    except:
        session.rollback()
        print(regatta_name + " was not persisted")
        traceback.print_exc(file=sys.stdout)
    finally:
        session.close()


def test_run_week(db_name, season, week_number):
    reset_db()
    session_class = get_session_class(db_name)
    process_week(REGATTA_DOMAIN+season, week_number, session_class)


def test_run_full(db_name):
    reset_db(db_name)
    process_all_regattas(db_name)


def create_test_db(new_db_name):
    create_db_engine = sqlalchemy.create_engine(DB_DOMAIN+'mysql', echo=False)
    conn = create_db_engine.connect()
    conn.execute("commit")
    conn.execute("create database " + new_db_name)
    conn.close()


def drop_db(db_name='test0'):
    engine = sqlalchemy.create_engine(DB_DOMAIN+'mysql', echo=False)
    conn = engine.connect()
    conn.execute("commit")
    conn.execute("drop database "+db_name)
    conn.close()


def reset_db(db_name='test0'):
    engine = sqlalchemy.create_engine(DB_DOMAIN+'mysql', echo=False)
    conn = engine.connect()
    conn.execute("commit")
    conn.execute("drop database "+db_name)
    conn.execute("create database "+db_name)
    conn.close()


def process_regatta(regatta_url, session):
    regatta_dict = scrapers.scrape_regatta(regatta_url)
    regatta_object = populators.populate_regatta(regatta_dict, session)
    ratings.process_regatta_ratings(regatta_object, session)

    return regatta_object


def process_week(season_url, week_num, session_class):
    session = session_class()
    week_dict = scrapers.scrape_week(season_url, week_num)
    print("    |--week " + str(week_num))
    # populate regatta objects
    regattas = []
    print(week_dict)
    for regatta_key, regatta_info in week_dict['regatta_urls'].iteritems():
        if regatta_info['scoring'] != "Combined":
            try:
                regatta_object = process_regatta(regatta_info['url'], session)
                session.commit()
                regattas.append(regatta_object)
                print("        |--"+regatta_key)
            except:
                session.rollback()
                traceback.print_exc(file=sys.stdout)
                # print("        |=="+regatta_key + " was not persisted: "+regatta_info['url'])

    # populate week object
    try:
        week_object = populators.populate_week(week_dict, regattas, session)
        session.commit()
    except:
        session.rollback()
        print("    |==week " + str(week_num) + " was not persisted")
        # raise
    finally:
        session.close()
    ratings.adjust_rankings()
    # TODO how to handle returning week object if it is not persisted
    return week_object


def process_all_regattas(db_name):
    session_class = get_session_class(db_name)
    # session=session_class.session()

    seasons_list = scrapers.scrape_seasons_ordered()
    for season in seasons_list:
        weeks_list = scrapers.scrape_weeks_ordered(season['url'])
        week_objects = []
        for week in weeks_list:
            week_object = process_week(season['url'], week['number'], session_class)
            week_objects.append(week_object)

        # persist season
        session = session_class()
        try:
            populators.populate_season(season, week_objects, session)
            session.commit()
            print("Season " + season['name'] + " ================")
        except:
            session.rollback()
            traceback.print_exc(file=sys.stdout)
            print("Season " + season['name'] + " was not persisted")
        finally:
            session.close()


def get_session_class(db_name):
    db_url = DB_DOMAIN + db_name
    engine = sqlalchemy.create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    session_class = sqlalchemy.orm.sessionmaker(bind=engine)
    return session_class

if __name__ == "__main__":
    main()
