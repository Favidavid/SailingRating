from elo import rate_1vs1
from dbinit import *

def adjust_ratings(regatta):
  """
  This is a testing ratings adjuster. It takes a regatta already in a database, 
  updates the sailor's currentrating, and creates a new ratingstamp
  """
  sailor_stats = {}
  for sailor in regatta.sailors: #[start,adjustment,#sailed,avgpointsfront,avgpointsb]
    sailor_stats[sailor.name_and_year] = [sailor.current_rating,0,0,0,0]
  for race in regatta.races:
    for race_result in race.race_results:
      race_result.
