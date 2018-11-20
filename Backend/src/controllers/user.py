# -*- coding: utf-8 -*-
import os
import hashlib
import MySQLdb
import question
import functools
from flask import Blueprint, g, jsonify, request, session

user = Blueprint('user', __name__)

def check_session(fun):
  @functools.wraps(fun)
  def wrapper(*args, **kw):
    print("check session")
    if 'user_id' not in session:  # 未登录
      return jsonify({'status':403, 'errmsg':'未登录'})
    return fun(*args, **kw)
  return wrapper

def avatarMD5(avatar):
  MD5 = hashlib.md5()
  MD5.update(avatar)
  return MD5.hexdigest()

# 微信登录后完善信息
@user.route('/api/users/<int:user_id>/perfect', methods=['PATCH'])
# @check_session
def perfectInfo(user_id):
  school = request.form.get("school")
  major = request.form.get("major")
  grade = request.form.get("grade")
  status = "%s%s%s" % (school, major, grade)
  avatarUrl = "%d.jpg" % user_id
  hasFile = True
  avatarmd5 = ""
  try:
    srcFile = request.files["avatar"]
  except:
    hasFile = False
  if hasFile:
    # 文件命名为user_id+后缀
    avatarUrl = str(user_id) + os.path.splitext(srcFile.filename)[1]
    srcFile.save("static/avatar/" + avatarUrl)
    avatarmd5 = avatarMD5(open("static/avatar/" + avatarUrl, "rb").read())

  ##返回的数据data
  data = {}
  data["status"]=200
  data["data"] = {}
  try:
    sql = """update user set avatarUrl='%s',status='%s',
       school='%s',major='%s',grade='%s', isNew=0
       where id=%d""" % (avatarUrl,status,school,major,grade,user_id)
    c = g.db.cursor()
    c.execute(sql)
    g.db.commit()
    data["data"]["md5"] = avatarmd5
  except Exception as e:
    print e
    data["errmsg"] = "完善信息失败"
    data["status"] = 500

  return jsonify(data)

# 3.点击头像跳转到提问页面
@user.route('/api/users/<int:user_id>/introduction')
# @check_session
def introduction(user_id):
  # 我自己的id
  id = request.args.get("id")
  c = g.db.cursor() 
  
  data = {}
  data["status"] = 200
  data["data"] = {}

  sql = '''select u.avatarUrl, u.username, u.description, u.status 
     from user u where u.id = %d''' % user_id
  c.execute(sql)
  result = c.fetchone()
  data["data"]["avatarUrl"] = result[0]
  data["data"]["username"] = result[1]
  data["data"]["description"] = result[2]
  data["data"]["status"] = result[3]

  #关注信息
  sql = '''select f.uid from follow f where followed_uid = %d''' % user_id
  c.execute(sql)
  results = c.fetchall()
  data["data"]["followedNum"] = len(results)
  data["data"]["followed"] = 0
  for row in results:
    if (row[0] == int(id)):
      data["data"]["followed"] = 1
      break

  #回答问题数
  sql = '''select count(*)
        from question q
        where q.answerer_id = %d''' % user_id
  c.execute(sql)
  ansNum = c.fetchone()
  data["data"]["ansNum"] = ansNum[0]

  #回答的问题
  data["data"]["answers"] = []
  sql = '''select q.id, q.description, q.answerer_id, q.audioSeconds
          from question q
          where q.answerer_id = %d and q.audioSeconds is not null''' % user_id
  c.execute(sql)
  results = c.fetchall()
  for row in results:
    record = {'id':row[0], 'description':row[1], 'audioSeconds':row[3]}
    tmp = question._getSomeDetail(row[0], row[2])
    record.update(tmp)
    data["data"]["answers"].append(record)

  return jsonify(data)

# 7. 找人模块页面 follow
@user.route('/api/users/<int:user_id>/follows')
# @check_session
def follow(user_id):
  c = g.db.cursor() 
  data = {}
  data["status"]=200
  data["data"] = []
  
  try:
    sql='''select f.followed_uid from follow f where f.uid = %d''' % user_id
    c.execute(sql)
    results = c.fetchall()
    for row in results:
      id = row[0]
      #用户信息
      sql = '''select u.username, u.avatarUrl, u.description, u.status from user u
              where u.id = %d''' % id
      c.execute(sql)
      record = c.fetchone()
      data["data"].append({"id":id, "username":record[0],
        "avatarUrl":record[1],"description":record[2], "status":record[3]})
  except:
    del data['data']
    data["errmsg"] = "请求失败"
    data["status"] = 500

  return jsonify(data)

# 7.找人模块页面recommendations 暂时与关注的一样
@user.route('/api/users/<int:user_id>/recommendations')
# @check_session
def recommendation(user_id):
  c = g.db.cursor() 
  data = {}
  data["status"]=200
  data["data"] = []
  
  try:
    sql='''select f.followed_uid from follow f where f.uid = %d''' % user_id
    c.execute(sql)
    results = c.fetchall()
    for row in results:
      id = row[0]
      #用户信息
      sql = '''select u.username, u.avatarUrl, u.description, u.status from user u
              where u.id = %d''' % id
      c.execute(sql)
      record = c.fetchone()
      data["data"].append({"id":id, "username":record[0],
        "avatarUrl":record[1],"description":record[2], "status":record[3]})
  except:
    del data['data']
    data["errmsg"] = "请求失败"
    data["status"] = 500

  return jsonify(data)

#合并
@user.route('/api/users/<int:user_id>/followsAndRecommendations')
# @check_session
def foAndRe(user_id):
  c = g.db.cursor() 
  data = {}
  data["status"]=200
  data["data"] = []
  
  try:
    # 关注
    sql='''select f.followed_uid from follow f where f.uid = %d''' % user_id
    c.execute(sql)
    results = c.fetchall()
    for row in results:
      id = row[0]
      #用户信息
      sql = '''select u.username, u.avatarUrl, u.description, u.status from user u
              where u.id = %d''' % id
      c.execute(sql)
      record = c.fetchone()
      data["data"].append({"id":id, "username":record[0],
        "avatarUrl":record[1],"description":record[2],
        "status":record[3], "followed": 1})

    # 推荐(没关注的人)
    # 用户信息
    sql = '''select u.id, u.username, u.avatarUrl, u.description, u.status from user u'''
    c.execute(sql)
    alluser = c.fetchall()
    results = [row[0] for row in results] + [user_id]
    for record in alluser:
      id = record[0]
      if id not in results:
        data["data"].append({"id":id, "username":record[1],
        "avatarUrl":record[2],"description":record[3],
        "status":record[4], "followed": 0})

  except:
    del data['data']
    data["errmsg"] = "请求失败"
    data["status"] = 500

  return jsonify(data)

# 8.找人功能
@user.route('/api/users/find', methods=['GET'])
# @check_session
def find():
  session['user_id'] = 1
  query_string = request.args['query_string']
  user_id = int(session['user_id'])

  c = g.db.cursor() 
  sql="""select u.id, u.username, u.avatarUrl, u.description, u.status from user u
       where u.username like '%%%s%%' or u.status like '%%%s%%' or u.description like '%%%s%%' LIMIT 5""" % (query_string, query_string, query_string)

  data = {}
  data["status"] = 200
  data["data"] = []
  
  try:
    c.execute(sql)
    results = c.fetchall()
    for row in results:
      sql='''select f.uid from follow f where f.uid = %d and f.followed_uid = %d''' % (user_id, row[0])
      c.execute(sql)
      result = c.fetchone()
      if result != None:
        data["data"].append({"id":row[0],"username":row[1],"avatarUrl":row[2],"description":row[3], "status":row[4], "followed":1})
      else:
        data["data"].append({"id":row[0],"username":row[1],"avatarUrl":row[2],"description":row[3], "status":row[4], "followed":0})

  except:
    del data['data']
    data["errmsg"] = "搜索失败"
    data["status"] = 500

  return jsonify(data)

# 10. "我的"模块
@user.route('/api/users/<int:user_id>')
# @check_session
def aboutMe(user_id):
  c = g.db.cursor() 
  sql = """select u.username, u.avatarUrl, u.status, u.description, u.school, u.major, u.grade
        from user u where u.id=%d""" % user_id
  
  #返回的数据data
  data = {}
  data["status"]=200
  data["data"]={}
  
  try:
    c.execute(sql)
    result=c.fetchone()
    data['data']['id'] = user_id
    data["data"]["username"] = result[0]
    data["data"]["avatarUrl"] = result[1]
    data["data"]["status"] = result[2]
    data["data"]["description"] = result[3]
    data["data"]["school"] = result[4]
    data["data"]["major"] = result[5]
    data["data"]["grade"] = result[6]

    # 回答的问题
    data["data"]["answer"] = []
    sql1 = """select q.id, q.description, asker.username, asker.avatarUrl, q.audioUrl
          from question q,user asker
          where q.answerer_id=%d and q.asker_id=asker.id and q.audioUrl is not null """ % user_id
    c.execute(sql1)
    results = c.fetchall()
    for row in results:
      id = int(row[0])
      description = row[1]
      asker_username = row[2]
      asker_avatarUrl = row[3]
      audioUrl = row[4]
      finished = True if audioUrl != None else False
      data["data"]["answer"].append({"id":id, "description":description,
        "asker_username":asker_username, "asker_avatarUrl":asker_avatarUrl, "finished":finished})
    data["data"]["ansNum"] = len(results)

    # 提出的问题
    data["data"]["asked"] = []
    sql2 = """select q.id,q.description,q.answerer_id,q.audioUrl
        from question q where q.asker_id=%d""" % user_id
    c.execute(sql2)
    results = c.fetchall()
    for row in results:
      id = row[0]
      description = row[1]
      answerer_id = row[2]
      if answerer_id == None:
        data["data"]["asked"].append({"id":id, "description":description,
          "finished":False, "answerer_id":"",
          "answerer_username":"", "answerer_status":"",
          "answerer_description":"", "answerer_avatarUrl":""})
      else:
        audioUrl = row[3]
        sql3 = """select u.username,u.status,u.description,u.avatarUrl
              from user u where u.id=%d""" % answerer_id
        c.execute(sql3)
        result = c.fetchone()
        answerer_username = result[0]
        answerer_status = result[1]
        answerer_description = result[2]
        answerer_avatarUrl = result[3]
        data["data"]["asked"].append({"id":id, "description":description,
            "finished":False if audioUrl == None else True,"answerer_id":answerer_id,
            "answerer_username":answerer_username,"answerer_status":answerer_status,
            "answerer_description":answerer_description,"answerer_avatarUrl":answerer_avatarUrl})
    data["data"]["askNum"] = len(results)

    # 被关注数
    sql4="""select count(*) from follow f where f.followed_uid=%d""" % user_id
    c.execute(sql4)
    result = c.fetchone()
    data["data"]["followedNum"] = result[0]

  except:
    del data['data']
    data["errmsg"] = "获取信息失败"
    data["status"] = 500
    
  return jsonify(data)

# 11.修改信息
@user.route('/api/users/<int:user_id>', methods=['PATCH'])
# @check_session
def updateInfo(user_id):
  username = request.form.get("username")
  status = request.form.get("status")
  description = request.form.get("description")
  school = request.form.get("school")
  major = request.form.get("major")
  grade = request.form.get("grade")
  hasFile = True
  avatarmd5 = ""
  try:
    srcFile = request.files["avatar"]
  except Exception as e:
    hasFile = False
    print e
  
  # 文件命名为user_id+后缀
  avatarUrl = "%d.jpg" % user_id
  if hasFile:  
    srcFile.save("static/avatar/%s" % avatarUrl)
    avatarmd5 = avatarMD5(open("static/avatar/" + avatarUrl, "rb").read())
  else:
    print "no file"
  ##返回的数据data
  data = {}
  data["status"]=200
  data["data"] = {}
  try:
    sql = """update user set username='%s',avatarUrl='%s',status='%s',description='%s',
       school='%s',major='%s',grade='%s'
       where id=%d""" % (username,avatarUrl,status,description,school,major,grade,user_id)
    c = g.db.cursor()
    c.execute(sql)
    g.db.commit()
    data["data"]["md5"] = avatarmd5
  except Exception as e:
    print e
    data["errmsg"] = "更新失败"
    data["status"] = 500

  return jsonify(data)

# 13. 添加关注
@user.route('/api/users/<int:uid>/follows', methods=['POST'])
# @check_session
def addFollow(uid):
  followed_uid = int(request.form.get("followed_uid"))

  c = g.db.cursor() 
  data = {}
  data["status"] = 200

  sql = "select * from follow f where f.uid = %d and f.followed_uid = %d" % (uid, followed_uid)
  c.execute(sql)
  result = c.fetchone()
  if result != None:
    data["errmsg"] = "已关注"
    data["status"] = 500
  else:
    sql = "insert into follow values (%d, %d)" % (uid, followed_uid)
    try:
      c.execute(sql)
      g.db.commit()
    except Exception as e:
      print e
      data["errmsg"] = "关注失败"
      data["status"] = 500

  return jsonify(data)

# 14. 取消关注
@user.route('/api/users/<int:uid>/follows', methods=['DELETE'])
# @check_session
def deleteFollow(uid):
  followed_uid = int(request.args.get("followed_uid"))
  c = g.db.cursor() 
  data = {}
  data["status"] = 200

  sql = "select * from follow f where f.uid = %d and f.followed_uid = %d" % (uid, followed_uid)
  c.execute(sql)
  result = c.fetchone()
  if result != None:
    sql = "delete from follow where uid = %d and followed_uid = %d" % (uid, followed_uid)
    c.execute(sql)
    g.db.commit()
  else:
    data["errmsg"] = "未关注"
    data["status"] = 500

  return jsonify(data)
