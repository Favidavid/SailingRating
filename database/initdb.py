from sqlalchemy import create_engine
from sqlalchemy import declarative_base
engine = create_engine('mysql+pymysql:///:memory:', echo=True)