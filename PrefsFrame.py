"""
PrefsFrame.py

A wxPython dialog to allow users to set preferences.

"""
import os
from os.path import expanduser
import wx


class ReturnVals(object):
    def __init__(self, NumRows, NumCols, CellHeight, CellWidth, WorkingDir, font):
        self.NumRows = NumRows
        self.NumCols = NumCols
        self.CellHeight = CellHeight
        self.CellWidth = CellWidth
        self.workingdir = WorkingDir
        self.font = font

class PFrame(wx.Dialog):
    def __init__(self, parent, id, grid, initdir=None):
        wx.Dialog.__init__(self, parent, id, "Preferences", \
                size = (600,400),style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        if not grid:
            pass
        self.res = None
        if initdir:
            self.workingdir = initdir
        else:
            self.workingdir = expanduser("~")
        self.tabs = wx.Notebook(self, -1, pos=(20,20), size=(560,300))
        self.panel_gen = wx.Panel(self.tabs, -1)
        self.panel_grid = wx.Panel(self.tabs, -1)
        self.panel_out = wx.Panel(self.tabs, -1)
        self.tabs.AddPage(self.panel_gen, "General")
        self.tabs.AddPage(self.panel_grid, "Data grid")
        self.tabs.AddPage(self.panel_out, "Output")
        self.gridfont = grid.GetDefaultCellFont()
        self.fontObj = wx.FontData()
        self.fontObj.EnableEffects(True)
        self.fontObj.SetColour(grid.GetDefaultCellTextColour())
        self.fontObj.SetInitialFont(self.gridfont)
        # outfont = output.get the font!
        wx.StaticText(self.panel_gen, -1, "Working directory:", pos=(20,30))
        wx.StaticText(self.panel_grid, -1, "Number of columns:", pos=(20,30))
        wx.StaticText(self.panel_grid, -1, "Number of rows:", pos=(20,60))
        wx.StaticText(self.panel_grid, -1, "Cell width:", pos=(300,30))
        wx.StaticText(self.panel_grid, -1, "Cell height:", pos=(300,60))
        wx.StaticText(self.panel_grid, -1, "Font face:", pos=(20,110))
        wx.StaticText(self.panel_grid, -1, "Size:", pos=(380,110))
        wx.StaticText(self.panel_out, -1, "Font face:", pos=(20,30))
        wx.StaticText(self.panel_out, -1, "Size:", pos=(380,30))
        self.numcols = wx.TextCtrl(self.panel_grid, -1, pos=(160,30), \
                size=(60,21),value=str(grid.GetNumberCols()))
        self.numrows = wx.TextCtrl(self.panel_grid, -1, pos=(160,60), \
                size=(60,21),value=str(grid.GetNumberRows()))
        self.cellwidth = wx.TextCtrl(self.panel_grid, -1, pos=(400,30), \
                size=(60,21),value=str(grid.GetDefaultColSize()))
        self.cellheight = wx.TextCtrl(self.panel_grid, -1, pos=(400,60),\
                size=(60,21),value=str(grid.GetDefaultRowSize()))
        self.directory = wx.TextCtrl(self.panel_gen, -1, pos=(160,30),size=(260,21))
        #self.font_sizeO = wx.TextCtrl(self.panel_out, -1, pos=(430,30),size=(30,21))
        #self.font_faceG = wx.TextCtrl(self.panel_grid, -1, pos=(160,110),size=(200,21))
        #self.font_sizeG = wx.TextCtrl(self.panel_grid, -1, pos=(430,110),size=(30,21))
        fontstring = "%s - %s points"%(self.gridfont.GetFaceName(), self.gridfont.GetPointSize())
        self.font_display = wx.StaticText(self.panel_grid, -1, fontstring,pos=(160,110))
        self.font_display.SetFont(self.gridfont)
        self.font_faceO = wx.TextCtrl(self.panel_out, -1, pos=(160,30),size=(200,21))
        self.font_sizeO = wx.TextCtrl(self.panel_out, -1, pos=(430,30),size=(30,21))

        button_cancel = wx.Button(self, 2296, "Cancel", size=(120,21), pos=(310,339))
        button_okay = wx.Button(self, 2297, "OK", size=(120,21), pos=(450,339))
        button_dir = wx.Button(self.panel_gen, 2298, "...",size=(60,21), pos=(420,26))
        button_font = wx.Button(self.panel_grid, 2299, "Set font",size=(120,21), pos=(360,110))
        if initdir == None:
            initdir = os.getcwd()
        self.directory.SetValue(initdir)
        self.Bind(wx.EVT_BUTTON, self.Cancel, id=2296)
        self.Bind(wx.EVT_BUTTON, self.Okay, id=2297)
        self.Bind(wx.EVT_BUTTON, self.GetDirectory, id=2298)
        self.Bind(wx.EVT_BUTTON, self.GetFont, id=2299)

    def GetFont(self, event):
        print ("here?")
        dlg = wx.FontDialog(self, self.fontObj)
        if dlg.ShowModal() == wx.ID_OK:
            font = dlg.GetFontData()
            self.font = font.GetChosenFont()
            fontstring = "%s - %s points"%(font.GetChosenFont().GetFaceName(), \
                    font.GetChosenFont().GetPointSize())
            self.font_display.SetLabel(fontstring)

    def GetValues(self):
        NumRows = int(self.numrows.GetValue())
        NumCols = int(self.numcols.GetValue())
        CellHeight = int(self.cellheight.GetValue())
        CellWidth = int(self.cellwidth.GetValue())
        try:
            font = self.font
        except:
            font = None
        self.Vals = ReturnVals(NumRows, NumCols, CellHeight, CellWidth, self.workingdir, font)

    def GetDirectory(self, event):
        dlg = wx.DirDialog(self, "Choose a directory", \
                defaultPath=self.workingdir, \
                style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.workingdir = dlg.GetPath()
            self.directory.SetValue(self.workingdir)

    def Okay(self, event):
        self.GetValues()
        self.res = "ok"
        self.Close()

    def Cancel(self, event):
        self.Close()

if __name__ == '__main__':
    app = wx.App()
    frame = PFrame(None, -1, None)
    PWin = frame.Show()
    app.MainLoop()
