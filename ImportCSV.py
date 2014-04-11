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
import os, os.path, csv, sys, shlex
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
        self.parent = parent
        help_text = "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis."
        self.box = wx.StaticBox(self, -1, "Select which delimiters:",pos=(10,60),\
                size=(540,125))
        t1 = wx.StaticText(self, -1, label=help_text, pos=(10,10))
        t1.Wrap(545)
        t2 = wx.StaticText(self.box,-1,"Preview of %s"%fileName, pos=(40,200))
        self.del_01 = wx.CheckBox(self.box, 760, " Tab", pos=(0,20))
        self.del_02 = wx.CheckBox(self.box, 760, " Comma", pos=(160,20))
        self.del_03 = wx.CheckBox(self.box, 760, " Space", pos=(320,20))
        self.del_04 = wx.CheckBox(self.box, 760, " Semicolon",pos=(0,45))
        self.del_05 = wx.CheckBox(self.box, 760, " Other:", pos=(160,45))
        self.del_06 = wx.CheckBox(self.box, 760, "Text delimiter:",pos=(0,80))
        self.edit_01 = wx.TextCtrl(self.box, 761, pos=(235,44), size=(30,-1))
        self.edit_02 = wx.TextCtrl(self.box, 762, pos=(125,79), size=(45,-1))

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
        self.FileName = GetFilename(self, startDir)
        #self.allFont = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL)
        #print FileName.fileName
        #fin = open(FileName.fileName, 'r')
        #head = [fin.next() for x in xrange(12)]
        self.decider = wx.Notebook(self, -1, pos=(10,0), \
                size=(580,240), style=wx.NB_TOP)
        self.p1 = PanelDelimiter(self.decider, self.FileName.fileName)
        self.p2 = PanelFixedWidth(self.decider, self.FileName.fileName)
        self.decider.AddPage(self.p1, "Delimited files")
        self.decider.AddPage(self.p2, "Fixed width files")
        t1 = wx.StaticText(self,-1,label="Header row:",pos=(250,250))
        t2 = wx.StaticText(self,-1,label="Import from row:",pos=(410,250))
        self.headerRow = wx.SpinCtrl(self, -1, min=0,max=100, initial=0, \
                pos=(340,250),size=(50,-1))
        self.dataRow = wx.SpinCtrl(self,-1,min=1,max=100, initial=1, \
                pos=(530,250),size=(50,-1))
        self.buttonImport = wx.Button(self,763,"Import", \
                pos=(500,400),size=(70,-1))
        self.buttonCancel = wx.Button(self,764,"Cancel", \
                pos=(405,400),size=(70,-1))
        self.grid = gridlib.Grid(self, -1, size=(560,100),pos=(20,290))
        self.grid.HideRowLabels()
        self.grid.CreateGrid(8,8)
        self.grid.SetColLabelSize(16)
        for i in range(8):
            self.grid.SetRowSize(i,16)
        self.gridFont = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL)
        self.grid.SetDefaultCellFont(self.gridFont)
        lineEndChoices = ['Not sure','\\n (Unix)','\\r\\n (Windows)','\\r (old Mac)']
        t3 = wx.StaticText(self,-1,"Line ending:",pos=(20,250))
        self.lineEnd = wx.Choice(self, 765,pos=(110,248),size=(120,-1),\
                choices = lineEndChoices)
        self.AttemptPreview()
        wx.EVT_CHECKBOX(self, 760, self.AttemptPreview)
        wx.EVT_TEXT(self, 761, self.AttemptPreview)
        wx.EVT_BUTTON(self, 764, self.CancelButton)
        wx.EVT_BUTTON(self, 763, self.ImportButton)
        wx.EVT_CHOICE(self, 765, self.AttemptPreview)

    def AttemptPreview(self, event=None):
        # set up CSV format
        delim = b','
        quote = b'"'
        if self.p1.del_01.IsChecked():
            delim = b'\t'
        if self.p1.del_02.IsChecked():
            delim = b','
        if self.p1.del_03.IsChecked():
            delim = b' '
        if self.p1.del_04.IsChecked():
            delim = b';'
        val = self.p1.edit_01.GetValue()
        if val != "":
            delim = b'%s'%val
            delim = delim[0]
            print delim,len(delim)
        #csv.register_dialect('CSV_import',delimiter=delim)
        data = []
        """
        with open(self.FileName.fileName,'rb') as fin:
            reader = csv.reader(fin, delimiter=delim, quotechar=quote)
            for row in reader:
                data.append(row)
        fin.close()
        """
        fin = open(self.FileName.fileName,'r')
        data = fin.read()
        fin.close()
        self.FillGrid2(data)

    def FillGrid2(self, data):
        self.grid.ClearGrid()
        # work out most common line end
        endSelect = self.lineEnd.GetSelection()
        lineTerm = '\n'
        if endSelect == 0:
            lineEnds = ['\n','\r\n','\r']
            maxes = []
            for lineEnd in lineEnds:
                maxes.append(self.GetMax(data, lineEnd))
            lineTerm = lineEnds[lineEnds.index(max(lineEnds))-1]
        elif endSelect == 1:
            lineTerm = '\n'
        elif endSelect == 2:
            lineTerm = '\r\n'
        elif endSelect == 3:
            lineTerm = '\r'
        data = data.split(lineTerm)
        # get delimiters
        delims = ''
        if self.p1.del_01.IsChecked():
            delims += b'\t'
        if self.p1.del_02.IsChecked():
            delims += b','
        if self.p1.del_03.IsChecked():
            delims += b' '
        if self.p1.del_04.IsChecked():
            delims += b';'
        # split each row
        for row in range(8):
            try:
                line = data[row]
                tokens = self.ParseLine(line, delims, '"')
                k = len(tokens)
                if k > 8:
                    k = 8
                for idxy in range(k):
                    self.grid.SetCellValue(row,idxy,tokens[idxy])
            except IndexError:
                break
        
    def ParseLine(self, line, delims, quotes):
        """
        Parses a line of text into components
        """
        inQuote = False
        try:
            inQuoteChar = quotes[0]
        except IndexError:
            inQuoteChar = ''
        token = ''
        tokens = []
        n = len(line)
        for idx in range(n):
            char = line[idx]
            if char in quotes:
                if inQuote:
                    if char == inQuoteChar:
                        pass
                    else:
                        token += char
                else:
                    inQuote = True
                    inQuoteChar = char
            else:
                if char in delims:
                    if len(token) > 0:
                        tokens.append(token)
                        token = ''
                    else:
                        pass
                else:
                    #print char
                    token += char
        if len(token) > 0:
            tokens.append(token)
        return tokens

    def GetMax(self, data, lineEnd):
        return len(data.split(lineEnd))

    def FillGrid(self, data):
        self.grid.ClearGrid()
        for idxx, row in enumerate(data):
            k = len(row)
            if k > 8:
                k = 8
            for idxy in range(k):
                self.grid.SetCellValue(idxx,idxy,row[idxy])

    def CancelButton(self, event):
        self.Close()
        sys.exit() # delete this!

    def ImportButton(self, event):
        self.Close()
        sys.exit() # delete this!


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

