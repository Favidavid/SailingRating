from flask import render_template, Flask
from objects import Sailor, School
from connection import db_session
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('layout.html')


@app.route('/ranking')
def ranking():
    ranking_list = db_session.query(Sailor).order_by(Sailor.current_rank).limit(100)
    return render_template('ranking.html', ranking_list=ranking_list)


@app.route('/ranking/<page_num>')
def ranking_page(page_num):
    ranking_list = db_session.query(Sailor).order_by(Sailor.current_rank).offset(100 * (int(page_num) - 1)).limit(100)
    return render_template('ranking.html', ranking_list=ranking_list)


@app.route('/sailor/<href>')
def sailor(href):
    sailor_object = db_session.query(Sailor).filter(Sailor.href == href).all()[0]
    return render_template('sailor.html', sailor=sailor_object, ratings=sailor_object.rating_history.__reversed__())


@app.route('/school/<href>')
def school(href):
    school_object = db_session.query(School).filter(School.name == href).all()[0]
    sailors = db_session.query(Sailor).join(Sailor.school).filter(School.name == href).order_by(Sailor.current_rank)
    return render_template('school.html', school=school_object, sailors=sailors)


if __name__ == '__main__':
    app.run(debug=True)
