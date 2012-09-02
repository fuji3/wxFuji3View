#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''wxFuji3View
python Mt. Fuji Viewer (1920 x 1080) (192 x 108) (384 x 216)
get jpeg files from http://live-fuji.jp/calender/
'''

import sys, os, stat
import time, datetime
import wx
import wx.calendar
import KnobCtrl

from fuji3get import Fuji3Get, DIR_FUJI, JPG_FUJI, URL_FUJI
from fuji3get import FMT_P, FMT_F, YMDHM_MIN

APP_TITLE = u'wxFuji3View'
IMGW, IMGH = 384, 216
FRMW, FRMH = 392, 832

class MyFrame(wx.Frame):
  def __init__(self, *args, **kwargs):
    super(MyFrame, self).__init__(title=APP_TITLE,
      pos=(240, 120), size=(FRMW, FRMH), *args, **kwargs)
    self.fuji3get = Fuji3Get()
    self.hlc = wx.Colour(208, 208, 255)
    self.bgc = wx.Colour(255, 255, 255)
    self.SetBackgroundColour(self.bgc)
    self.emp = wx.EmptyBitmap(IMGW, IMGH)
    p, s, a = wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE
    szv = wx.BoxSizer(wx.VERTICAL)
    self.prev = wx.StaticBitmap(self, wx.NewId(), self.emp)
    szv.Add(self.prev, 1, wx.EXPAND)
    self.curr = wx.StaticBitmap(self, wx.NewId(), self.emp)
    szv.Add(self.curr, 1, wx.EXPAND)
    self.next = wx.StaticBitmap(self, wx.NewId(), self.emp)
    szv.Add(self.next, 1, wx.EXPAND)
    pnv1 = wx.Panel(self, wx.NewId())
    szv1h = wx.BoxSizer(wx.HORIZONTAL)
    self.holidays = [(1, 1), (2, 3), (4, 29), (12, 23)]
    self.cal = wx.calendar.CalendarCtrl(pnv1, wx.NewId(),
      wx.DateTime_Now(), pos=(0, 0),
      style=wx.calendar.CAL_SHOW_HOLIDAYS | wx.calendar.CAL_SUNDAY_FIRST \
        | wx.calendar.CAL_SHOW_SURROUNDING_WEEKS \
        | wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION)
    szv1h.Add(self.cal, 3, wx.EXPAND)
    self.knob = KnobCtrl.KnobCtrl(pnv1, wx.NewId(), size=(64, 64))
    self.knob.SetKnobRadius(6)
    self.knob.SetAngularRange(-60, 240)
    self.knob.SetTags(xrange(11))
    self.knob.SetValue(50)
    self.knob.SetTagsColour(wx.Colour(64, 64, 255))
    self.knob.SetBoundingColour(wx.Colour(255, 255, 255))
    self.knob.SetFirstGradientColour(wx.Colour(192, 192, 255))
    self.knob.SetSecondGradientColour(wx.Colour(32, 32, 255))
    szv1h.Add(self.knob, 1, wx.EXPAND)
    pnv1h1 = wx.Panel(pnv1, wx.NewId())
    szv1h1v = wx.BoxSizer(wx.VERTICAL)
    self.ffffup = wx.StaticText(pnv1h1, wx.NewId(), u'↑↑week↑↑', p, s, a)
    szv1h1v.Add(self.ffffup, 0, wx.EXPAND)
    self.fffup = wx.StaticText(pnv1h1, wx.NewId(), u'↑↑day↑↑', p, s, a)
    szv1h1v.Add(self.fffup, 0, wx.EXPAND)
    self.ffup = wx.StaticText(pnv1h1, wx.NewId(), u'↑4hours↑', p, s, a)
    szv1h1v.Add(self.ffup, 0, wx.EXPAND)
    self.fup = wx.StaticText(pnv1h1, wx.NewId(), u'↑1hour↑', p, s, a)
    szv1h1v.Add(self.fup, 0, wx.EXPAND)
    self.up = wx.StaticText(pnv1h1, wx.NewId(), u'↑up↑', p, s, a)
    szv1h1v.Add(self.up, 0, wx.EXPAND)
    self.pause = wx.StaticText(pnv1h1, wx.NewId(), u'pause', p, s, a)
    szv1h1v.Add(self.pause, 0, wx.EXPAND)
    self.down = wx.StaticText(pnv1h1, wx.NewId(), u'↓down↓', p, s, a)
    szv1h1v.Add(self.down, 0, wx.EXPAND)
    self.fdown = wx.StaticText(pnv1h1, wx.NewId(), u'↓1hour↓', p, s, a)
    szv1h1v.Add(self.fdown, 0, wx.EXPAND)
    self.ffdown = wx.StaticText(pnv1h1, wx.NewId(), u'↓4hours↓', p, s, a)
    szv1h1v.Add(self.ffdown, 0, wx.EXPAND)
    self.fffdown = wx.StaticText(pnv1h1, wx.NewId(), u'↓↓day↓↓', p, s, a)
    szv1h1v.Add(self.fffdown, 0, wx.EXPAND)
    self.ffffdown = wx.StaticText(pnv1h1, wx.NewId(), u'↓↓week↓↓', p, s, a)
    szv1h1v.Add(self.ffffdown, 0, wx.EXPAND)
    pnv1h1.SetSizer(szv1h1v)
    szv1h.Add(pnv1h1, 1, wx.EXPAND)
    pnv1.SetSizer(szv1h)
    szv.Add(pnv1, 0, wx.EXPAND)
    self.SetSizer(szv)
    self.outofrange = False
    self.direc, self.po = -1, self.down # must change self.po sync self.direc
    self.po.SetBackgroundColour(self.hlc)
    self.knob.SetValue(self.direc + 50)
    self.ymdhm_min = datetime.datetime.strptime(YMDHM_MIN, FMT_P)
    self.ymdhm = self.fuji3get.align600sec(datetime.datetime.now())
    self.pymdhm = self.ymdhm
    # self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
    # self.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEnterWindow)
    # self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeaveWindow)
    # self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvents)
    self.ffffup.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEvents)
    self.fffup.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEvents)
    self.ffup.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEvents)
    self.fup.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEvents)
    self.up.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEvents)
    self.pause.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEvents)
    self.down.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEvents)
    self.fdown.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEvents)
    self.ffdown.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEvents)
    self.fffdown.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEvents)
    self.ffffdown.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEvents)
    self.Bind(wx.calendar.EVT_CALENDAR, self.OnCalSelected, self.cal)
    self.Bind(wx.calendar.EVT_CALENDAR_MONTH, self.OnChangeMonth, self.cal)
    self.Bind(KnobCtrl.KC_EVENT_ANGLE_CHANGED, self.OnAngleChanged, self.knob)
    self.intimer = False
    self.timer = wx.Timer(self, wx.NewId())
    self.Bind(wx.EVT_TIMER, self.OnTimer)
    self.timer.Start(20)

  def OnMouseEvents(self, ev):
    if ev.Entering(): print u'enter',
    if ev.Leaving(): print u'leave', # EVT_LEAVE_WINDOW or EVT_MOUSE_EVENTS
    o = ev.GetEventObject()
    if o == self.po: return
    self.po.SetBackgroundColour(self.bgc) # o.GetBackgroundColour()
    self.po.Refresh()
    self.po = o
    o.SetBackgroundColour(self.hlc)
    o.Refresh()
    if o == self.pause: s, self.direc = u'   pause', 0
    elif o == self.ffffup: s, self.direc = u'  ffffup', 6 * 24 * 7
    elif o == self.fffup: s, self.direc = u'   fffup', 6 * 24
    elif o == self.ffup: s, self.direc = u'    ffup', 6 * 4
    elif o == self.fup: s, self.direc = u'     fup', 6
    elif o == self.up: s, self.direc = u'      up', 1
    elif o == self.down: s, self.direc = u'    down', -1
    elif o == self.fdown: s, self.direc = u'   fdown', -6
    elif o == self.ffdown: s, self.direc = u'  ffdown', -6 * 4
    elif o == self.fffdown: s, self.direc = u' fffdown', -6 * 24
    elif o == self.ffffdown: s, self.direc = u'ffffdown', -6 * 24 * 7
    print s

  def OnCalSelected(self, ev):
    print u'CalSelected %s' % ev.GetValue()

  def OnChangeMonth(self, ev):
    print u'ChangeMonth %s' % ev.GetValue()

  def OnAngleChanged(self, ev):
    print u'AngleChanged %s' % ev.GetValue()

  def OnTimer(self, ev):
    if self.intimer: return
    self.intimer = True
    if self.direc > 0:
      dsec = (600 * self.direc) if self.ymdhm.hour < 20 else (3600 * 8)
    elif self.direc < 0:
      dsec = (600 * self.direc) if self.ymdhm.hour > 3 else (-3600 * 8)
    else: # == 0 pause
      dsec = 0
    ymdhm = self.ymdhm + datetime.timedelta(0, dsec)
    if ymdhm >= self.ymdhm_min and ymdhm <= datetime.datetime.now():
      self.outofrange, self.ymdhm = False, ymdhm
    else:
      if not self.outofrange:
        print u'%s out of range' % datetime.datetime.strftime(ymdhm, FMT_F)
      self.outofrange = True
    if self.ymdhm != self.pymdhm:
      print datetime.datetime.strftime(self.ymdhm, FMT_F)
      self.pymdhm = self.ymdhm
      self.RefreshBmp()
    self.intimer = False

  def BmpImgFile(self, dsec):
    ymdhm = self.ymdhm + datetime.timedelta(0, dsec)
    t = datetime.datetime.timetuple(ymdhm)[:5]
    f = os.path.join(self.fuji3get.cache_dir, DIR_FUJI % t[:3], JPG_FUJI % t)
    if not os.path.exists(f): self.fuji3get.getjpeg(t)
    if not os.path.exists(f): return self.emp
    if os.stat(f)[stat.ST_SIZE] == 0: return self.emp
    tfp = open(f, 'rb')
    if tfp:
      jpg = self.fuji3get.chkjpeg(tfp.read(16))
      tfp.close()
      if not jpg: # Image file is not of type 17.
        os.remove(f)
        return self.emp
    try:
      im = wx.Image(f, wx.BITMAP_TYPE_JPEG).Scale(IMGW, IMGH)
    except wx._core.PyAssertionError, e:
      return self.emp # wxImage::Scale(): invalid image
    return wx.BitmapFromImage(im)

  def RefreshBmp(self):
    self.prev.SetBitmap(self.BmpImgFile(-600))
    self.curr.SetBitmap(self.BmpImgFile(0))
    self.next.SetBitmap(self.BmpImgFile(600))

if __name__ == '__main__':
  app = wx.App(False)
  frm = MyFrame(None, wx.NewId())
  app.SetTopWindow(frm)
  frm.Show()
  app.MainLoop()
