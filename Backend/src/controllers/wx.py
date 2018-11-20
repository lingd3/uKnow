# -*- coding: utf-8 -*-
import requests
import hashlib
import functools
from uuid import uuid4
from flask import Blueprint, session, g, jsonify, request
requests.packages.urllib3.disable_warnings()

wx = Blueprint('wx', __name__)

def check_session(fun):
  @functools.wraps(fun)
  def wrapper(*args, **kw):
    print("check session")
    if 'user_id' in session:  # 已登录
      try:
        user_id = session['user_id']
        c = g.db.cursor()
        sql = "select u.isNew, u.token from user u where u.id = %d" % user_id
        c.execute(sql)
        result = c.fetchone()
        session['user_id'] = user_id
        return jsonify({'status':200, 'data':{'user_id':session['user_id'], 'isNew':result[0], 'token':result[1]}})
      except Exception as e:
        return jsonify({'status':500, 'errmsg':'请求失败'})
    return fun(*args, **kw)
  return wrapper

def avatarMD5(avatar):
  MD5 = hashlib.md5()
  MD5.update(avatar)
  return MD5.hexdigest()

@wx.route('/api/wxlogin', methods = ['POST'])
# @check_session
def wxlogin():
  avatarmd5 = ""
  try:
    if "user_id" in session:
      logout()

    c = g.db.cursor()
    appid = request.form.get("appid")
    code = request.form.get("code")
    AppSecret = 'e6de1f862f58500eab65974335e93e7c'
    res = requests.get('https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code' % (appid, AppSecret, code)).json()
    openid = res['openid']
    access_token = res['access_token']

    sql = """select u.id, u.isNew, u.token from user u where u.openid = '%s'""" % openid
    c.execute(sql)
    result = c.fetchone()

    if result == None:
      res = requests.get('https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s' % (access_token, openid)).json()
      nickname = res['nickname'].encode('iso-8859-1')
      headimgurl = res['headimgurl']
      sql = """insert into user (username, avatarUrl, status, description, school, major, grade, openid, token)
               values ('%s', 'default.jpg', 'status', '', 'sysu', 'ss', 'one', '%s', '%s')""" % (nickname, openid, uuid4().hex)
      c.execute(sql)
      sql = """select u.id, u.isNew, u.token from user u where u.openid = '%s'""" % openid
      c.execute(sql)
      result = c.fetchone()
      avatarUrl = '%d.jpg' % result[0]
      avatar = requests.get(headimgurl).content
      open('static/avatar/%s' % avatarUrl, 'wb').write(avatar)
      sql = """update user set avatarUrl='%s' where id=%d""" % (avatarUrl, result[0])
      c.execute(sql)
      g.db.commit()
      avatarmd5 = avatarMD5(open("static/avatar/" + avatarUrl, "rb").read())
            
    session['user_id'] = result[0]
    return jsonify({'status':200, 'data':{'user_id':result[0], 'isNew':result[1], 'token':result[2], "md5":avatarmd5}})

  except Exception as e:
    print e
    return jsonify({'status':500, 'errmsg':'登录失败'})

@wx.route('/api/tklogin', methods = ['POST'])
# @check_session
def tklogin():
  if "user_id" in session:
    logout()

  c = g.db.cursor()
  token = request.form.get("token", '')
  sql = """select u.id, u.isNew from user u where u.token = '%s'""" % token
  c.execute(sql)
  result = c.fetchone()
  if result == None:
    return jsonify({'status':500, 'errmsg':'登录失败'})
  else:
    session['user_id'] = result[0]
    return jsonify({'status':200, 'data':{'user_id':result[0], 'isNew':result[1]}})

@wx.route('/api/logout', methods = ['POST'])
def logout():
  try:
    session.pop('user_id')
  except Exception as e:
    return jsonify({'status':500, 'data':{}})
  return jsonify({'status':200, 'data':{}})