"""
ImportCSV.py

A Python module to import all manner of CSV files. Produces a dialog 
in wxPython for users to specify things like delimiters and so on.

Usage:


import ImportCSV

def GetData(frame, base_directory):
    result = ImportCSV.ImportCSV(base_directory)
    if result == None:
        # User did not select file 
    else:
        file_name = result[0]       # string
        variable_names = result[1]  # list
        data = result[2]            # list of lists

Requires two parameters: a wxFrame and the directory to start
Returns:

1. Name of imported file
2. Variable names (if any)
3. Data
OR
4. None (no file selected or error made import impossible)

(c) 2014 Alan James Salmoni

"""



from __future__ import unicode_literals
import os, os.path, sys, codecs
import wx
import wx.grid as gridlib

################################################
# Dialog to retrieve file name. Needed before we can do anything

class GetFilename(object):
    def __init__(self, parent, startDir=None):
        if not startDir:
            startDir = os.path.expanduser("~")
        dlg = wx.FileDialog(parent, message="Open a CSV file", defaultDir=startDir, \
                wildcard="CSV text (*.csv)|*.csv|Plain text (*.txt)|*.txt|\
                Data file (*.dat)|*.dat|Any file (*.*)|*.*")
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
    def __init__(self, parent, fileName):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        help_text = "Salstat can load files from Excel and LibreOffice/OpenOffice. "
        t1 = wx.StaticText(self, -1, label=help_text, pos=(10,10))
        t1.Wrap(545)


################################################
# Panel for delimited files

class PanelDelimiter(wx.Panel):
    def __init__(self, parent, fileName):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        help_text = "Delimited files are separated (delimited) by characters like a comma. Salstat lets you specify the delimiters you need as well as a header (variable names)."
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
        self.del_02.SetValue(True)
        self.edit_02.SetValue('"')

################################################
# Panel for fixed width files

class PanelFixedWidth(wx.Panel):
    def __init__(self, parent, fileName):
        wx.Panel.__init__(self, parent, -1)
        help_text = "Fixed width files blah, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
        t1 = wx.StaticText(self, -1, label=help_text, pos=(10,10))
        t1.Wrap(545)

################################################
# Main class that binds it all together

class ImportDialog(wx.Dialog):
    def __init__(self, FileName):
        wx.Dialog.__init__(self, None, title="Importing a CSV file",\
                size=(600,470))
        self.FileName = FileName
        self.decider = wx.Notebook(self, -1, pos=(10,0), \
                size=(580,240), style=wx.NB_TOP)
        self.p1 = PanelDelimiter(self.decider, self.FileName.fileName)
        self.p2 = PanelFixedWidth(self.decider, self.FileName.fileName)
        self.decider.AddPage(self.p1, "Delimited files")
        self.decider.AddPage(self.p2, "Fixed width files")
        t1 = wx.StaticText(self,-1,label="Import from row:",pos=(245,250))
        self.headerRow = wx.CheckBox(self, 760, " Header on first row", \
                pos=(430,250))
        self.dataRow = wx.SpinCtrl(self,766,min=1,max=100, initial=1, \
                pos=(365,250),size=(50,-1))
        self.dataRow.SetValue(1)
        self.buttonImport = wx.Button(self,763,"Import", \
                pos=(500,400),size=(70,-1))
        self.buttonImport.SetDefault()
        self.buttonCancel = wx.Button(self,764,"Cancel", \
                pos=(405,400),size=(70,-1))
        self.grid = gridlib.Grid(self, -1, size=(560,100),pos=(20,290))
        #self.grid.HideRowLabels()
        self.MaxRows = 100
        self.MaxCols = 8
        self.grid.SetColLabelSize(16)
        self.grid.SetRowLabelSize(40)
        self.grid.SetDefaultColSize(60)
        self.grid.CreateGrid(self.MaxRows,self.MaxCols)
        for i in range(8):
            self.grid.SetRowSize(i,16)
            self.grid.SetColLabelValue(i, " ")
        self.gridFont = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL)
        self.grid.SetDefaultCellFont(self.gridFont)
        lineEndChoices = ['Not sure','\\n (Unix)','\\r\\n (Windows)','\\r (old Mac)']
        t3 = wx.StaticText(self,-1,"Line ending:",pos=(20,250))
        self.lineEnd = wx.Choice(self, 765,pos=(105,248),size=(120,-1),\
                choices = lineEndChoices)
        self.AttemptPreview()
        # It seems odd but it seems better for all events to be routed to the same method
        wx.EVT_CHECKBOX(self, 760, self.AttemptPreview)
        wx.EVT_TEXT(self, 761, self.AttemptPreview)
        wx.EVT_TEXT(self, 762, self.AttemptPreview)
        wx.EVT_BUTTON(self, 764, self.CancelButton)
        wx.EVT_BUTTON(self, 763, self.ImportButton)
        wx.EVT_CHOICE(self, 765, self.AttemptPreview)
        wx.EVT_SPINCTRL(self, 766, self.AttemptPreview)

    def AttemptPreview(self, event=None):
        # check we have filename first
        if self.FileName.fileName == None:
            return
        else:
            # retrieve data 
            data = []
            fin = codecs.open(self.FileName.fileName, encoding='utf-8')
            #fin = open(self.FileName.fileName,'r')
            data = fin.read(10000)
            fin.close()
            # populate preview
            self.FillGrid(data)

    def FillGrid(self, data):
        # Fill self.grid with data and variables
        self.grid.ClearGrid()
        # Get line ending
        endSelect = self.lineEnd.GetSelection()
        lineTerm = '\n'
        if endSelect == 0:
            # Use most common as a guess
            lineEnds = ['\n','\r\n','\r']
            maxes = []
            for lineEnd in lineEnds:
                maxes.append(self.GetMax(data, lineEnd))
            lineTerm = lineEnds[lineEnds.index(max(lineEnds))-1]
        # Or have user selection
        elif endSelect == 1:
            lineTerm = '\n'
        elif endSelect == 2:
            lineTerm = '\r\n'
        elif endSelect == 3:
            lineTerm = '\r'
        # split file into rows
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
        val = self.p1.edit_01.GetValue()
        if val != "":
            delims += val
        quotes = self.p1.edit_02.GetValue()
        beginRow = self.dataRow.GetValue()
        if self.headerRow.IsChecked():
            # User's setting a row as a header for the grid
            self.headers = self.ParseLine(data[beginRow-1], delims, quotes)
            for idx in range(self.MaxCols):
                try:
                    self.grid.SetColLabelValue(idx, self.headers[idx])
                except IndexError:
                    self.grid.SetColLabelValue(idx," ")
            bonus = 1
        else:
            for idx in range(self.MaxCols):
                self.grid.SetColLabelValue(idx, " ")
            bonus = 0
            self.headers = None
        # Fill the grid as specified
        data = data.split(lineTerm)
        self.gridData = []
        for row in range(self.MaxRows):
            try:
                line = data[beginRow+bonus+row-1]
                tokens = self.ParseLine(line, delims, quotes)
                self.gridData.append(tokens)
                k = len(tokens)
                for idxy in range(self.MaxCols):
                    try:
                        self.grid.SetCellValue(row,idxy,tokens[idxy])
                    except IndexError:
                        self.grid.SetCellValue(row,idxy,"")
            except IndexError:
                break

    def ParseLine(self, line, delims, quotes):
        """
        Parses a line of CSV text into components. This attempts to 
        be a proper parser that can cope with multiple delimiters.
        """
        inQuote = False # flag for being 'within' quotes
        token = '' # current token
        tokens = [] # list of tokens
        # inQuoteChar = None
        for char in line:
            if inQuote: # so if we're in the middle of a quote...
                if char == inQuoteChar: # ...and have a matching quote character...
                    tokens.append(token) # add the token to list (ignore quote character)
                    token = '' # and begin new token
                    inQuote = False # flag that we're not in a quote any more
                else: # But if char is a non-matching quote...
                    token += char # ...just add to token 
            elif char in delims: # or if char is a delimiter...
                if len(token) > 0: # ...and token is worth recording...
                    tokens.append(token) # add token to list
                    token = '' # and begin new token
                else: # if token has 0 length and no content...
                    pass # ...adjacent delimiters so do nothing
            elif char in quotes: # But if char is a quote...
                inQuoteChar = char # record it to check for matching quote later
                inQuote = True # and flag that we're in a quotation
            else: # And if char is anything else...
                token += char # add to token
        if len(token) > 0: # Check if last item is worth recording (len > 0)
            tokens.append(token) # add to list of tokens
        return tokens # return list of tokens

    def GetMax(self, data, lineEnd):
        # help method to find the maximum of each line ending
        return len(data.split(lineEnd))

    def CancelButton(self, event):
        # let's get out!
        self.FileName.fileName = None
        self.Close()

    def ImportButton(self, event):
        fin = codecs.open(self.FileName.fileName, encoding='utf-8')
        data = fin.read()
        fin.close()
        endSelect = self.lineEnd.GetSelection()
        lineTerm = '\n'
        if endSelect == 0:
            # Use most common as a guess
            lineEnds = ['\n','\r\n','\r']
            maxes = []
            for lineEnd in lineEnds:
                maxes.append(self.GetMax(data, lineEnd))
            lineTerm = lineEnds[lineEnds.index(max(lineEnds))-1]
        # Or have user selection
        elif endSelect == 1:
            lineTerm = '\n'
        elif endSelect == 2:
            lineTerm = '\r\n'
        elif endSelect == 3:
            lineTerm = '\r'
        # split file into rows
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
        val = self.p1.edit_01.GetValue()
        if val != "":
            delims += val
        quotes = self.p1.edit_02.GetValue()
        beginRow = self.dataRow.GetValue()
        if self.headerRow.IsChecked():
            # User's setting a row as a header for the grid
            self.headers = self.ParseLine(data[beginRow-1], delims, quotes)
            for idx in range(self.MaxCols):
                try:
                    self.grid.SetColLabelValue(idx, self.headers[idx])
                except IndexError:
                    self.grid.SetColLabelValue(idx," ")
            bonus = 1
        else:
            for idx in range(self.MaxCols):
                self.grid.SetColLabelValue(idx, " ")
            bonus = 0
            self.headers = None
        # Fill the grid as specified
        data = data.split(lineTerm)
        self.gridData = []
        for row in range(len(data)):
            try:
                line = data[beginRow+bonus+row-1]
                tokens = self.ParseLine(line, delims, quotes)
                self.gridData.append(tokens)
            except IndexError:
                break
        self.Close()

class CSVObject(object):
    """
    This class instantiates a file object as an interable. It means that 
    CSV files can be read more efficiently than reading the entire data 
    into memory. 
    """
    def __init__(self, fileName, delims, quotes):
        self.fileName = fileName
        self.delims = delims
        self.quotes = quotes
        self.fin = open(fileName, 'r')
        
    def __iter__(self):
        return self
        
    def next(self):
        line = self.fin.next()
        return self.ParseLine(line)

    def ParseLine(self, line):
        """
        Parses a line of CSV text into components. This attempts to 
        be a proper parser that can cope with multiple delimiters.
        """
        inQuote = False # flag for being 'within' quotes
        token = '' # current token
        tokens = [] # list of tokens
        for char in line:
            if inQuote: # so if we're in the middle of a quote...
                if char == inQuoteChar: # ...and have a matching quote character...
                    tokens.append(token) # add the token to list (ignore quote character)
                    token = '' # and begin new token
                    inQuote = False # flag that we're not in a quote any more
                else: # But if char is a non-matching quote...
                    token += char # ...just add to token 
            elif char in self.delims: # or if char is a delimiter...
                if len(token) > 0: # ...and token is worth recording...
                    tokens.append(token) # add token to list
                    token = '' # and begin new token
                else: # if token has 0 length and no content...
                    pass # ...adjacent delimiters so do nothing
            elif char in self.quotes: # But if char is a quote...
                inQuoteChar = char # record it to check for matching quote later
                inQuote = True # and flag that we're in a quotation
            else: # And if char is anything else...
                token += char # add to token
        if len(token) > 0: # Check if last item is worth recording (len > 0)
            tokens.append(token) # add to list of tokens
        return tokens # return list of tokens


################################################
# Function to control all this

def ImportCSV(frame=None, startDir=None):
    """
    Controls all the module.
    Parameters: startDir: where to start the file dialog
    Returns: 
    filename: Path + File name selected by user
    headers: Variable name (None if none selected)
    data: data as a list of lists
    """
    if not startDir:
        startDir = os.path.expanduser("~")
    if not frame:
        app = wx.App(False)
        frame = wx.Frame(None, wx.ID_ANY, "Hello World")
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
            data = dlg.gridData
            dlg.Destroy()
            return fileName, variableNames, data
    else:
        dlg.Destroy()
        return None


################################################
# Main routine for testing only!

if __name__ == '__main__':
    #print ImportCSV()
    fname = '/Users/alansalmoni/00_test.csv'
    delims = ", ;"
    quotes = '"'
    obj = CSVObject(fname, delims, quotes)
    for ln in obj:
        print ln

