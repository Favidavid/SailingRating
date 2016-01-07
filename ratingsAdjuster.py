from elo import adjust_1vs1
from dbinit import RatingStamp


PROVISIONAL_MIN = 5
K_FACTOR = 5.0

sailor_stats = {}
def process_regatta_ratings(regatta, session):
  for sailor in regatta.sailors:
    # [adjustment_sum, no_races_sailed]
    sailor_stats[sailor.name_and_year] = [0,0]
  for race in regatta.races:
    process_race(race)
  for sailor in regatta.sailors:
    cumulative_adj = sailor_stats[sailor.name_and_year][0]
    num_sailed = sailor_stats[sailor.name_and_year][1]
    print "======= " + sailor.name_and_year
    print sailor_stats[sailor.name_and_year]
    if num_sailed == 0:
      print "zero races"
      continue
    sailor.current_rating += int(round(cumulative_adj))#/ float(num_sailed)))
    new_rating = RatingStamp(sailor, sailor.current_rating, 0, regatta.date)
    sailor.races_sailed += num_sailed
    if sailor.provisional:
      if sailor.races_sailed >= PROVISIONAL_MIN:
        sailor.provisional = False
    session.add(new_rating)
    session.add(sailor)

def process_race(race):
  for race_result in race.race_results:
    adjust_skipper_rating_race(race_result, race)

def adjust_skipper_rating_race(race_result,race):
  race_adjustment = float()
  fin_val = race_result.finish_value
  skipper = race_result.skipper_sailor
  for o_race_result in race.race_results: #opponent race result
    if (o_race_result.id != race_result.id) and (skipper.provisional or not o_race_result.skipper_sailor.provisional):
      o_skipper = o_race_result.skipper_sailor
      if fin_val > o_race_result.finish_value:
        race_adjustment -= K_FACTOR * adjust_1vs1(skipper.current_rating, o_skipper.current_rating)
        print "win "+str(adjust_1vs1(skipper.current_rating, o_skipper.current_rating))
      elif fin_val < o_race_result.finish_value:
        race_adjustment += K_FACTOR * adjust_1vs1(skipper.current_rating, o_skipper.current_rating)
        print "lose "+str(adjust_1vs1(skipper.current_rating, o_skipper.current_rating))
      else:
        race_adjustment += K_FACTOR * adjust_1vs1(skipper.current_rating, o_skipper.current_rating, True)
        print "tie "+str(adjust_1vs1(skipper.current_rating, o_skipper.current_rating, True))
  sailor_stats[skipper.name_and_year][0] += race_adjustment
  sailor_stats[skipper.name_and_year][1] += 1

def adjust_rankings():
  return None