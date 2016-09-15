import datetime
host = "mysql+pymysql://root:password@localhost/"
regatta_domain = "http://scores.collegesailing.org/"
db = 'new2'
app = {
    'db_name':'app'
}
season = {  # sunday (end) of the first week in each season
    'f08': datetime.date(2008, 9, 7),
    's09': datetime.date(2009, 2, 8),
    'f09': datetime.date(2009, 9, 6),
    's10': datetime.date(2010, 2, 7),
    'f10': datetime.date(2010, 9, 5),
    's11': datetime.date(2011, 2, 6),
    'f11': datetime.date(2011, 9, 4),
    's12': datetime.date(2012, 2, 5),
    'f12': datetime.date(2012, 9, 2),
    's13': datetime.date(2013, 2, 3),
    'f13': datetime.date(2013, 9, 8),
    's14': datetime.date(2014, 2, 2),
    'f14': datetime.date(2014, 9, 7),
    's15': datetime.date(2015, 2, 8),
    'f15': datetime.date(2015, 9, 6),
    's16': datetime.date(2016, 2, 7),
    'f16': datetime.date(2016, 9, 4),
}
k_factor = 5.0
k_lose_factor = 3.0

crew_s_k_factor = 2.5
crew_c_k_factor = 2.5
crew_s_k_lose_factor = 1.5
crew_c_k_lose_factor = 1.5
provisional_min = 10

regatta_url_blacklist = [
    'http://scores.collegesailing.org/s12/otoole',
    'http://scores.collegesailing.org/f11/yale-women',
    'http://scores.collegesailing.org/s15/army-spring-open'
    ]
