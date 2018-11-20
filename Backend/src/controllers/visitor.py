# -*- coding: utf-8 -*-
import os
import MySQLdb
import question
import jieba
from flask import Blueprint, g, jsonify, request

visitor = Blueprint('visitor', __name__)

def _getSomeDetail(question_id, answerer_id):
  c = g.db.cursor()
  tmp = {}
  if answerer_id:
    sql = '''select u.username, u.avatarUrl, u.status, u.description
           from user u where u.id = %d''' % answerer_id
    c.execute(sql)
    result = c.fetchone()
    tmp['answerer_username'] = result[0]
    tmp['answerer_avatarUrl'] = result[1]
    tmp['answerer_status'] = result[2]
    tmp['answerer_description'] = result[3]
  else:
    tmp['answerer_username'] = None
    tmp['answerer_avatarUrl'] = None
    tmp['answerer_status'] = None
    tmp['answerer_description'] = None

  #收听人数
  sql = 'select count(*) from listening l where l.qid = %d' % question_id
  c.execute(sql)
  listeningNum = c.fetchone()[0]
  
  #点赞人数
  sql = '''select count(*) from comment c where c.qid = %d and c.liked = 1''' % question_id
  c.execute(sql)
  praiseNum = c.fetchone()[0]

  tmp['listeningNum'] = listeningNum
  tmp['praiseNum'] = praiseNum

  return tmp

# 1. 推荐页面
@visitor.route('/api/wx/questions/recommend')
def getRecommend():
  c = g.db.cursor()
  data = {}
  data["status"] = 200

  try:
    data["data"] = []
    sql = '''select q.id, q.description, q.answerer_id, q.audioSeconds
            from question q where q.audioUrl is not null'''
    c.execute(sql)
    results = c.fetchall()
    for row in results:
      record = {'id':row[0], 'description':row[1], 'answerer_id': row[2], 'audioSeconds':row[3]}
      tmp = _getSomeDetail(row[0], row[2])
      record.update(tmp)
      data["data"].append(record)

  except:
    del data['data']
    data["errmsg"] = "推荐失败"
    data["status"] = 500

  return jsonify(data)

# 2. 点击问题后进入详情页面
@visitor.route('/api/wx/questions/<int:question_id>')
def questionDetail(question_id):
  c = g.db.cursor() 

  data = {}
  data["status"] = 200
  try:
    data["data"] = {}
    sql = '''select q.description, q.askDate, q.audioUrl, q.asker_id, q.answerer_id, q.audioSeconds
          from question q where q.id = %d''' % question_id

    c.execute(sql)
    result = c.fetchone()
    data['data']['id'] = question_id
    data['data']['description'] = result[0]
    data['data']['askDate'] = str(result[1])
    data['data']['audioUrl'] = result[2]
    data['data']['audioSeconds'] = result[5] 

    asker_id = result[3]
    answerer_id = result[4]

    sql = '''select u.username, u.avatarUrl from user u where u.id = %d''' % asker_id
    c.execute(sql)
    result = c.fetchone()
    data['data']['asker_username'] = result[0]
    data['data']['asker_avatarUrl'] = result[1]

    tmp = _getSomeDetail(question_id, answerer_id)
    data['data'].update(tmp)

  except Exception as e:
    del data['data']
    data["errmsg"] = "操作失败"
    data["status"] = 500

  return jsonify(data)

# 4. 收听
@visitor.route('/api/wx/questions/<int:question_id>/listenings', methods = ['POST'])
def listenings(question_id):
  data = {}
  data["status"] = 200
  data["data"] = {}
  try:
    sql = '''select q.audioUrl from question q where q.id = %d''' % question_id
    c = g.db.cursor()
    c.execute(sql)
    result = c.fetchone()
    data['data']['audioUrl'] = result[0]

  except:
    data["errmsg"] = "收听失败"
    data["status"] = 500

  return jsonify(data)

# 6. 搜索感兴趣的问题
@visitor.route('/api/wx/questions/find', methods=['GET'])
def findQuestion():
  data = {}
  data["status"] = 200
  args = request.args
  try:
    data['data'] = []
    query = args['query_string']
    c = g.db.cursor()

    # 分词
    query_statement = " ".join(jieba.cut(query))
    list = query_statement.split()
    
    for string in list:
      sql = """select q.id, q.description, q.answerer_id
            from question q where q.description like \'%%%s%%\' and q.audioUrl is not null""" % string
      c.execute(sql)
      result = c.fetchall()

      for row in result:
        record = {'id':row[0], 'description':row[1], 'answerer_id':row[2]}
        tmp = _getSomeDetail(row[0], row[2])
        record.update(tmp)
        data['data'].append(record)
    
  except Exception as e:
    del data['data']
    data['status'] = 500
    data['errmsg'] = '搜索失败'

  return jsonify(data)
