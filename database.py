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
    Base.metadata.create_all(bind=engine)


def add_user(name, password):
    from models import User
    u = User(name, password)
    db_session.add(u)
    db_session.commit()


def delete_user(user):
    db_session.delete(user)
    db_session.commit()


def add_entry(title, text, tag):
    from models import Memo
    now = datetime.datetime.today()
    memo = Memo(title, text, tag, now)
    db_session.add(memo)
    db_session.commit()


def delete_entry(id):
    from models import Memo
    memo = Memo.query.filter(Memo.id == id).first()
    if memo:
        db_session.delete(memo)
        db_session.commit()


def close_db():
    db_session.remove()
