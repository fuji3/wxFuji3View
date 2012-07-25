#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''sl3conf
'''

import sys, os
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
    cn.execute(u'create table env (id integer primary key autoincrement,' + \
      'k varchar(4096), v varchar(4096));')
    cn.commit()
    cn.close()

  def write(self, k, val):
    v = self.read(k)
    cn = sqlite3.connect(self.sl3fn)
    if v is None:
      cn.execute(u'''insert into env (k, v) values ('%s', '%s');''' % (k, val))
    else:
      cn.execute(u'''update env set v='%s' where k='%s';''' % (val, k))
    cn.commit()
    cn.close()

  def read(self, k):
    v = None
    cn = sqlite3.connect(self.sl3fn)
    cur = cn.cursor()
    cur.execute(u'''select k, v from env where k='%s';''' % k)
    for row in cur:
      v = row[1]
      break
    cn.close()
    return v

if __name__ == '__main__':
  conf = SL3Conf(u'fuji3get')
  conf.write('cache_dir', 'TEST')
  print u'cache_ask: %s' % conf.read('cache_ask')
  print u'cache_dir: %s' % conf.read('cache_dir')
