"""
DescriptivesFrame.py

A wxPython dialog to allow users to select a range of descriptive
statistics and variables for analysis.

"""

import wx
import salstat_stats, AllRoutines

class DescribeObj(object):
    def __init__(self):
        pass

class DFrame(wx.Dialog):
    def __init__(self, parent, id, grid):
        wx.Dialog.__init__(self, parent, id, "Describe data", \
                size = (800,600),style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.grid = grid
        self.res = None
        self.SetMinSize((400,300))
        ico = wx.Icon('icons/PurpleIcon05_32.png',wx.BITMAP_TYPE_PNG)
        self.SetIcon(ico)
        sizerH01 = wx.BoxSizer(wx.HORIZONTAL)
        self.panel1 = wx.Panel(self)
        self.panel2 = wx.Panel(self)
        sizerL = wx.BoxSizer(wx.VERTICAL)
        sizerR = wx.BoxSizer(wx.VERTICAL)

        panelR03 = wx.Panel(self)
        self.tests = wx.Notebook(self)

        cancelButton = wx.Button(panelR03, 1341, "Cancel", pos=(20,0), size=(90,-1))
        okButton = wx.Button(panelR03, 1342, "Analyse", pos=(130,0), size=(90,-1))

        t1 = wx.StaticText(self, -1, "Describe these variables:")
        t2 = wx.StaticText(self, -1, "Grouped by these variables:")
        t3 = wx.StaticText(self, -1, " ")
        t4 = wx.StaticText(self, -1, "Select descriptive statistics:")

        self.GetVars()
        self.varListIV = wx.CheckListBox(self, -1, choices=self.vars)
        self.varListGRP = wx.CheckListBox(self, -1, choices=self.vars)

        testshort, testlong = self.GetTests()
        self.testListShort = wx.CheckListBox(self.tests, -1, choices=testshort)
        self.testListLong  = wx.CheckListBox(self.tests, -1, choices=testlong)
        self.tests.AddPage(self.testListShort, "Most used tests")
        self.tests.AddPage(self.testListLong, "All tests")

        bord = 10
        sizerL.Add(t1, 0, wx.ALL, border=bord)
        sizerL.Add(self.varListIV, 1, wx.EXPAND|wx.ALL)
        sizerL.Add(t2, 0, wx.ALL, border=bord)
        sizerL.Add(self.varListGRP, 1, wx.EXPAND|wx.ALL)
        sizerL.Add(t3, 0, wx.ALL, border=bord)

        sizerR.Add(t4, 0, wx.ALL, border=bord)
        sizerR.Add(self.tests, 1, wx.EXPAND|wx.ALL)
        sizerR.Add(panelR03, 0, wx.ALL|wx.ALIGN_RIGHT, border=bord)

        sizerH01.Add(sizerL, 1, wx.EXPAND|wx.ALL, border=bord)
        sizerH01.AddSpacer(0)
        sizerH01.Add(sizerR, 1, wx.EXPAND|wx.ALL, border=bord)
        
        self.SetAutoLayout(True)
        self.SetSizer(sizerH01)
        self.Layout()
        wx.EVT_BUTTON(self, 1341, self.CancelButton)
        wx.EVT_BUTTON(self, 1342, self.OkayButton)

    def CancelButton(self, event):
        self.res = "cancel"
        self.Close()

    def OkayButton(self, event):
        self.res = "ok"
        self.Close()

    def GetValues(self):
        IVs = self.varListIV.GetChecked()
        self.IVs = []
        for IV in IVs:
            self.IVs.append(self.ColNums[IV])
        self.GRPs = self.varListGRP.GetChecked()
        page = self.tests.GetSelection()
        if page == 0:
            self.stats = self.testListShort.GetCheckedStrings()
        elif page == 1:
            self.stats = self.testListLong.GetCheckedStrings()

    def GetVars(self):
        if self.grid:
            self.vars, self.ColNums = self.grid.GetUsedCols()
        else:
            self.vars = ["var 001", "var 002","var 003", "var 004"]
            self.ColNums = range(len(self.vars))

    def GetTests(self):
        testshort = AllRoutines.GetMostUsedTests()
        testlong  = AllRoutines.GetAllTests()
        return testshort, testlong

    def OnClose(self, event):
        self.Close()


if __name__ == '__main__':
    app = wx.App()
    frame = DFrame(None, -1, None)
    frame.Show(True)
    app.MainLoop()

