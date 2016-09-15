import argparse
import sys
import traceback

import sqlalchemy
from objects import Base
import config
import connection

import populators
import ratings
import scrapers

parser = argparse.ArgumentParser()
parser.add_argument("-db", nargs='?', dest='db_name')
parser.add_argument("-s", nargs='?', dest='season')
parser.add_argument("-w", nargs='?', dest='week')
parser.add_argument("-r", nargs='?', dest='regatta')
args = parser.parse_args()


def main():
    # test_run_regatta(args.db_name, args.regatta)
    # ratingsAdjuster.process_regatta_ratings()
    # test_run_week(args.db_name, args.season, args.week)
    test_run_full()


def test_run_regatta(regatta_name):
    # create_test_db(db_name)
    connection.reset_db()
    session = connection.db_session
    try:
        process_regatta(config.regatta_domain+regatta_name, session)
        session.commit()
    except:
        session.rollback()
        print(regatta_name + " was not persisted")
        traceback.print_exc(file=sys.stdout)
    finally:
        session.close()


def test_run_week(season, week_number):
    connection.reset_db()
    session = connection.db_session
    process_week(season, week_number, session)


def test_run_full():
    connection.reset_db()
    process_all_regattas()


def process_regatta(regatta_url, session):
    regatta_dict = scrapers.scrape_regatta(regatta_url)
    regatta_object = populators.populate_regatta(regatta_dict, session)
    ratings.update_regatta_sailor_ratings(regatta_object)

    return regatta_object


def process_week(season_id, week_num, session):
    print("\n  WEEK " + str(week_num) + '   ===')
    week_regatta_dicts = scrapers.scrape_week(season_id=season_id, week_num=week_num)
    week_object = populators.populate_week(season_id, week_num, week_regatta_dicts, session)
    ratings.score_week(week_object, session)
    ratings.update_rankings_for_week(week_object, session)
    return week_object


def process_all_regattas():
    seasons_list = scrapers.scrape_seasons_ordered_recent_first()
    for season_id in seasons_list.__reversed__():
        print("\nSEASON " + str(season_id) + ' =====================')
        weeks_list = scrapers.scrape_weeks_ordered_recent_first(season_id)
        for week_id in weeks_list.__reversed__():
            week_object = process_week(season_id=season_id, week_num=week_id, session=connection.db_session)

        # persist season
        # try:
        #     populators.populate_season(season, week_objects, session)
        #     session.commit()
        #     print("\n\n\nSEASON" + season['id'] + '   ' + season['name'] + ' ==================')
        # except:
        #     session.rollback()
        #     traceback.print_exc(file=sys.stdout)
        #     print("Season " + season['name'] + " was not persisted")
        # finally:
        #     session.close()


def process_all_start_point(start_season_id, start_week_id):
    seasons_list = scrapers.scrape_seasons_ordered_recent_first()
    for season_id in seasons_list[:seasons_list.index(start_season_id)+1].__reversed__():
        print("\nSEASON " + str(season_id) + ' =====================')
        weeks_list = scrapers.scrape_weeks_ordered_recent_first(season_id)
        if season_id == start_season_id:
            weeks_list = weeks_list[:weeks_list.index(start_week_id)+1]
        for week_id in weeks_list.__reversed__():
            week_object = process_week(season_id=season_id, week_num=week_id, session=connection.db_session)


if __name__ == "__main__":
    main()
