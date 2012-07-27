#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''fuji3get
http://live-fuji.jp/calender/
画像は10分おきに公開されていて、一番映ってる時間が長いと思われる
夏至の日(6/21-23頃)でだいたい午前4:00頃から午後19:50頃まで撮影されています。
http://live-fuji.jp/calender/dayView.php?date=20120621
http://live-fuji.jp/calender/dayView.php?date=20120622
http://live-fuji.jp/calender/dayView.php?date=20120623
一枚づつのページはこちらで、
http://live-fuji.jp/calender/kobetuView.php?date=YYYYmmdd&h=HH&i=MM
画像だけの場合のURLはこちらです。
http://live-fuji.jp/hi-fuji/YYYYmmdd/HHMM.jpg

たとえば、開始日と終了日を指定して、
$ fuji3get.py 20110311 20120720
などと実行したいです。
'''

import sys, os, stat
import re
import time, datetime
import urllib2
import sl3conf

USER_AGENT = 'fuji3bot/Python-urllib'
VENDOR_NAME = u'fuji3get'
CONF_NAME = VENDOR_NAME
BASE_DIR = u'/var/cache/fuji3cache'
DIR_FUJI = u'%04d/%02d/%02d'
JPG_FUJI = u'%04d%02d%02d%02d%02d.jpg'
URL_FUJI = u'http://live-fuji.jp/hi-fuji/%04d%02d%02d/%02d%02d.jpg'
FMT_P = '%Y%m%d%H%M'
FMT_F = '%Y-%m-%d %H:%M'
YMDHM_MIN = '201101010000'

class Fuji3Get(object):
  def __init__(self):
    self.error_count = 0
    self.sl3conf = sl3conf.SL3Conf(VENDOR_NAME, CONF_NAME)
    self.cache_ask = self.sl3conf.read(u'cache_ask')
    if self.cache_ask is None:
      self.sl3conf.write(u'cache_ask', u'True')
      self.sl3conf.write(u'cache_dir', BASE_DIR)
      self.cache_ask = self.sl3conf.read(u'cache_ask')
    self.cache_dir = self.sl3conf.read(u'cache_dir')

  def chkjpeg(self, d, silent=True):
    if d[6:10] == 'JFIF': return True
    self.error_count += 1
    if not silent: print u'**** may not be a jpeg file ****'
    return False

  def getjpeg(self, ymdhm):
    dir = os.path.join(self.cache_dir, DIR_FUJI % ymdhm[:3])
    outf = JPG_FUJI % ymdhm
    outfile = os.path.join(dir, outf)
    url = URL_FUJI % ymdhm
    print u'get %s ->' % url,
    if os.path.exists(outfile):
      if os.stat(outfile)[stat.ST_SIZE] == 0:
        print u'not found, skipped'
        return
      tfp = open(outfile, 'rb')
      if tfp:
        jpg = self.chkjpeg(tfp.read(16), silent=False)
        tfp.close()
        if jpg:
          print u'exists, skipped'
          return
      os.remove(outfile)
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', USER_AGENT)]
    try:
      ifp = opener.open(url) # ifp = urllib2.urlopen(url)
      if ifp:
        print outf
        if not os.path.exists(dir): os.makedirs(dir)
        ofp = open(outfile, 'wb')
        if ofp:
          d = ifp.read()
          jpg = self.chkjpeg(d, silent=False)
          ofp.write(d)
          ofp.close()
          if not jpg: os.remove(outfile)
        ifp.close()
    except urllib2.HTTPError, e: # 404 Not Found, 403 Forbidden, 401 Auth, etc.
      print e # sys.exc_info()[0]
      delta = datetime.datetime.now() - datetime.datetime(*ymdhm)
      if delta > datetime.timedelta(2, 0):
        if not os.path.exists(dir): os.makedirs(dir)
        ofp = open(outfile, 'wb')
        if ofp: ofp.close()
    except urllib2.URLError, e: # time out, getaddrinfo failed, etc.
      print e # sys.exc_info()[0]
    # except httplib.BadStatusLine, e: # httplib.InvalidURL, ...

  def chkymdhm(self, ymdhmstr):
    r = re.compile('^\d{12}$', re.I)
    if not r.match(ymdhmstr): return None, 'must be a number of 12 digits'
    iymdhm = int(ymdhmstr)
    nowstr = datetime.datetime.strftime(datetime.datetime.now(), FMT_P)
    if iymdhm > int(nowstr):
      return None, 'must be less than or equal to %s' % nowstr
    if iymdhm < int(YMDHM_MIN):
      return None, 'must be greater than or equal to %s' % YMDHM_MIN
    month, day = int(ymdhmstr[4:6]), int(ymdhmstr[6:8])
    if month < 1 or month > 12: return None, 'month is out of range'
    if day < 1 or day > 31: return None, 'day is out of range'
    h, m = int(ymdhmstr[8:10]), int(ymdhmstr[10:12])
    if h < 0 or h > 23: return None, 'hour is out of range'
    if m < 0 or m > 59: return None, 'minute is out of range'
    try:
      res = datetime.datetime.strptime(ymdhmstr, FMT_P)
    except ValueError, e:
      return None, e # None, sys.exc_info()[0]
    return res, None

  def align600sec(self, ymdhm):
    m, s, u = ymdhm.minute % 10, ymdhm.second, ymdhm.microsecond
    return ymdhm - datetime.timedelta(minutes=m, seconds=s, microseconds=u)

  def fuji3get(self, sdt, edt):
    s = self.chkymdhm(sdt)
    if s[0] is None: return 'start %s' % s[1]
    e = self.chkymdhm(edt)
    if e[0] is None: return 'end %s' % e[1]
    if s[0] > e[0]: return 'start must be less than or equal to end'
    as, ae = self.align600sec(s[0]), self.align600sec(e[0])
    print u'duration: %s - %s' % (as, ae)
    self.error_count = 0
    ymdhm = as
    while ymdhm <= ae:
      self.getjpeg(datetime.datetime.timetuple(ymdhm)[:5])
      ymdhm += datetime.timedelta(seconds=600)
    print u'total errors: %d' % self.error_count
    return None

if __name__ == '__main__':
  if len(sys.argv) < 3:
    print u'Usage: %s start(YYYYmmddHHMM) end(YYYYmmddHHMM)' % (sys.argv[0])
  else:
    r = Fuji3Get().fuji3get(sys.argv[1], sys.argv[2])
    if r: print u'error: %s' % r
