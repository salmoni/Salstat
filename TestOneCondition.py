#!/usr/bin/env python

import time, os, os.path
import urllib, codecs
import urllib.parse as urlparse
import wx
import images
import sys, numpy
import AllRoutines


class TestsClass(wx.Panel):
    def __init__(self, parent, columnList):
        wx.Panel.__init__(self, parent, -1)
        helpWithin = "These tests help you compare values against a hypothetic mean value."
        t20 = wx.StaticText(self,-1,label=helpWithin,pos=(20,20))
        t20.Wrap(620)
        t21 = wx.StaticText(self,-1,"Select the test you want:",pos=(60,80))
        t22 = wx.StaticText(self,-1,"Select your variable:",pos=(320,80))
        t23 = wx.StaticText(self,-1,"Enter the user hypothesised mean here:",pos=(320,150))
        self.test1 = wx.CheckBox(self,-1,"One sample t-test",pos=(60,110))
        self.test2 = wx.CheckBox(self,-1,"One sample sign test",pos=(60,140))
        self.test3 = wx.CheckBox(self,-1,"Chi square for variance ration",pos=(60,170))
        self.IVBox = wx.Choice(self,211, (324,100), (160,20), columnList)
        self.UMean = wx.TextCtrl(self, -1, pos=(324,170), size=(80,-1))

class TestDialog(wx.Dialog):
    def __init__(self, columnList, testFlag = False):
        wx.Dialog.__init__(self, None, title="Correlations",\
                size=(700,425))
        self.testFlag = testFlag
        helpTop = "These tests allow you to see if a set of observations are different from a hypothetical mean. "
        t1 = wx.StaticText(self,-1, label=helpTop, pos=(20,30),size=(-1,660))
        t1.Wrap(660)
        self.decider = wx.Notebook(self, -1, pos=(20,65), size=(660,290))
        self.testSubs = TestsClass(self.decider, columnList)
        self.decider.InsertPage(0, self.testSubs,"One sample tests")
        okayButton = wx.Button(self,211,"Analyse",pos=(540,360),size=(125,-1))
        cancelButton = wx.Button(self,212,"Cancel",pos=(390,360),size=(125,-1))
        okayButton.SetDefault()
        self.Bind(wx.EVT_BUTTON, self.AnalyseButton, id=211)
        self.Bind(wx.EVT_BUTTON, self.CancelButton, id=212)

    def AnalyseButton(self, event):
        page = self.decider.GetSelection()
        self.results = {}
        tests = []
        self.results["testType"] = 'neither'
        if self.testSubs.test1.IsChecked():
            tests.append('ttestone') # ['ttestone','signtest','chivariance']
        if self.testSubs.test2.IsChecked():
            tests.append('signtest')
        if self.testSubs.test3.IsChecked():
            tests.append('chivariance')
        self.results["IV"] = []
        self.results["IV"] = self.testSubs.IVBox.GetSelection()
        self.results["tests"] = tests
        self.results['umean'] = self.testSubs.UMean.GetValue()
        self.Close()
        return self.results

    def CancelButton(self, event):
        self.Close()
        return None



#---------------------------------------------------------------------------
# main loop, just for testing
if __name__ == '__main__':
    cList = ['a','b','c']
    app = wx.App()
    frame = TestDialog(cList, testFlag=True)
    frame.Show(True)
    app.MainLoop()
