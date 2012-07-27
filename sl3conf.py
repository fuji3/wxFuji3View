#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''sl3conf
create table の方で unique(k, s) 指定しておけば
create unique index を作らなくても sqlite_autoindex_env_1 が自動で作られる
'''

import sys, os
import time, datetime
import sqlite3

class SL3Conf(object):
  def __init__(self, vendor_name, conf_name=None):
    self.vendor_name = vendor_name
    self.conf_name = vendor_name if conf_name is None else conf_name
    self.sl3fn = self.get_conf_file()
    if not os.path.exists(self.sl3fn): self.init_conf()

  def get_conf_dir(self):
    userdir = os.path.expanduser('~')
    if not os.path.isdir(userdir): os.mkdir(userdir)
    vendordir = os.path.join(userdir, u'.%s' % self.vendor_name)
    if not os.path.isdir(vendordir): os.mkdir(vendordir)
    return vendordir

  def get_conf_file(self):
    return os.path.join(self.get_conf_dir(), u'%s.sl3' % self.conf_name)

  def init_conf(self):
    cn = sqlite3.connect(self.sl3fn)
    cn.execute(u'create table env (id integer primary key autoincrement,' \
      + u' k varchar(255), v varchar(4096), s varchar(255), o integer,' \
      + u' cdate integer, edate integer, unique(k, s));')
    # cn.execute(u'create unique index env_k_s on env(k, s);')
    cn.execute(u'create index env_o on env(o);')
    cn.commit()
    cn.close()

  def write(self, k, val, sect=u''):
    v = self.read(k, sect)
    cn = sqlite3.connect(self.sl3fn)
    dt = datetime.datetime.now()
    ts = int(time.mktime(datetime.datetime.timetuple(dt))) * 1000000
    ts += dt.microsecond
    if v is None:
      cn.execute(u'insert into env (k, v, s, o, cdate, edate) values' \
        + u" ('%s', '%s', '%s', 0, %d, %d);" % (k, val, sect, ts, ts))
    else:
      cn.execute(u"update env set v='%s',edate=%d where k='%s' and s='%s';" \
        % (val, ts, k, sect))
    cn.commit()
    cn.close()

  def read(self, k, sect=u''):
    v = None
    cn = sqlite3.connect(self.sl3fn)
    cur = cn.cursor()
    cur.execute(u"select k,v,s from env where k='%s' and s='%s' order by o;" \
      % (k, sect))
    for row in cur:
      v = row[1]
      break
    cn.close()
    return v

if __name__ == '__main__':
  conf = SL3Conf(u'fuji3get')
  if conf.read(u'cache_ask') is None:
    conf.write(u'cache_ask', u'True')
    conf.write(u'cache_dir', u'/var/cache/fuji3cache')
    conf.write(u'testfield', u'日本語')
  print u'cache_ask: %s' % conf.read(u'cache_ask')
  print u'cache_dir: %s' % conf.read(u'cache_dir')
  print u'testfield: %s' % conf.read(u'testfield')
