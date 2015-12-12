from elo import rate_1vs1
from dbinit import RatingStamp

sailor_stats = {}
def process_regatta_ratings(regatta):
  for sailor in regatta.sailors:
    # [adjustment_sum, no_races_sailed]
    sailor_stats[sailor.name_and_year] = [0,0]
  for race in regatta.races:
    process_race(race)
  for sailor in regatta.sailors:
    sailor.current_rating += sailor_stats[sailor.name_and_year][0]
    new_rating = RatingStamp(sailor, sailor.current_rating, 0, )
    sailor.races_sailed += sailor_stats[sailor.name_and_year][1]
    if sailor.provisional:
      if sailor.races_sailed >= 10:
        sailor.provisional = False

def process_race(race):
  for race_result in race.race_results:
    adjust_skipper_rating_race(race_result, race)

def adjust_skipper_rating_race(race_result,race):
  race_adjustment=0
  fin_val = race_result.finish_value
  skipper = race_result.skipper_sailor
  for o_race_result in race.race_results:
    if (o_race_result.id != race_result.id) and (not o_race_result.skipper_sailor.provisional or skipper.provisional):
      o_skipper = o_race_result.skipper_sailor
      if fin_val > o_race_result.finish_value:
        race_adjustment += rate_1vs1(skipper.current_rating, o_skipper.current_rating)[0]
      elif fin_val < o_race_result.finish_value:
        race_adjustment += rate_1vs1(o_skipper.current_rating, skipper.current_rating)[1]
      else:
        race_adjustment += rate_1vs1(o_skipper.current_rating, skipper.current_rating, True)[1]
  sailor_stats[skipper.name_and_year][1] += 1
  sailor_stats[skipper.name_and_year][0] += race_adjustment

