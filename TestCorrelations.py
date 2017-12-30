#!/usr/bin/env python

import time, os, os.path
import urllib, codecs
import urllib.parse as urlparse
import wx
import images
import sys, numpy
import AllRoutines


class CorrelationsClass(wx.Panel):
    def __init__(self, parent, columnList):
        wx.Panel.__init__(self, parent, -1)
        helpWithin = "Correlations are for finding out the association between two variables."
        t20 = wx.StaticText(self,-1,label=helpWithin,pos=(20,20))
        t20.Wrap(620)
        t21 = wx.StaticText(self,-1,"Select the test you want:",pos=(60,80))
        t22 = wx.StaticText(self,-1,"Select your variables:",pos=(320,80))
        self.test1 = wx.CheckBox(self,-1,"Pearson's correlation",pos=(60,110))
        self.test2 = wx.CheckBox(self,-1,"Spearman's correlation",pos=(60,140))
        self.test3 = wx.CheckBox(self,-1,"Kendall's Tau correlation",pos=(60,170))
        self.test4 = wx.CheckBox(self,-1,"Point biserial R",pos=(60,200))
        self.DVBox = wx.CheckListBox(self,-1,pos=(320,100),size=(300,120),choices=columnList)

class TestDialog(wx.Dialog):
    def __init__(self, columnList, testFlag = False):
        wx.Dialog.__init__(self, None, title="Correlations",\
                size=(700,425))
        self.testFlag = testFlag
        helpTop = "These tests allow you to measure the association between 2 variables. "
        t1 = wx.StaticText(self,-1, label=helpTop, pos=(20,30),size=(-1,660))
        t1.Wrap(660)
        self.decider = wx.Notebook(self, -1, pos=(20,65), size=(660,290))
        self.correlationSubs = CorrelationsClass(self.decider, columnList)
        self.decider.InsertPage(0, self.correlationSubs,"Correlations")
        okayButton = wx.Button(self,211,"Analyse",pos=(540,360),size=(125,-1))
        cancelButton = wx.Button(self,212,"Cancel",pos=(390,360),size=(125,-1))
        okayButton.SetDefault()
        self.Bind(wx.EVT_BUTTON, self.AnalyseButton, id=211)
        self.Bind(wx.EVT_BUTTON, self.CancelButton, id=212)

    def AnalyseButton(self, event):
        page = self.decider.GetSelection()
        self.results = {}
        tests = []
        self.results["testType"] = 'between'
        if self.correlationSubs.test1.IsChecked():
            tests.append('pearsons')
        if self.correlationSubs.test2.IsChecked():
            tests.append('spearmans')
        if self.correlationSubs.test3.IsChecked():
            tests.append('kendalls')
        if self.correlationSubs.test4.IsChecked():
            tests.append('pointbr')
        self.results["IV"] = []
        self.results["DV"] = self.correlationSubs.DVBox.GetChecked()
        self.results["tests"] = tests
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
