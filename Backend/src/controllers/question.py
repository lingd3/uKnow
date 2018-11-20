# -*- coding: utf-8 -*-
import os
import datetime
import MySQLdb
import functools
import jieba
from flask import Blueprint, g, jsonify, request, session

question = Blueprint('question', __name__)

def check_session(fun):
  @functools.wraps(fun)
  def wrapper(*args, **kw):
    if 'user_id' not in session:  # 未登录
      return jsonify({'status':403, 'errmsg':'未登录'})
    return fun(*args, **kw)
  return wrapper

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
@question.route('/api/questions/recommend')
# @check_session
def getRecommend():
  c = g.db.cursor()
  data = {}
  data["status"] = 200

  session['user_id'] = 1
  id = session['user_id']

  sql = '''select u.status from user u where u.id=%s''' % id
  c.execute(sql)
  result = c.fetchone()
  status = result[0]

  # 分词
  query_statement = " ".join(jieba.cut(status))
  list = query_statement.split()

  count = 0
  data["data"] = []
  for string in list:
    sql = """select q.id, q.description, q.answerer_id, q.audioSeconds
          from question q where q.audioUrl is not null and q.description like \'%%%s%%\'""" % string
    c.execute(sql)
    results = c.fetchall()
    for row in results:
      record = {'id':row[0], 'description':row[1], 'answerer_id': row[2], 'audioSeconds':row[3]}
      tmp = _getSomeDetail(row[0], row[2])
      record.update(tmp)
      data["data"].append(record)
      count = count+1

  if count < 20:
    sql = """select q.id, q.description, q.answerer_id, q.audioSeconds
          from question q where q.audioUrl is not null"""
    c.execute(sql)
    results = c.fetchall()
    for row in results:
      record = {'id':row[0], 'description':row[1], 'answerer_id': row[2], 'audioSeconds':row[3]}
      tmp = _getSomeDetail(row[0], row[2])
      record.update(tmp)
      data["data"].append(record)
      count = count+1
      if count > 20:
        break

  return jsonify(data)

# 2. 点击问题后进入详情页面
@question.route('/api/questions/<int:question_id>')
# @check_session
def questionDetail(question_id):
  c = g.db.cursor() 

  data = {}
  data["status"] = 200

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

  try:
    sql = '''select * from comment c where c.uid = %d and c.qid = %d''' % (int(session['user_id']), question_id)
    c.execute(sql)
    result = c.fetchone()
    if result == None:
      data['data']['commented'] = 0
    else:
      data['data']['commented'] = 1
      data['data']['liked'] = result[2]

  except Exception as e:
    del data['data']
    data["errmsg"] = "未评价"
    data["status"] = 500

  return jsonify(data)

# 4. 收听
@question.route('/api/questions/<int:question_id>/listenings', methods = ['POST'])
# @check_session
def listenings(question_id):
  data = {}
  data["status"] = 200
  data["data"] = {}

  user_id = int(session['user_id'])

  try:
    sql = '''select q.audioUrl from question q where q.id = %d''' % question_id
    c = g.db.cursor()
    c.execute(sql)
    result = c.fetchone()
    data['data']['audioUrl'] = result[0]

  except:
    data["errmsg"] = "问题未回答"
    data["status"] = 500

  return jsonify(data)

# 5.评价
@question.route('/api/questions/<int:question_id>/comments', methods=['POST'])
# @check_session
def comment(question_id):
  praise = request.form.get("praise")
  user_id = int(request.form.get("user_id"))

  c = g.db.cursor() 

  data = {}
  data["status"] = 200
  data["data"] = {}

  sql = '''select * from comment c where c.uid = %d and c.qid = %d''' % (user_id, question_id)
  c.execute(sql)
  result = c.fetchone()
  if result != None:
    data["errmsg"] = "已评价"
    data["status"] = 500
  else:
    sql = "insert into comment values (%s, %d, %d)" % (user_id, question_id, int(praise))
    try:
      if praise == "0" or praise == "1":
        c.execute(sql)
        g.db.commit()
      sql = "insert into listening values (%d, %d)" % (int(user_id), question_id)
      c.execute(sql)
      g.db.commit()

    except Exception as e:
      print e
      data["errmsg"] = "评价失败"
      data["status"] = 500

  return jsonify(data)

# 6. 搜索感兴趣的问题
@question.route('/api/questions/find', methods=['GET'])
# @check_session
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

# 9.提问
@question.route('/api/questions', methods=['POST'])
# @check_session
def askQuestion():
  description = request.form.get("description")
  askDate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  answerer_id = int(request.form.get("answerer_id"))
  asker_id = session['user_id']

  c = g.db.cursor() 
  sql = "insert into question(description, askDate, asker_id, answerer_id) values ('%s','%s', %d, %d)" % (description,askDate,asker_id,answerer_id)
  #返回的数据data
  data = {}
  data["status"]=200
  data["data"] = {}
  try:
    c.execute(sql)
    g.db.commit()
  except:
    data["errmsg"] = "提问失败"
    data["status"] = 500

  return jsonify(data)

# 12.回答问题
@question.route('/api/questions/<int:question_id>/answer', methods=['PATCH'])
# @check_session
def updateInfo(question_id):
  # answerer_id = request.form.get("answerer_id")
  audioUrl = None
  hasFile = True
  c = g.db.cursor()
  
  ##返回的数据data
  data = {}
  data["status"]=200
  data["data"] = {}

  sql = """select audioUrl from question where id = %d""" % question_id
  c.execute(sql)
  if c.fetchone()[0] != None:
    data["errmsg"] = "问题已回答"
    data["status"] = 500
  else:
    try:
      srcFile = request.files["audio"]
      audioSeconds = request.form.get('audioSeconds')
      print "audioSeconds", audioSeconds
    except:
      hasFile = False
    try:
      if hasFile == True:
        # 文件命名为question_id+后缀
        audioUrl = str(question_id) + os.path.splitext(srcFile.filename)[1]
        srcFile.save("static/audio/" + audioUrl)
        sql="""update question set audioUrl='%s', audioSeconds = '%s'
            where id=%d""" % (audioUrl, audioSeconds, question_id)
        c.execute(sql)
        g.db.commit()
    except Exception as e:
      data["errmsg"] = "录音上传失败"
      data["status"] = 500
  
  return jsonify(data)