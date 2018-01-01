"""
ImportExcel.py
A Python module to read Excel files into Salstat. Does not include xlsx format
(at least, not just yet)
"""

from __future__ import unicode_literals
import os, os.path
import wx, wx.aui
import wx.grid as gridlib


################################################
# Custom grid class for previewing data

class Grid(gridlib.Grid):
    def __init__(self, parent, pos):
        gridlib.Grid.__init__(self, parent, size=(560,200), pos=(0,0))

    def ResizeGrid(self, nCols, nRows, spare=10):
        # check that data is saved before clearing!
        self.ClearGrid()
        # resize grid to accommodate data
        actual_cols = self.GetNumberCols()
        num_cols_to_append = nCols + spare
        self.DeleteCols(pos=0, numCols=actual_cols)
        self.AppendCols(numCols=num_cols_to_append)
        actual_rows = self.GetNumberRows()
        num_rows_to_append = nRows + spare
        self.DeleteRows(pos=0, numRows=actual_rows)
        self.AppendRows(numRows=num_rows_to_append)


def GetFileSizes(filename):
    try:
        workbook = open_workbook(filename)
    except: # what error?
        pass # seriously, what?
    nsheets = workbook.nsheets
    sheet_names = workbook.sheet_names()
    for idx_sheet in range(nsheets):
        sheet = workbook.sheet_by_index(idx_sheet)

def GetCells(workbook, sheet_number):
    worksheet = workbook.sheet_by_index(sheet_number)
    nrows = worksheet.nrows
    ncols = worksheet.ncols
    # resize grid to accomodate data size
    for idx_row in range(nrows):
        for idx_col in range(ncols):
            val = worksheet.cell(idx_row, idx_col)
            # set cell of grid to 'val'

################################################
# Panel for database

class PanelDB(wx.Panel):
    def __init__(self, parent, fileName, pos, size):
        wx.Panel.__init__(self, parent, -1, pos=pos, size=size)
        self.parent = parent
        help_text = "Salstat can retrieve data from relational databases. "
        t1 = wx.StaticText(self, -1, label=help_text, pos=(10,10))
        t1.Wrap(545)

################################################
# Main class that binds it all together

class ImportDialog(wx.Dialog):
    def __init__(self, FileName):
        wx.Dialog.__init__(self, None, title="Import from a database",\
                size=(600,380))
        self.FileName = FileName
        self.excel = ['.xls','.xlsx']
        self.loo   = ['.ods']
        extension = os.path.splitext(self.FileName.fileName)[1]
        if extension.lower() in self.excel:
            self.ftype = "excel"
        elif extension.lower() in self.loo:
            self.ftype = "libre"
        else:
            self.ftype = None
        if not self.ftype:
            self.CancelButton(None)
        help_text = "Salstat can load files from Excel and LibreOffice/OpenOffice. "
        t1 = wx.StaticText(self, -1, label=help_text, pos=(20,10))
        t1.Wrap(545)
        t2 = wx.StaticText(self,-1,label="Import from row:",pos=(20,50))
        self.headerRow = wx.CheckBox(self, 760, " Header on first row", \
                pos=(210,50))
        self.dataRow = wx.SpinCtrl(self,766,min=1,max=100, initial=1, \
                pos=(140,49),size=(50,-1))
        self.dataRow.SetValue(1)
        self.buttonImport = wx.Button(self,763,"Import", \
                pos=(500,310),size=(70,-1))
        self.buttonImport.SetDefault()
        self.buttonCancel = wx.Button(self,764,"Cancel", \
                pos=(405,310),size=(70,-1))
        self.worksheets = wx.aui.AuiNotebook(self, -1, pos=(20,90), \
                size=(560,210),style=wx.NB_TOP|wx.aui.AUI_NB_WINDOWLIST_BUTTON)
        self.MaxRows = 100
        self.MaxCols = 40
        self.gridFont = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL)
        if self.ftype == "excel":
            self.workbook = xlrd.open_workbook(self.FileName.fileName)
            sheets = self.workbook.sheets()
        elif self.ftype == "libre":
            self.workbook = ezodf.opendoc(self.FileName.fileName)
            sheets = self.workbook.sheets
        self.grids = []
        for idx, sheet in enumerate(sheets):
            self.grids.append(Grid(self.worksheets, -1))
            self.grids[idx].HideRowLabels()
            self.grids[idx].SetColLabelSize(16)
            self.grids[idx].SetRowLabelSize(40)
            self.grids[idx].SetDefaultColSize(60)
            self.grids[idx].CreateGrid(self.MaxRows,self.MaxCols)
            for i in range(self.MaxCols):
                self.grids[idx].SetColLabelValue(i, " ")
            for i in range(self.MaxRows):
                self.grids[idx].SetRowSize(i,16)
            self.grids[idx].SetDefaultCellFont(self.gridFont)
            self.worksheets.AddPage(self.grids[idx],sheet.name)
            if self.ftype == 'excel':
                nrows = sheet.nrows
                ncols = sheet.ncols
            elif self.ftype == 'libre':
                nrows = sheet.nrows()
                ncols = sheet.ncols()
            self.grids[idx].ResizeGrid(ncols, nrows)
            for idx_row in range(nrows):
                for idx_col in range(ncols):
                    if self.ftype == 'excel':
                        val = sheet.cell(idx_row, idx_col).value
                    elif self.ftype == 'libre':
                        val = sheet[idx_row, idx_col].value
                    self.grids[idx].SetCellValue(idx_row, idx_col, str(val))
        # It seems odd but it seems better for all events to be routed to the same method
        self.Bind(wx.EVT_CHECKBOX, self.AdjustGrid, id=760)
        self.Bind(wx.EVT_SPINCTRL, self.AdjustGrid, id=766)
        self.Bind(wx.EVT_BUTTON, self.CancelButton, id=764)
        self.Bind(wx.EVT_BUTTON, self.ImportButton, id=763)



