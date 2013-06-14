# -*- encoding:utf-8 -*-

from sqlalchemy import Column, Integer, String, DateTime, Text
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True)
    name = Column(String(50), unique = True)
    password = Column(String(50), unique = True)
    
    def __init__(self, name, password):
        self.name = name
        self.password = password

    def __rept__(self):
        return "User<'%s', '%s'>" % (self.username, self.password)


class Memo(Base):
    __tablename__ = 'memos'
    id = Column(Integer, primary_key = True)
    title = Column(String(200), nullable = False, unique = True)
    text = Column(Text, nullable = False)
    tag = Column(String(100), nullable = False)
    date_time = Column(DateTime(), unique = True)

    def __init__(self, title, text, tag, date_time):
        self.title = title
        self.text = text
        self.tag = tag
        self.date_time = date_time

    def __rept__(self):
        return u"Memo<'%s', '%s', '%s', '%s'>" % (self.title, self.text,
                self.tag, self.date_time.strftime('%Y/%m/%d %H:%M:%S'))

