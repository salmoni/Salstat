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
        self.alphaValNeeded = False
        self.SetMinSize((400,300))
        ico = wx.Icon('icons/PurpleIcon05_32.png',wx.BITMAP_TYPE_PNG)
        self.SetIcon(ico)
        sizerH01 = wx.BoxSizer(wx.HORIZONTAL)
        self.panel1 = wx.Panel(self)
        self.panel2 = wx.Panel(self)
        sizerL = wx.BoxSizer(wx.VERTICAL)
        sizerR = wx.BoxSizer(wx.VERTICAL)

        panelR03 = wx.Panel(self, size=(-1, 30))
        self.tests = wx.Notebook(self)
        panelR02 = wx.Panel(self, size=(-1, 30))

        cancelButton = wx.Button(panelR03, 1341, "Cancel", pos=(20,0), size=(90,-1))
        okButton = wx.Button(panelR03, 1342, "Analyse", pos=(130,0), size=(90,-1))
        okButton.SetDefault()

        wx.StaticText(panelR02, -1, "Alpha value:", pos=(0,-1))
        self.alphaText = wx.TextCtrl(panelR02, -1, pos=(120,0), size=(40,-1))
        self.alphaText.Disable()

        t1 = wx.StaticText(self, -1, "Describe these variables:")
        t2 = wx.StaticText(self, -1, "Grouped by these variables:")
        t3 = wx.StaticText(self, -1, " ")
        t4 = wx.StaticText(self, -1, "Select descriptive statistics:")

        self.GetVars()
        self.varListDV = wx.CheckListBox(self, -1, choices=self.vars)
        self.varListGRP = wx.CheckListBox(self, -1, choices=self.vars)

        testshort, testlong = self.GetTests()
        self.testListShort = wx.CheckListBox(self.tests, 1343, choices=testshort)
        self.testListLong  = wx.CheckListBox(self.tests, 1344, choices=testlong)
        self.tests.AddPage(self.testListShort, "Most used tests")
        self.tests.AddPage(self.testListLong, "All tests")

        bord = 10
        sizerL.Add(t1, 0, wx.ALL, border=bord)
        sizerL.Add(self.varListDV, 1, wx.EXPAND|wx.ALL)
        sizerL.Add(t2, 0, wx.ALL, border=bord)
        sizerL.Add(self.varListGRP, 1, wx.EXPAND|wx.ALL)
        sizerL.Add(t3, 0, wx.ALL, border=bord)

        sizerR.Add(t4, 0, wx.ALL, border=bord)
        sizerR.Add(self.tests, 1, wx.EXPAND|wx.ALL)
        sizerR.Add(panelR02, 0, wx.ALL|wx.ALIGN_LEFT, border=bord)
        sizerR.Add(panelR03, 0, wx.ALL|wx.ALIGN_RIGHT, border=bord)

        sizerH01.Add(sizerL, 1, wx.EXPAND|wx.ALL, border=bord)
        sizerH01.AddSpacer(0)
        sizerH01.Add(sizerR, 1, wx.EXPAND|wx.ALL, border=bord)
        
        self.SetAutoLayout(True)
        self.SetSizer(sizerH01)
        self.Layout()
        wx.EVT_BUTTON(self, 1341, self.CancelButton)
        wx.EVT_BUTTON(self, 1342, self.OkayButton)
        wx.EVT_CHECKLISTBOX(self, 1343, self.CheckChecked)
        wx.EVT_CHECKLISTBOX(self, 1344, self.CheckChecked)

    def CheckChecked(self, event):
        page = self.tests.GetSelection()
        if page == 0:
            stats = self.testListShort.GetCheckedStrings()
        elif page == 1:
            stats = self.testListLong.GetCheckedStrings()
        alphaFlag = False
        for stat in stats:
            if stat in self.alphaTests:
                self.alphaText.Enable()
                self.alphaValNeeded = True
                alphaFlag = True
        if not alphaFlag:
            self.alphaText.Disable()
            self.alphaValNeeded = False

    def CancelButton(self, event):
        self.res = "cancel"
        self.alpha = None
        self.Close()

    def OkayButton(self, event):
        self.res = "ok"
        alpha_val = self.alphaText.GetValue()
        if self.CanClose():
            self.Close()

    def GetValues(self):
        DVs = self.varListDV.GetChecked()
        self.DVs = []
        for DV in DVs:
            self.DVs.append(self.ColNums[DV])
        self.GRPs = self.varListGRP.GetChecked()
        page = self.tests.GetSelection()
        if page == 0:
            self.stats = self.testListShort.GetCheckedStrings()
        elif page == 1:
            self.stats = self.testListLong.GetCheckedStrings()

    def CanClose(self):
        self.alpha = None
        if self.alphaValNeeded:
            try:
                self.alpha = float(self.alphaText.GetValue())
                if (self.alpha > 0.0) and (self.alpha < 1.0):
                    return True
                else:
                    return False
            except ValueError:
                return False
        else:
            return True

    def GetVars(self):
        if self.grid:
            self.vars, self.ColNums = self.grid.GetUsedCols()
        else:
            self.vars = ["var 001", "var 002","var 003", "var 004"]
            self.ColNums = range(len(self.vars))

    def GetTests(self):
        testshort = AllRoutines.GetMostUsedTests()
        testlong  = AllRoutines.GetAllTests()
        self.alphaTests = AllRoutines.GetExtraTests()
        return testshort, testlong

    def OnClose(self, event):
        self.Close()


if __name__ == '__main__':
    app = wx.App()
    frame = DFrame(None, -1, None)
    frame.ShowModal()
    print frame.alpha
    app.MainLoop()

