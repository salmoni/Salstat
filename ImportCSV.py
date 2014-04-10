"""
ImportCSV.py

A Python module to import all manner of CSV files. Produces a dialog 
in wxPython for users to specify things like delimiters and so on.

Requires a single parameter: the directory to start
Returns:

1. Name of imported file
2. Variable names (if any)
3. Data
OR
4. None (no file selected or error made import impossible)

(c) 2014 Alan James Salmoni

"""

from __future__ import unicode_literals
import os, os.path
import wx
from wx.stc import *
import wx.grid as gridlib

class GetFilename(object):
    def __init__(self, parent, startDir):
        dlg = wx.FileDialog(parent, message="Open a CSV file", defaultDir=startDir, \
                wildcard="CSV text (*.csv)|*.csv|Plain text (*.txt)|*.txt|\
                Data file (*.dat)|*.dat|Any file (*.*)|*.*")
        #dlg.SetIcon(ico)
        if dlg.ShowModal() == wx.ID_OK:
            #print "Selected ", dlg.GetPath()
            self.fileName = dlg.GetPath()
            if os.path.exists(self.fileName):
                self.fileName
            else:
                self.fileName = None
        else:
            self.fileName = None

class PanelDelimiter(wx.Panel):
    def __init__(self, parent, fileName):
        wx.Panel.__init__(self, parent, -1)
        help_text = "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis."
        self.box = wx.StaticBox(self, -1, "Select which delimiters:",pos=(10,60),\
                size=(540,125))
        t1 = wx.StaticText(self, -1, label=help_text, pos=(10,10))
        t1.Wrap(545)
        t2 = wx.StaticText(self.box,-1,"Preview of %s"%fileName, pos=(40,200))
        self.del_01 = wx.CheckBox(self.box, -1, " Tab", pos=(0,20))
        self.del_02 = wx.CheckBox(self.box, -1, " Comma", pos=(160,20))
        self.del_03 = wx.CheckBox(self.box, -1, " Space", pos=(320,20))
        self.del_04 = wx.CheckBox(self.box, -1, " Semicolon",pos=(0,45))
        self.del_05 = wx.CheckBox(self.box, -1, " Other:", pos=(160,45))
        self.del_06 = wx.CheckBox(self.box, -1, "Text delimiter:",pos=(0,80))
        self.edit_01 = wx.TextCtrl(self.box, -1, pos=(235,44), size=(30,-1))
        self.edit_02 = wx.TextCtrl(self.box, -1, pos=(125,79), size=(45,-1))

class PanelFixedWidth(wx.Panel):
    def __init__(self, parent, fileName):
        wx.Panel.__init__(self, parent, -1)
        help_text = "Fixed width files blah, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
        t1 = wx.StaticText(self, -1, label=help_text, pos=(10,10))
        t1.Wrap(545)

class ImportDialog(wx.Dialog):
    def __init__(self, startDir):
        wx.Dialog.__init__(self, None, title="Importing a CSV file",\
                size=(600,470))
        FileName = GetFilename(self, startDir)
        #print FileName.fileName
        fin = open(FileName.fileName, 'r')
        head = [fin.next() for x in xrange(12)]
        self.decider = wx.Notebook(self, -1, pos=(10,0), \
                size=(580,240), style=wx.NB_TOP)
        p1 = PanelDelimiter(self.decider, FileName.fileName)
        p2 = PanelFixedWidth(self.decider, FileName.fileName)
        self.decider.AddPage(p1, "Delimited files")
        self.decider.AddPage(p2, "Fixed width files")
        t1 = wx.StaticText(self,-1,label="Header row is:",pos=(30,250))
        t2 = wx.StaticText(self,-1,label="Import data from row:",pos=(300,250))
        self.headerRow = wx.SpinCtrl(self, -1, min=0,max=100, initial=0, \
                pos=(140,250),size=(70,-1))
        self.dataRow = wx.SpinCtrl(self,-1,min=1,max=100, initial=1, \
                pos=(460,250),size=(70,-1))
        self.buttonImport = wx.Button(self,-1,"Import", \
                pos=(500,400),size=(70,-1))
        self.buttonCancel = wx.Button(self,-1,"Cancel", \
                pos=(405,400),size=(70,-1))
        self.grid = gridlib.Grid(self, -1, size=(560,100),pos=(20,290))
        self.grid.HideRowLabels()
        self.grid.CreateGrid(8,8)
        self.grid.SetColLabelSize(16)
        for i in range(8):
            self.grid.SetRowSize(i,16)
        self.AttemptPreview(head)

    def AttemptPreview(self, head):
        pass


################################################
# Classes just for testing this module

class MyFrame(wx.Frame):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title="Example frame")

        # show a MessageDialog
        style = wx.OK|wx.ICON_INFORMATION
        # create panel
        #panel = MyPanel(self)


if __name__ == '__main__':
    startDir = os.path.expanduser("~")
    app = wx.App(False)
    frame = ImportDialog(startDir)
    frame.Show()
    app.MainLoop()

