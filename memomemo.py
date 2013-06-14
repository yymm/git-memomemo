# -*- encoding: utf-8 -*-

from __future__ import with_statement

import os
import datetime

from docutils.core import publish_parts
from docutils.parsers.rst import directives

from flask import Flask, render_template, session, \
                    Markup, request, redirect, url_for

from models import Memo, User
from database import init_db, close_db, db_session

#from wdb import Wdb

from sphinx.directives.other import *
from sphinx.directives.code import *

import rst_directive

from sqlalchemy import and_

# Configuration
DEBUG = True
SECRET_KEY = 'development key'

app = Flask(__name__)

# Wdb Setting
#app.debug = True
#app.wsgi_app = Wdb(app.wsgi_app)

app.config.from_object(__name__)
app.config.from_envvar('FLASK_SETTINGS', silent=True)

# gloval value
error_msg = None
filter_word = None

@app.teardown_appcontext
def close_db_connection(exception):
    close_db()


@app.route('/')
def show_memos():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    error = None
    if error_msg:
        error = error_msg
    entries = create_memos_dic()
    tags = create_tags_dic()
    home_html = queryHome()
    return render_template('show_memos.html', **locals())


def addTodo(entries):
    todo = Memo.query.filter(Memo.tag == "TODO").first()
    entries.insert(0, todo)


def queryHome():
    home = Memo.query.filter(Memo.tag == "bookmark").first()
    return parse_rst(home.text)


def create_memos_dic():
    global filter_word
    memos = queryMemo()
    filter_word = None
    entries = []
    for memo in memos:
        dic = {}
        dic['id'] = memo.id
        dic['title'] = memo.title
        dic['basetext'] = memo.text
        dic['text'] = parse_rst(memo.text)
        dic['tag'] = memo.tag
        dic['date_time'] = memo.date_time.strftime('%Y/%m/%d %H:%M:%S')
        entries.append(dic)
    return entries
    

def create_tags_dic():
    # 参照countHash
    # http://d.hatena.ne.jp/shakezo/20120211/1328948595
    countHash = {}
    for memo in Memo.query.all():
        tags = memo.tag.split(',')
        for tag in tags:
            tag = tag.strip()
            if countHash.has_key(tag):
                countHash[tag] += 1
            else:
                countHash[tag] = 1

    tags = []
    for key in countHash:
        value = countHash[key]
        tag_dic = {}
        tag_dic["name"] = key
        tag_dic["size"] = value * 10
        tag_dic["url"] = url_for('search_memo') + '?tag=' + key
        tags.append(tag_dic)

    return tags


def parse_rst(rst):
    return Markup(publish_parts(rst, writer_name='html')['body'])


def queryMemo():
    before_now = u"date_time<='" + str(datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'))+"'"
    
    # non filter -> bookmark and memos in a week
    if not filter_word:
        time_delta = datetime.datetime.today() - datetime.timedelta(7)
        default_time_filter = u"date_time>='" + str(time_delta.strftime('%Y-%m-%d %H:%M:%S'))+"'"
        filter_str = and_(before_now, default_time_filter)
        memos = Memo.query.filter(filter_str).order_by(Memo.date_time.desc()).all()
        addTodo(memos)
        return memos

    ftitle = filter_word['title']
    ftag = filter_word['tag']
    fdate = filter_word['date']
    
    if ftitle:
        if fdate:
            time_delta = datetime.datetime.today() - datetime.timedelta(int(fdate))
            time_filter = u"date_time>='" + str(time_delta.strftime('%Y-%m-%d %H:%M:%S'))+"'"
            filter_str = and_(Memo.title == ftitle, before_now, time_filter)
            return Memo.query.filter(filter_str).order_by(Memo.date_time.desc()).all()
        return Memo.query.filter(Memo.title == ftitle).order_by(Memo.date_time.desc()).all()

    if ftag:
        match_tag = "%" + ftag + "%"
        if fdate:
            time_delta = datetime.datetime.today() - datetime.timedelta(int(fdate))
            time_filter = u"date_time>='" + str(time_delta.strftime('%Y-%m-%d %H:%M:%S'))+"'"
            filter_str = and_(Memo.tag.like(match_tag), before_now, time_filter)
            return Memo.query.filter(filter_str).order_by(Memo.date_time.desc()).all()
        return Memo.query.filter(Memo.tag.like(match_tag)).order_by(Memo.date_time.desc()).all()
    
    if fdate:
        time_delta = datetime.datetime.today() - datetime.timedelta(int(fdate))
        time_filter = u"date_time>='" + str(time_delta.strftime('%Y-%m-%d %H:%M:%S'))+"'"
        filter_str = and_(before_now, time_filter)
        return Memo.query.filter(filter_str).order_by(Memo.date_time.desc()).all()

    return Memo.query.order_by(Memo.date_time.desc()).all()



@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        exist_user = False
        users = User.query.all()
        for user in users:
            if request.form['username'] == user.name:
                exist_user = True
        exist_password = False
        for user in users:
            if request.form['password'] == user.password:
                exist_password = True
        if not exist_user:
            error = 'Invalid username'
        elif not exist_password:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            return redirect(url_for('show_memos'))
    return render_template('login.html', **locals())


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


@app.route('/add', methods=['POST'])
def add_memo():
    global error_msg
    error_msg = None
    if not session.get('logged_in'):
        abort(404)
    title = request.form['title']
    text = request.form['text']
    tag = request.form['tag']
    today = datetime.datetime.today()
    if len(title) == 0 or len(text) == 0 or len(tag) == 0:
        error_msg = 'Invalid entry'
    else:
        # 同じタイトルは上書きされる
        memo = Memo.query.filter(Memo.title == title).first()
        if memo:
            update_memo(memo, text, tag, today)
        else:
            m = Memo(title, text, tag, today)
            db_session.add(m)
            db_session.commit()
    return redirect(url_for('show_memos'))


@app.route('/delete', methods=['GET'])
def delete_memo():
    global error_msg
    error_msg = None
    memo_id = request.args['memo-id']
    memo = Memo.query.filter(Memo.id == memo_id).first()
    if memo:
        db_session.delete(memo)
        db_session.commit()
    else:
        error_msg = 'No entry...'
    return redirect(url_for('show_memos'))


def update_memo(memo, text, tag, today):
    memo.text = text
    memo.tag = tag
    memo.today = today
    db_session.commit()


@app.route('/search', methods=['POST', 'GET'])
def search_memo():
    global filter_word
    filter_word = { 'title' : None, 'tag' : None, 'date' : None }
    
    if request.method == 'POST':
        title= request.form['title']
        tag= request.form['tag']
        date = request.form['date']
    else:
        title = ''
        tag = request.args['tag']
        date = ''

    filter_word['title'] = title if len(title) != 0 else None
    filter_word['tag'] = tag if len(tag) != 0 else None
    filter_word['date'] = date if len(date) != 0 else None
    return redirect(url_for('show_memos'))


if __name__ == '__main__':
    init_db()
    #users = User.query.all()
    #if len(users) == 0:
        #add_user('hoge', 'hoge')
    #app.run(host=os.environ['MEMO_HOST'], port=int(os.environ['MEMO_PORT']))
    # deployment heroku
    app.run()
