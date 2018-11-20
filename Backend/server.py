# -*- coding: utf-8 -*-
import sys
import MySQLdb
from datetime import timedelta
from flask import Flask, g, request

from src.controllers.wx import wx
from src.controllers.user import user
from src.controllers.question import question
from src.controllers.visitor import visitor

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.register_blueprint(wx)
app.register_blueprint(user)
app.register_blueprint(question)
app.register_blueprint(visitor)
app.secret_key = 'xue-wen_secret-key'
app.permanent_session_lifetime = timedelta(minutes=360)

def connectDB():
  try:
    return MySQLdb.connect("127.0.0.1", "root", "root", "xuewen", charset='utf8')
  except Exception as e:
    raise e

def getDB():
  if not hasattr(g, 'db'):
    g.db = connectDB()
  return g.db

def initDB():
  db = connectDB()
  with app.open_resource("sql/insert2DB.sql") as fs:
    c = db.cursor()
    lines = fs.readlines()
    for line in lines:
      c.execute(line.strip())
      db.commit()
  db.close()

@app.before_request
def before_request():
  print request.cookies
  if not hasattr(g, 'db'):
    g.db = connectDB()

@app.teardown_request
def teardown_request(exception):
  if hasattr(g, 'db'):
    g.db.close()

# 当前执行
if __name__ == '__main__':
  app.run(host = "0.0.0.0")
  # app.run(host = "0.0.0.0", debug = True)


