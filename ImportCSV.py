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

class ImportDialog(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, title="Importing a CSV file",\
                size=(600,350))
        FileName = GetFilename(self, startDir)
        #print FileName.fileName
        fin = open(FileName.fileName, 'r')
        head = [fin.next() for x in xrange(12)]
        

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
    frame = ImportDialog()
    frame.Show()
    app.MainLoop()

