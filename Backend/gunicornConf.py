# *-* coding: utf-8 *-*
import gevent.monkey
import multiprocessing

reload = True         # 修改代码时自动重启gunicorn
bind = "0.0.0.0:2334" # 绑定ip和端口
gevent.monkey.patch_all()
workers = multiprocessing.cpu_count() * 2
worker_class = "gevent"
keepalive = 5
threads = multiprocessing.cpu_count() * 2
backlog = 2048
proc_name = 'gunicorn.proc'
pidfile = '/tmp/gunicorn.pid'
debug = True
loglevel = 'debug'
