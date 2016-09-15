from elo import adjust_1vs1

from objects import RatingStamp, Sailor
from config import k_factor, k_lose_factor, crew_c_k_factor, crew_c_k_lose_factor, crew_s_k_factor, crew_s_k_lose_factor
from config import provisional_min


def score_week(week, session):
    unique_sailor_objects = set()
    for regatta in week.regattas:
        update_regatta_sailor_ratings(regatta)
        session.commit()
        unique_sailor_objects.update(regatta.sailors)
    ratings = create_rating_stamps_for_week(sailor_objects=unique_sailor_objects, week=week)
    session.add_all(ratings)
    session.commit()


def update_rankings_for_week(week, session):
    sailors = Sailor.query.order_by(Sailor.current_rating).all()
    for rank, sailor in enumerate(sailors.__reversed__()):
        sailor.current_rank = rank + 1
    for sailor_rating in week.rating_stamps:
        sailor_rating.rank = sailor_rating.sailor.current_rank
    session.commit()


def update_regatta_sailor_ratings(regatta):
    sailor_stats = {}
    for sailor in regatta.sailors:
        # [adjustment_sum, no_races_sailed]
        sailor_stats[sailor.name_and_year] = [0, 0]
    for race in regatta.races:
        for race_result in race.race_results:
            update_skipper_stats_for_one_race(race_result, race, sailor_stats)
            update_crew_stats_for_one_race(race_result, race, sailor_stats)
    for sailor in regatta.sailors:
        cumulative_adj = sailor_stats[sailor.name_and_year][0]
        num_sailed = sailor_stats[sailor.name_and_year][1]
        if num_sailed == 0:
            continue
        sailor.current_rating += int(round(cumulative_adj))  # / float(num_sailed)))
        sailor.races_sailed += num_sailed
        if sailor.provisional:
            if sailor.races_sailed >= provisional_min:
                sailor.provisional = False


def update_skipper_stats_for_one_race(race_result, race, sailor_stats):
    race_adjustment = float()
    fin_val = race_result.finish_value
    skipper = race_result.skipper_sailor
    if not skipper:
        return
    for o_race_result in race.race_results:  # opponent race result
        if (o_race_result.id != race_result.id) and o_race_result.skipper_sailor and \
                (skipper.provisional or not o_race_result.skipper_sailor.provisional):
            o_skipper = o_race_result.skipper_sailor
            if not o_skipper:
                continue
            if fin_val > o_race_result.finish_value:
                race_adjustment -= k_lose_factor * adjust_1vs1(skipper.current_rating, o_skipper.current_rating)
            elif fin_val < o_race_result.finish_value:
                race_adjustment += k_factor * adjust_1vs1(skipper.current_rating, o_skipper.current_rating)
            else:
                race_adjustment += k_factor * adjust_1vs1(skipper.current_rating, o_skipper.current_rating, True)
    sailor_stats[skipper.name_and_year][0] += race_adjustment
    sailor_stats[skipper.name_and_year][1] += 1


def update_crew_stats_for_one_race(race_result, race, sailor_stats):
    race_adjustment = float()
    fin_val = race_result.finish_value
    crew = race_result.crew_sailor
    if not crew:
        return
    for o_race_result in race.race_results:  # opponent race result
        if (o_race_result.id != race_result.id) and o_race_result.skipper_sailor and \
                (crew.provisional or not o_race_result.skipper_sailor.provisional):
            o_skipper = o_race_result.skipper_sailor
            if not o_skipper:
                continue
            if fin_val > o_race_result.finish_value:
                race_adjustment -= crew_s_k_lose_factor * adjust_1vs1(crew.current_rating, o_skipper.current_rating)
            elif fin_val < o_race_result.finish_value:
                race_adjustment += crew_s_k_factor * adjust_1vs1(crew.current_rating, o_skipper.current_rating)
            else:
                race_adjustment += crew_s_k_factor * adjust_1vs1(crew.current_rating, o_skipper.current_rating, True)
    for o_race_result in race.race_results:  # opponent race result
        if (o_race_result.id != race_result.id) and o_race_result.crew_sailor and \
                (crew.provisional or not o_race_result.crew_sailor.provisional):
            o_crew = o_race_result.crew_sailor
            if not o_crew:
                continue
            if fin_val > o_race_result.finish_value:
                race_adjustment -= crew_c_k_lose_factor * adjust_1vs1(crew.current_rating, o_crew.current_rating)
            elif fin_val < o_race_result.finish_value:
                race_adjustment += crew_c_k_factor * adjust_1vs1(crew.current_rating, o_crew.current_rating)
            else:
                race_adjustment += crew_c_k_factor * adjust_1vs1(crew.current_rating, o_crew.current_rating, True)

    sailor_stats[crew.name_and_year][0] += race_adjustment
    sailor_stats[crew.name_and_year][1] += 1


def create_rating_stamps_for_week(sailor_objects, week):
    ratings = []
    for sailor in sailor_objects:
        new_rating = RatingStamp(sailor=sailor, rating=sailor.current_rating, rank=0, week=week)
        ratings.append(new_rating)
    return ratings
