from elo import adjust_1vs1

from database.objects import RatingStamp

PROVISIONAL_MIN = 5
K_FACTOR = 5.0


def score_week(regattas, session):
    for regatta in regattas:
        try:
            score_regatta_ratings(regatta, session)
            session.commit()
        except:
            print('regatta with url: ' + regatta.url + ', was not scored correctly')


def score_regatta_ratings(regatta, session):
    sailor_stats = {}
    for sailor in regatta.sailors:
        # [adjustment_sum, no_races_sailed]
        sailor_stats[sailor.name_and_year] = [0, 0]
    for race in regatta.races:
        for race_result in race.race_results:
            update_skipper_stats_for_one_race(race_result, race, sailor_stats)
    for sailor in regatta.sailors:
        cumulative_adj = sailor_stats[sailor.name_and_year][0]
        num_sailed = sailor_stats[sailor.name_and_year][1]
        if num_sailed == 0:
            continue
        sailor.current_rating += int(round(cumulative_adj))  # / float(num_sailed)))
        new_rating = RatingStamp(sailor, sailor.current_rating, 0, regatta.date)
        sailor.races_sailed += num_sailed
        if sailor.provisional:
            if sailor.races_sailed >= PROVISIONAL_MIN:
                sailor.provisional = False
        session.add(new_rating)
        session.add(sailor)


def update_skipper_stats_for_one_race(race_result, race, sailor_stats):
    race_adjustment = float()
    fin_val = race_result.finish_value
    skipper = race_result.skipper_sailor
    for o_race_result in race.race_results:  # opponent race result
        if (o_race_result.id != race_result.id) and \
                (skipper.provisional or not o_race_result.skipper_sailor.provisional):
            o_skipper = o_race_result.skipper_sailor
            if fin_val > o_race_result.finish_value:
                race_adjustment -= K_FACTOR * adjust_1vs1(skipper.current_rating, o_skipper.current_rating)
            elif fin_val < o_race_result.finish_value:
                race_adjustment += K_FACTOR * adjust_1vs1(skipper.current_rating, o_skipper.current_rating)
            else:
                race_adjustment += K_FACTOR * adjust_1vs1(skipper.current_rating, o_skipper.current_rating, True)
    sailor_stats[skipper.name_and_year][0] += race_adjustment
    sailor_stats[skipper.name_and_year][1] += 1


def update_rankings(session):

    session.commit()
