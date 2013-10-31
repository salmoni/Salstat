"""
GridObject

Customises the Salstat grid somewhat by allowing meta-data to be associated with each column.
(c) 2013 Alan James Salmoni
"""

import wx
import wx.grid 

ID_FILE_NEW = wx.NewId()
ID_FILE_NEWOUTPUT = wx.NewId()
ID_FILE_OPEN = wx.NewId()
ID_FILE_SAVE = wx.NewId()
ID_FILE_SAVEAS = wx.NewId()
ID_FILE_PRINT = wx.NewId()
ID_FILE_EXIT = wx.NewId()
ID_EDIT_CUT = wx.NewId()
ID_EDIT_COPY = wx.NewId()
ID_EDIT_PASTE = wx.NewId()
ID_EDIT_SELECTALL = wx.NewId()
ID_EDIT_FIND = wx.NewId()
ID_EDIT_DELETECOL = wx.NewId()
ID_EDIT_DELETEROW = wx.NewId()
ID_PREF_VARIABLES = wx.NewId()
ID_PREF_GRID = wx.NewId()
ID_PREF_CELLS = wx.NewId()
ID_PREF_FONTS = wx.NewId()
ID_EDIT_INSERTCOL = wx.NewId()
ID_EDIT_INSERTROW = wx.NewId()
ID_EDIT_APPENDCOL = wx.NewId()
ID_EDIT_APPENDROW = wx.NewId()


class ColumnObject(object):
    def __init__(self):
        self.name = None
        self.missingvalues = None
        self.measure = None
        self.align = "left"
        self.type = None

class Grid(wx.grid.Grid):
    def __init__(self, parent, ID, num_cols = 40, num_rows = 100):
        wx.grid.Grid.__init__(self, parent)
        self.CreateGrid(num_cols, num_rows)
        self.meta = []
        for i in range(num_cols):
            colObj = ColumnObject()
            colObj.name = self.GetColLabelValue(i)
            self.meta.append(colObj)

    def AnyChange(self):
        num_cols = self.GetGridCursorCol()
        for idx in range(num_cols):
            self.SetColLabelValue(idx, self.meta[idx].name)

    def CutData(self, event):
        print len(self.meta)

    def CopyData(self, event):
        pass

    def PasteData(self, event):
        pass

    def SelectAllCells(self, event):
        pass

    def GoFindDialog(self, event):
        pass

    def insert_cols(self, num_cols, position = None):
        try:
            num_cols = int(num_cols)
            if position == None:
                position = self.GetGridCursorCol()
            res = self.InsertCols(position, num_cols, updateLabels=False)
            if res:
                for idx in range(num_cols):
                    obj = ColumnObject()
                    obj.name = "Unnamed"
                    self.meta.insert(position+idx, obj)
            self.AnyChange()
        except:
            pass

    def append_cols(self, num_cols):
        pass

    def delete_cols(self, num_cols, position = None):
        pass

    def delete_rows(self, num_rows, position = None):
        pass

    def insert_rows(self, num_rows, position = None):
        pass

    def append_rows(self, num_rows):
        pass

    def remake_grid(self, num_cols = 40, num_rows = 100):
        pass

    def resize_grid(self, num_cols, num_rows):
        pass

class DataFrame(wx.Frame):
    def __init__(self, parent, ID):
        wx.Frame.__init__(self,parent,-1)

        menuBar = wx.MenuBar()
        file_menu = wx.Menu()
        edit_menu = wx.Menu()
        prefs_menu = wx.Menu()
        describe_menu = wx.Menu()
        analyse_menu = wx.Menu()
        preparation_menu = wx.Menu()
        chart_menu = wx.Menu()
        help_menu = wx.Menu()
        edit_menu.Append(ID_EDIT_CUT, 'Cu&t\tCTRL+X')
        edit_menu.Append(ID_EDIT_COPY, '&Copy\tCTRL+C')
        edit_menu.Append(ID_EDIT_PASTE, '&Paste\tCTRL+V')
        edit_menu.Append(ID_EDIT_SELECTALL, 'Select &All\tCTRL+A')
        edit_menu.Append(ID_EDIT_FIND, '&Find and Replace...\tCTRL+F')
        edit_menu.AppendSeparator()
        edit_menu.Append(ID_EDIT_DELETECOL, 'Delete Current Column')
        edit_menu.Append(ID_EDIT_DELETEROW, 'Delete Current Row')
        edit_menu.AppendSeparator()
        edit_menu.Append(ID_EDIT_INSERTCOL, 'Insert columns...')
        edit_menu.Append(ID_EDIT_INSERTROW, 'Insert rows...')
        edit_menu.Append(ID_EDIT_APPENDCOL, 'Append columns...')
        edit_menu.Append(ID_EDIT_APPENDROW, 'Append rows...')
        menuBar.Append(file_menu, '&File')
        menuBar.Append(edit_menu, '&Edit')
        menuBar.Append(prefs_menu, '&Preferences')
        menuBar.Append(analyse_menu, '&Analyse')
        self.SetMenuBar(menuBar)

        self.grid = Grid(self, -1)
        self.grid.SetDefaultColSize(60, True)
        self.grid.SetRowLabelSize(40)

        wx.EVT_MENU(self, ID_EDIT_CUT, self.grid.CutData)
        wx.EVT_MENU(self, ID_EDIT_COPY, self.grid.CopyData)
        wx.EVT_MENU(self, ID_EDIT_PASTE, self.grid.PasteData)
        wx.EVT_MENU(self, ID_EDIT_SELECTALL, self.grid.SelectAllCells)
        wx.EVT_MENU(self, ID_EDIT_FIND, self.grid.GoFindDialog)
        wx.EVT_MENU(self, ID_EDIT_DELETECOL, self.grid.delete_cols)
        wx.EVT_MENU(self, ID_EDIT_DELETEROW, self.grid.delete_rows)
        wx.EVT_MENU(self, ID_EDIT_INSERTCOL, self.InsertCols)
        wx.EVT_MENU(self, ID_EDIT_INSERTROW, self.InsertRows)
        wx.EVT_MENU(self, ID_EDIT_APPENDCOL, self.AppendCols)
        wx.EVT_MENU(self, ID_EDIT_APPENDROW, self.AppendRows)

    def InsertCols(self, event):
        dlg = wx.TextEntryDialog(self, "Enter columns")
        if dlg.ShowModal() == wx.ID_OK:
            num_cols = dlg.GetValue()
            self.grid.insert_cols(num_cols)

    def InsertRows(self, event):
        pass

    def AppendCols(self, event):
        pass

    def AppendRows(self, event):
        pass


if __name__ == '__main__':
    app = wx.App()
    frame = DataFrame(None, -1)
    #frame.grid.SetFocus()
    frame.Show(True)
    app.MainLoop()


