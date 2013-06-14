# -*- encoding:utf-8 -*-

import os
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_PATH = os.environ['MEMO_DB']

engine = create_engine(DB_PATH, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import models
    Base.metadata.create_all(bind = engine)


def add_user(name, password):
    from models import User
    u = User(name, password)
    db_session.add(u)
    db_session.commit()


def delete_user(user):
    db_session.delete(user)
    db_session.commit()


def close_db():
    db_session.remove()
