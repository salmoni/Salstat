"""
PrefsFrame.py

A wxPython dialog to allow users to set preferences.

"""
import os
import wx


class PFrame(wx.Dialog):
    def __init__(self, parent, id, grid, initdir=None):
        wx.Dialog.__init__(self, parent, id, "Preferences", \
                size = (600,400),style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.tabs = wx.Notebook(self, -1, pos=(20,20), size=(560,300))
        self.panel_gen = wx.Panel(self.tabs, -1)
        self.panel_grid = wx.Panel(self.tabs, -1)
        self.panel_out = wx.Panel(self.tabs, -1)
        self.tabs.AddPage(self.panel_gen, "General")
        self.tabs.AddPage(self.panel_grid, "Data grid")
        self.tabs.AddPage(self.panel_out, "Output")
        wx.StaticText(self.panel_gen, -1, "Working directory:", pos=(20,30))
        wx.StaticText(self.panel_grid, -1, "Number of columns:", pos=(20,30))
        wx.StaticText(self.panel_grid, -1, "Number of rows:", pos=(20,60))
        wx.StaticText(self.panel_grid, -1, "Cell width:", pos=(300,30))
        wx.StaticText(self.panel_grid, -1, "Cell height:", pos=(300,60))
        wx.StaticText(self.panel_grid, -1, "Font face:", pos=(20,110))
        wx.StaticText(self.panel_grid, -1, "Size:", pos=(380,110))
        wx.StaticText(self.panel_out, -1, "Font face:", pos=(20,30))
        wx.StaticText(self.panel_out, -1, "Size:", pos=(380,30))
        self.numcols = wx.TextCtrl(self.panel_grid, -1, pos=(160,30), size=(60,21))
        self.numrows = wx.TextCtrl(self.panel_grid, -1, pos=(160,60), size=(60,21))
        self.cellwidth = wx.TextCtrl(self.panel_grid, -1, pos=(400,30), size=(60,21))
        self.cellheight = wx.TextCtrl(self.panel_grid, -1, pos=(400,60), size=(60,21))
        self.directory = wx.TextCtrl(self.panel_gen, -1, pos=(160,30),size=(260,21))
        #self.font_sizeO = wx.TextCtrl(self.panel_out, -1, pos=(430,30),size=(30,21))
        self.font_faceG = wx.TextCtrl(self.panel_grid, -1, pos=(160,110),size=(200,21))
        self.font_sizeG = wx.TextCtrl(self.panel_grid, -1, pos=(430,110),size=(30,21))
        self.font_faceO = wx.TextCtrl(self.panel_out, -1, pos=(160,30),size=(200,21))
        self.font_sizeO = wx.TextCtrl(self.panel_out, -1, pos=(430,30),size=(30,21))
        button_dir = wx.Button(self.panel_gen, 2298, "...",size=(60,21), pos=(420,26))
        button_cancel = wx.Button(self, 2296, "Cancel", size=(120,21), pos=(310,339))
        button_okay = wx.Button(self, 2297, "OK", size=(120,21), pos=(450,339))
        if initdir == None:
            initdir = os.getcwd()
        self.directory.SetValue(initdir)
        wx.EVT_BUTTON(self, 2296, self.Cancel)
        wx.EVT_BUTTON(self, 2297, self.Okay)

    def GetValues(self):
        self.NumRows = self.numrows.GetValue()
        self.NumCols = self.numcols.GetValue()
        self.CellHeight = self.cellheight.GetValue()
        self.CellWidth = self.cellwidth.GetValue()
        self.workingdir = self.directory.GetValue()

    def Okay(self, event):
        self.GetValues()
        self.Close()

    def Cancel(self, event):
        self.Destroy()

if __name__ == '__main__':
    app = wx.App()
    frame = PFrame(None, -1, None)
    frame.Show(True)
    app.MainLoop()

