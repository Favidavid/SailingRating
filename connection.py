from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import config

engine = create_engine(config.host + config.db + '?charset=utf8')
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define database so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()

    import objects
    Base.metadata.create_all(bind=engine)


def create_db(new_db_name):
    create_db_engine = create_engine(config.host+'mysql', echo=False)
    conn = create_db_engine.connect()
    conn.execute("commit")
    conn.execute("create database " + new_db_name)
    conn.close()


def drop_db(db_name):
    drop_engine = create_engine(config.host+'mysql', echo=False)
    conn = drop_engine.connect()
    conn.execute("commit")
    conn.execute("drop database "+db_name)
    conn.close()


def reset_db(db_name):
    reset_engine = create_engine(config.host+'mysql', echo=False)
    conn = reset_engine.connect()
    conn.execute("commit")
    conn.execute("drop database "+db_name)
    conn.execute("create database "+db_name)
    conn.close()