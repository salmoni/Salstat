"""
ImportExcel.py
A Python module to read Excel files into Salstat. Does not include xlsx format
(at least, not just yet)
"""

from __future__ import unicode_literals
import os, os.path 
import HTMLParser
import wx, wx.aui, xlrd
import wx.grid as gridlib
import requests
import BeautifulSoup as BS


################################################
# Save data as HTML table
def ExportHTML(filename, grid):
    fout = open(filename, "w")
    numcols = grid.GetNumberCols()
    numrows = grid.GetNumberRows()
    fout.write('<!DOCTYPE html>\n<html lang="en">\n<body>\n<table>\n<tr>\n')
    for colidx in range(numcols):
        fout.write('<th>%s</th>'%(grid.GetColLabelValue(colidx)))
    fout.write('</tr>/n')
    for i in range(numrows):
        fout.write('<tr>')
        for j in range(numcols):
            fout.write('<td>%s</td>'%(grid.GetCellValue(i, j)))
        fout.write('</tr>\n')
    fout.write('</table>\n</body>\n</html>')
    fout.close
    grid.Saved = True

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
    def __init__(self, URL):
        wx.Dialog.__init__(self, None, title="Scraping a web page",\
                size=(600,380))
        self.URL = URL
        # ensure URL is a valid URL
        # TODO
        # page is retrieved
        try:
            request = requests.get(self.URL)
            page = request.text
        except:
            page = None
        # page is parsed and tables extracted
        if not page:
            self.URL = None
            self.Close()
        else:
            parser = HTMLParser.HTMLParser()
            soup = BS.BeautifulSoup(page)
            self.tables = soup.findAll('table')
            # user selects which table to import
            # table & data are imported
            ID_WINDOW_CLOSE = wx.NewId()
            help_text = "These are all the tables in the web page you just entered. "
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
            self.grids = []
            for idx, table in enumerate(self.tables):
                caption = table.find('caption')
                if caption == None:
                    caption = 'table %04.f'%(idx)
                # set attributes to hold headers & stats
                variableNames = []
                gridData = []
                # get number cols, rows
                headings = table.findAll('th')
                for heading in headings:
                    val = heading.text
                    val = parser.unescape(val)
                    variableNames.append(val)
                rows = table.findAll('tr')
                ncols = 0
                nrows = len(rows)
                for row in rows:
                    line = []
                    cols = row.findAll('td')
                    if len(cols) > ncols:
                        ncols = len(cols)
                    for col in cols:
                        line.append(col.text)
                    gridData.append(line)
                self.grids.append(Grid(self.worksheets, -1))
                self.grids[idx].HideRowLabels()
                self.grids[idx].SetColLabelSize(16)
                self.grids[idx].SetRowLabelSize(40)
                self.grids[idx].SetDefaultColSize(60)
                self.grids[idx].CreateGrid(nrows+10,ncols+10)
                for i in range(ncols):
                    self.grids[idx].SetColLabelValue(i, " ")
                for i in range(nrows):
                    self.grids[idx].SetRowSize(i,16)
                self.grids[idx].SetDefaultCellFont(self.gridFont)
                if caption == None:
                    caption = 'table %04.f'%(idx)
                headings = table.findAll('th')
                for idxhead, heading in enumerate(headings):
                    self.grids[idx].SetColLabelValue(idxhead, heading.text)
                self.worksheets.AddPage(self.grids[idx],caption)
                for idx_row in range(len(gridData)):
                    for idx_col in range(len(gridData[idx_row])):
                        val = unicode(gridData[idx_row][idx_col])
                        val = parser.unescape(val)
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
        self.URL = None
        self.Close()

    def AdjustGrid(self, event):
        pass

    def ImportButton(self, event):
        parser = HTMLParser.HTMLParser()
        self.gridData = []
        self.headers = []
        tableIdx = self.worksheets.GetSelection()
        table = self.tables[tableIdx]
        # get headers
        beginRow = self.dataRow.GetValue() - 1
        headings = table.findAll('th')
        for heading in headings:
            val = heading.text
            val = parser.unescape(val)
            self.headers.append(val)
        rows = table.findAll('tr')
        for row in rows:
            cols = row.findAll('td')
            line = []
            for col in cols:
                val = parser.unescape(col.text)
                line.append(val)
            if len(line) > 0:
                self.gridData.append(line)
        self.Close()


################################################
# Function to control all this

def ImportHTML(frame, URL):
    """
    Controls all the module.
    Parameters: startDir: where to start the file dialog
    Returns: 
    filename: Path + File name selected by user
    headers: Variable name (None if none selected)
    data: data as a list of lists
    """
    dlg = ImportDialog(URL)
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



