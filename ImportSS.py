"""
ImportExcel.py
A Python module to read Excel files into Salstat. Does not include xlsx format
(at least, not just yet)
"""

from __future__ import unicode_literals
import os, os.path 
import wx, wx.aui, xlrd
import wx.grid as gridlib
from xlrd import open_workbook
from xlwt import Workbook
import ezodf


################################################
# Save in xlsx format

def SaveToExcel(filename, grid):
    book = Workbook()
    book = Workbook(encoding='utf-8')
    datasheet = book.add_sheet('Data')
    metasheet = book.add_sheet('Meta')
    metasheet.write(0,0,"Name")
    metasheet.write(1,0,"Alignment")
    metasheet.write(2,0,"Label")
    metasheet.write(3,0,"Measure")
    metasheet.write(4,0,"Variable type")
    metasheet.write(5,0,"Decimal places")
    metasheet.write(6,0,"Missing values")
    numcols = grid.GetNumberCols()
    numrows = grid.GetNumberRows()
    for idxx in range(numcols):
        for idxy in range(numrows):
            val = grid.GetCellValue(idxy, idxx)
            datasheet.write(idxy + 1, idxx, val)
        label = grid.GetColLabelValue(idxx)
        meta = grid.meta[label]
        datasheet.write(0, idxx, meta['name'])
        metasheet.write(0, idxx + 1, meta['name'])
        metasheet.write(1, idxx + 1, meta['align'])
        metasheet.write(2, idxx + 1, meta['label'])
        metasheet.write(3, idxx + 1, meta['measure'])
        metasheet.write(4, idxx + 1, meta['ivdv'])
        metasheet.write(5, idxx + 1, meta['decplaces'])
        metasheet.write(6, idxx + 1, meta['missingvalues'])
    book.save(filename)    

################################################
# Save in xlsx format

def SaveToLibre(filename, grid):
    numcols = grid.GetNumberCols()
    numrows = grid.GetNumberRows()
    book = ezodf.newdoc(doctype="ods", filename=filename)
    book.sheets += ezodf.Sheet('Data', size=(numrows + 10, numcols + 10))
    book.sheets += ezodf.Sheet('Meta', size=(20, numcols + 10))
    datasheet = book.sheets['Data']
    metasheet = book.sheets['Meta']
    metasheet[(0,0)].set_value("Name")
    metasheet[(1,0)].set_value("Alignment")
    metasheet[(2,0)].set_value("Label")
    metasheet[(3,0)].set_value("Measure")
    metasheet[(4,0)].set_value("Variable type")
    metasheet[(5,0)].set_value("Decimal places")
    metasheet[(6,0)].set_value("Missing values")
    for idxx in range(numcols):
        for idxy in range(numrows):
            val = grid.GetCellValue(idxy, idxx)
            datasheet[(idxy + 1, idxx)].set_value(val)
        label = grid.GetColLabelValue(idxx)
        meta = grid.meta[label]
        datasheet[(0, idxx)].set_value(meta['name'])
        metasheet[(0, idxx + 1)].set_value(meta['name'])
        metasheet[(1, idxx + 1)].set_value(meta['align'])
        metasheet[(2, idxx + 1)].set_value(meta['label'])
        metasheet[(3, idxx + 1)].set_value(meta['measure'])
        metasheet[(4, idxx + 1)].set_value(meta['ivdv'])
        metasheet[(5, idxx + 1)].set_value(meta[str('decplaces')])
        metasheet[(6, idxx + 1)].set_value(meta['missingvalues'])
    book.save()
    

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
# Dialog to retrieve file name. Needed before we can do anything

class GetFilename(object):
    def __init__(self, parent, startDir):
        dlg = wx.FileDialog(parent, message="Open a spreadsheet file", defaultDir=startDir, \
                wildcard="Excel (newer) (*.xlsx)|*.xlsx|Excel (older) (*.xls)|*.xls|\
                LibreOffice Calc (*.ods)|*.ods")
        ico = wx.Icon('icons/PurpleIcon05_32.png',wx.BITMAP_TYPE_PNG)
        dlg.SetIcon(ico)
        if dlg.ShowModal() == wx.ID_OK:
            self.fileName = dlg.GetPath()
            if os.path.exists(self.fileName):
                self.fileName
            else:
                self.fileName = None
        else:
            self.fileName = None

################################################
# Panel for spreadsheets

class PanelSpreadsheet(wx.Panel):
    def __init__(self, parent, fileName, pos, size):
        wx.Panel.__init__(self, parent, -1, pos=pos, size=size)
        self.parent = parent
        help_text = "Salstat can load files from Excel and LibreOffice/OpenOffice Calc. "
        t1 = wx.StaticText(self, -1, label=help_text, pos=(10,10))
        t1.Wrap(545)

################################################
# Main class that binds it all together

class ImportDialog(wx.Dialog):
    def __init__(self, FileName):
        wx.Dialog.__init__(self, None, title="Importing a spreadsheet file",\
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
                        val = unicode(sheet.cell(idx_row, idx_col).value)
                    elif self.ftype == 'libre':
                        val = unicode(sheet[idx_row, idx_col].value)
                    self.grids[idx].SetCellValue(idx_row, idx_col, val)
        # It seems odd but it seems better for all events to be routed to the same method
        wx.EVT_CHECKBOX(self, 760, self.AdjustGrid)
        wx.EVT_SPINCTRL(self, 766, self.AdjustGrid)
        wx.EVT_BUTTON(self, 764, self.CancelButton)
        wx.EVT_BUTTON(self, 763, self.ImportButton)

    def AttemptPreview(self, event=None):
        beginRow = self.dataRow.GetValue()
        if self.headerRow.IsChecked():
            pass

    def CancelButton(self, event):
        # let's get out!
        self.FileName.fileName = None
        self.Close()

    def AdjustGrid(self, event):
        if self.ftype == "excel":
            sheets = self.workbook.sheets()
        elif self.ftype == "libre":
            sheets = self.workbook.sheets
        sheetIdx = self.worksheets.GetSelection()
        sheet = sheets[sheetIdx]
        self.grids[sheetIdx].ClearGrid()
        # beginData = # get row where data begins
        if self.ftype == 'excel':
            nrows = sheet.nrows
            ncols = sheet.ncols
        elif self.ftype == 'libre':
            nrows = sheet.nrows()
            ncols = sheet.ncols()
        self.grids[sheetIdx].ClearGrid()
        # get headers
        beginRow = self.dataRow.GetValue()-1
        if self.headerRow.IsChecked():
            for idxCol in range(ncols):
                if self.ftype == 'excel':
                    val = unicode(sheet.cell(beginRow, idxCol).value)
                elif self.ftype == 'libre':
                    val = unicode(sheet[beginRow, idxCol].value)
                #print idxCol, val
                self.grids[sheetIdx].SetColLabelValue(idxCol, val)
            bonus = 1
        else:
            self.headers = []
            bonus = 0
        for idx_row in range(beginRow+bonus,nrows):
            for idx_col in range(ncols):
                if self.ftype == 'excel':
                    val = unicode(sheet.cell(idx_row, idx_col).value)
                elif self.ftype == 'libre':
                    val = unicode(sheet[idx_row, idx_col].value)
                self.grids[sheetIdx].SetCellValue(idx_row-beginRow-bonus, idx_col, val)

    def ImportButton(self, event):
        if self.ftype == "excel":
            sheets = self.workbook.sheets()
        elif self.ftype == "libre":
            sheets = self.workbook.sheets
        self.varnames = []
        self.gridData = []
        sheetIdx = self.worksheets.GetSelection()
        sheet = sheets[sheetIdx]
        # beginData = # get row where data begins
        if self.ftype == 'excel':
            nrows = sheet.nrows
            ncols = sheet.ncols
        elif self.ftype == 'libre':
            nrows = sheet.nrows()
            ncols = sheet.ncols()
        # get headers
        beginRow = self.dataRow.GetValue()-1
        if self.headerRow.IsChecked():
            self.headers = []
            for idxCol in range(ncols):
                if self.ftype == 'excel':
                    val = unicode(sheet.cell(beginRow, idxCol).value)
                elif self.ftype == 'libre':
                    val = unicode(sheet[beginRow, idxCol].value)
                self.headers.append(val)
            bonus = 1
        else:
            self.headers = []
            bonus = 0
        for idx_row in range(beginRow+bonus, nrows):
            line = []
            for idx_col in range(ncols):
                if self.ftype == 'excel':
                    val = unicode(sheet.cell(idx_row, idx_col).value)
                elif self.ftype == 'libre':
                    val = unicode(sheet[idx_row, idx_col].value)
                line.append(val)
            self.gridData.append(line)
        self.Close()


################################################
# Function to control all this

def ImportSS(frame, startDir):
    """
    Controls all the module.
    Parameters: startDir: where to start the file dialog
    Returns: 
    filename: Path + File name selected by user
    headers: Variable name (None if none selected)
    data: data as a list of lists
    """
    FileName = GetFilename(frame, startDir)
    if FileName.fileName == None:
        return None
    dlg = ImportDialog(FileName)
    if dlg.ShowModal():
        if dlg.FileName.fileName == None:
            dlg.Destroy()
            return None
        else:
            fileName = dlg.FileName.fileName
            variableNames = dlg.headers
            gridData = dlg.data
            dlg.Destroy()
            return fileName, variableNames, gridData
    else:
        dlg.Destroy()
        return None


################################################
# Main routine for testing only!

if __name__ == '__main__':
    startDir = os.path.expanduser("~")
    app = wx.App(False)
    x = ImportCSV(startDir)
    print x[0]
    try:
        print x[1],len(x[1])
    except TypeError:
        print "No headers"
    print x[2],len(x[2])
    #x.Close()
    #frame = ImportDialog(startDir)
    #frame.Show()
    app.MainLoop()  


