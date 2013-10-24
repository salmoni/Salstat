#!/usr/bin/env python

"""SalStat Statistics Package. Copyright 2002 Alan James Salmoni. Licensed 
under the GNU General Public License (GPL). See the file COPYING for full
details of this license. """

# import wx stuff
from __future__ import unicode_literals
import wx
from wx.stc import *
import wx.grid as gridlib
import wx.html as htmllib
import wx.html2 as html2lib
import xlrd, xlwt # import xls format
import string, os, os.path, pickle

# import SalStat specific modules
import salstat_stats, images, xlrd, tabler, charter, ChartWindow
import MetaGrid
import numpy, math

# and for plots!
#from wx.Python.lib.wx.PlotCanvas import *
#from wx.Python.lib import wx.PlotCanvas
# set ip the xml modules
from xml.dom import minidom

#---------------------------------------------------------------------------
# set up id's for menu events - all on menu, some also available elsewhere
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
ID_PREPARATION_DESCRIPTIVES = wx.NewId()
ID_PREPARATION_TRANSFORM = wx.NewId()
ID_PREPARATION_OUTLIERS = wx.NewId()
ID_PREPARATION_NORMALITY = wx.NewId()
ID_TRANSFORM_SQUAREROOT = wx.NewId()
ID_TRANSFORM_SQUARE = wx.NewId()
ID_TRANSFORM_INVERSE = wx.NewId()
ID_TRANSFORM_OTHER = wx.NewId()
ID_ANALYSE_1COND = wx.NewId()
ID_ANALYSE_2COND = wx.NewId()
ID_ANALYSE_3COND = wx.NewId()
ID_ANALYSE_CORRELATION = wx.NewId()
ID_ANALYSE_2FACT = wx.NewId()
ID_ANALYSE_SCRIPT = wx.NewId()
ID_ANALYSE2_1COND = wx.NewId()
ID_ANALYSE2_2COND = wx.NewId()
ID_ANALYSE2_3COND = wx.NewId()
ID_ANALYSE2_1_TTEST = wx.NewId()
ID_ANALYSE2_1_SIGN = wx.NewId()
ID_CHART = wx.NewId()
ID_CHART_DRAW = wx.NewId()
ID_BARCHART_DRAW = wx.NewId()
ID_HELP_WIZARD = wx.NewId()
ID_HELP_TOPICS = wx.NewId()
ID_HELP_SCRIPTING = wx.NewId()
ID_HELP_LICENCE = wx.NewId()
ID_HELP_ABOUT = wx.NewId()
ID_OFILE_NEW = wx.NewId()
ID_OFILE_OPEN = wx.NewId()
ID_OFILE_SAVE = wx.NewId()
ID_OFILE_SAVEAS = wx.NewId()
ID_OFILE_PRINT = wx.NewId()
ID_OFILE_CLOSE = wx.NewId()
ID_OEDIT_CUT = wx.NewId()
ID_OEDIT_COPY = wx.NewId()
ID_OEDIT_PASTE = wx.NewId()
ID_OEDIT_SELECTALL = wx.NewId()
ID_OPREF_FONT = wx.NewId()
ID_FILE_GSAVEAS = wx.NewId()
ID_FILE_GPRINTSETUP = wx.NewId()
ID_FILE_GPRINTPREVIEW = wx.NewId()
ID_FILE_GPRINT = wx.NewId()
ID_FILE_GCLOSE = wx.NewId()
ID_TITLE_GYAXIS = wx.NewId()
ID_TITLE_GXAXIS = wx.NewId()
ID_TITLE_GTITLE = wx.NewId()
ID_TITLE_LEGEND = wx.NewId()
ID_TITLE_GRID = wx.NewId()

DescList=['N','Sum','Mean','Variance','Standard Deviation','Standard Error',\
                                    'Sum of Squares','Sum of Squared Devs', \
                                    'Coefficient of Variation','Minimum',   \
                                    'Maximum','Range','Number Missing',     \
                                    'Geometric Mean','Harmonic Mean',       \
                                    'Skewness','Kurtosis', 'Median',        \
                                    'Median Absolute Deviation','Mode',     \
                                    'Interquartile Range',                  \
                                    'Number of Unique Levels']

HypList = ['One tailed','Two tailed']
inits={}    # dictionary to hold the config values
ColsUsed = []
RowsUsed = []
missingvalue = -99.999
global filename # ugh
filename = 'UNTITLED'
global BWidth, BHeight # ugh again!
BWidth = 80
BHeight = 25
HOME = os.getcwd()

if wx.Platform == '__WXMSW__':
    face1 = 'Courier New'
    face2 = 'Times New Roman'
    face3 = 'Courier New'
    fontsizes = [7,8,10,12,16,22,30]
    pb = 12
    wind = 50
    DOCDIR = 'c:\My Documents'
    INITDIR = os.getcwd()
else:
    face1 = 'Helvetica'
    face2 = 'Times'
    face3 = 'Courier'
    fontsizes = [10,12,14,16,19,24,32]
    pb = 12
    wind = 50
    DOCDIR = os.environ['HOME']
    INITDIR = DOCDIR

class History:
    def __init__(self):
        self.history = '' # change this for the proper DTD please!

    def AppendEvent(self, xmltags):
        self.history = self.history + xmltags

    def ClearHistory(self):
        self.history = ''

class SaveDialog2(wx.Dialog):
    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, "Save Data?", \
                           size=(404+wind,100+wind))#, style = wx.DIALOG_MODAL)
        icon = images.getIconIcon()
        #icon = wx.Icon("icons/PurpleIcon05_32.png",wx.BITMAP_TYPE_PNG)
        iconPNG = wx.Image("icons/PurpleIcon05_64.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        iconBMP = wx.StaticBitmap(self, -1, iconPNG, pos=(20,16))
        l1 = wx.StaticText(self, -1, 'Do you want to save the changes you made to', pos=(105,16))
        l2 = wx.StaticText(self, -1, 'this document?', pos=(105, 36))
        discardButton = wx.Button(self, 332, "Don't save", size=(90, 21),pos=(105,80))
        saveButton = wx.Button(self, 331, "Save...", size=(69, 21),pos=(274,80))
        CancelButton = wx.Button(self, 333, "Cancel", size=(69, 21),pos=(355,80))
        self.SetIcon(ico)
        self.Layout()
        wx.EVT_BUTTON(self, 331, self.SaveData)
        wx.EVT_BUTTON(self, 332, self.DiscardData)
        wx.EVT_BUTTON(self, 333, self.CancelDialog)

    def SaveData(self, event):
        self.EndModal(2)

    def DiscardData(self, event):
        self.EndModal(3)

    def CancelDialog(self, event):
        self.EndModal(4)

class SaveDialog(wx.Dialog):
    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, "Save Data?", \
                           size=(270+wind,100+wind))#, style = wx.DIALOG_MODAL)
        icon = images.getIconIcon()
        self.SetIcon(ico)
        self.Choice = 'none'
        vbox = wx.BoxSizer(wx.VERTICAL)
        l1 = wx.StaticText(self, -1, 'You have unsaved Data')
        l2 = wx.StaticText(self, -1, 'Do you wish to save it?')
        vbox.Add(l1,1, wx.ALIGN_CENTER)
        vbox.Add(l2,1, wx.ALIGN_CENTER)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        saveButton = wx.Button(self, 331, "Save...", size=(BWidth, BHeight))
        discardButton = wx.Button(self, 332, "Don't save", size=(BWidth, BHeight))
        CancelButton = wx.Button(self, 333, "Cancel", size=(BWidth, BHeight))
        hbox.Add(saveButton, 0, wx.ALL, 5)
        hbox.Add(discardButton, 0, wx.ALL, 5)
        hbox.Add(CancelButton, 0, wx.ALL, 5)
        vbox.Add(hbox,1)
        self.SetAutoLayout(True)
        self.SetSizer(vbox)
        self.Layout()
        self.res = ""
        wx.EVT_BUTTON(self, 331, self.SaveData)
        wx.EVT_BUTTON(self, 332, self.DiscardData)
        wx.EVT_BUTTON(self, 333, self.CancelDialog)

    def SaveData(self, event):
        frame.grid.Saved = True
        frame.grid.SaveAsDataASCII(self) # will it be ASCII or XML?
        output.Close(True)
        frame.Close(True)
        self.res = "Saved"
        self.Close(True)

    def DiscardData(self, event):
        output.Close(True)
        frame.Close(True)
        self.res = "Discard"
        self.Close(True)

    def CancelDialog(self, event):
        self.res = "Cancel"
        self.Close(True)

#---------------------------------------------------------------------------
# creates an init file in the home directory of the user
class GetInits:
    """This class deals with a users init file. The coords and sizes of the
    various widgets are kept here, and are stored throughout the program
    as a dictionary for easy access. When the program starts, the home
    directory is checked for the init files existence. If absent, it is
    created with a series of default values. If it is present, the values are
    read into the dictionary in a slightly roundabout way! I am sure that
    there is a more "Python" way of doing this, but this way works for now"""
    def __init__(self):
        self.initfile = os.path.join(INITDIR, '.salstatrc')
        if os.path.isfile(self.initfile):
            self.ReadInitFile(self.initfile)
        else:
            self.CreateInitFile(self.initfile)

    def ReadInitFile(self, initfilename):
        inits.clear()
        fin = file(initfilename, 'r')
        for i in range(28):
            a = fin.readline()
            a = string.split(a)
            tmpdict = {a[0]:a[1]}
            inits.update(tmpdict)

    def CreateInitFile(self, initfilename):
        inits = {
        'gridsizex': '600',
        'gridsizey': '420',
        'gridposx': '50',
        'gridposy': '20',
        'gridcellsx': '20',
        'gridcellsy': '80',
        'outputsizex': '500',
        'outputsizey': '400',
        'outputposx': '20',
        'outputposy': '50',
        'scriptsizex': '600',
        'scriptsizey': '400',
        'scriptposx': '35',
        'scriptposy': '35',
        'chartsizex': '600',
        'chartsizey': '400',
        'chartposx': '50',
        'chartposy': '50',
        'helpsizex': '600',
        'helpsizey': '400',
        'helpposx': '40',
        'helpposy': '40',
        'lastfile1': "...",
        'lastfile2': "...",
        'lastfile3': "...",
        'lastfile4': "...",
        'opendir': DOCDIR,
        'savedir': DOCDIR
        }
        initskeys = inits.keys()
        initsvalues = inits.values()
        fout = file(initfilename,'w')
        for i in range(len(initskeys)):
            fout.write(str(initskeys[i])+' '+str(initsvalues[i])+'\n')
        fout.close()
        self.ReadInitFile(initfilename) # damn hack!

#---------------------------------------------------------------------------
# class to output the results of several "descriptives" in one table
class ManyDescriptives:
    def __init__(self, source, ds):
        #__x__ = len(ds)
        str2 = '<table class="table table-striped">'
        outlist = ['Statistic']
        for i in ds:
            outlist.append(i.Name)
        ln = tabler.vtable(outlist)
        str2 = str2 + ln

        if source.DescChoice.IsChecked(0):
            outlist = ['N']
            for i in ds:
                outlist.append(i.N)
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if source.DescChoice.IsChecked(1):
            outlist = ['Sum']
            for i in ds:
                outlist.append(i.sum)
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if source.DescChoice.IsChecked(2):
            outlist = ['Mean']
            for i in ds:
                outlist.append(i.mean)
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if source.DescChoice.IsChecked(3):
            outlist = ['Sample variance']
            for i in ds:
                outlist.append(i.samplevar)
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if source.DescChoice.IsChecked(4):
            outlist = ['Sample Standard Deviation']
            for i in ds:
                outlist.append(i.stddev)
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if source.DescChoice.IsChecked(5):
            outlist = ['Standard error']
            for i in ds:
                outlist.append(i.stderr)
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if source.DescChoice.IsChecked(6):
            outlist = ['Sum of squares']
            for i in ds:
                outlist.append(i.sumsquares)
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if source.DescChoice.IsChecked(7):
            outlist = ['Sum of squared deviations']
            for i in ds:
                outlist.append(i.ssdevs)
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if source.DescChoice.IsChecked(8):
            outlist = ['Coefficient of variation']
            for i in ds:
                outlist.append(i.coeffvar)
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if source.DescChoice.IsChecked(9):
            outlist = ['Minimum']
            for i in ds:
                outlist.append(i.minimum)
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if source.DescChoice.IsChecked(10):
            outlist = ['Maximum']
            for i in ds:
                outlist.append(i.maximum)
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if source.DescChoice.IsChecked(11):
            outlist = ['Range']
            for i in ds:
                outlist.append(i.range)
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if source.DescChoice.IsChecked(12):
            outlist = ['Number missing']
            for i in ds:
                outlist.append(i.missing)
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if source.DescChoice.IsChecked(13):
            outlist = ['Geometric mean']
            for i in ds:
                outlist.append(i.geomean)
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if source.DescChoice.IsChecked(14):
            outlist = ['Harmonic mean']
            for i in ds:
                outlist.append(i.harmmean)
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if source.DescChoice.IsChecked(15):
            outlist = ['Skewness']
            for i in ds:
                outlist.append(i.skewness)
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if source.DescChoice.IsChecked(16):
            outlist = ['Kurtosis']
            for i in ds:
                outlist.append(i.kurtosis)
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if source.DescChoice.IsChecked(17):
            outlist = ['Median']
            for i in ds:
                outlist.append(i.median)
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if source.DescChoice.IsChecked(18):
            outlist = ['Median absolute deviation']
            for i in ds:
                outlist.append(i.mad)
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if source.DescChoice.IsChecked(19):
            outlist = ['Mode']
            for i in ds:
                outlist.append(i.mode)
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if source.DescChoice.IsChecked(20):
            outlist = ['Number of unique values']
            for i in ds:
                outlist.append(i.numberuniques)
            ln = tabler.vtable(outlist)
            str2 = str2 + ln
        output.Addhtml(str2+'</table>\n')

#---------------------------------------------------------------------------
# class for grid - used as datagrid.
class SimpleGrid(gridlib.Grid):
    def __init__(self, parent, log):
        gridlib.Grid.__init__(self, parent)
        self.parent = parent
        self.named = False
        self.Saved = True
        self.filename = "Untitled"
        self.moveTo = None
        self.SetGridLineColour(wx.LIGHT_GREY)
        self.CreateGrid(int(inits.get("gridcellsy")), \
                                    int(inits.get("gridcellsx")))
        self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_BOTTOM)
        #for i in range(20):
            #self.SetColFormatFloat(i, 8, 4)
        gridlib.EVT_GRID_CELL_CHANGE(self, self.AlterSaveStatus)
        gridlib.EVT_GRID_RANGE_SELECT(self, self.RangeSelected)
        self.wildcard = "Any File (*.*)|*.*|" \
                        "ASCII data format (*.dat)|*.dat|" \
                        "SalStat Format (*.xml)|*.xml"
        self.BeginMeta()

    def BeginMeta(self):
        self.meta = {}
        ncols = self.GetNumberCols()
        for colidx in range(ncols):
            labelObj = {}
            varObj = {'label':labelObj}
            varObj['name'] = self.GetColLabelValue(colidx)
            varObj['ivdv'] = 'None set'
            varObj['align'] = 'left'
            varObj['missingvalues'] = ''
            varObj['measure'] = 'None set'
            self.meta[colidx] = varObj

    def RangeSelected(self, event):
        if event.Selecting():
            self.tl = event.GetTopLeftCoords()
            self.br = event.GetBottomRightCoords()

    def AlterSaveStatus(self, event):
        # this is activated when the user enters some data
        self.Saved = False
        # also record in the history file
        col = self.GetGridCursorCol()
        row = self.GetGridCursorRow()
        value = self.GetCellValue(row, col)
        xmlevt = '<data row="'+str(row)+'" col="'+str(col)+'">'+str(value)+'</data>\n'
        hist.AppendEvent(xmlevt)
        #print hist.history
        # check if missing data and mark background if it is

    def CutData(self, event):
        buffer = wx.TextDataObject()
        currentcol = self.GetGridCursorCol()
        currentrow = self.GetGridCursorRow()
        if self.IsSelection():
            self.tl = self.GetSelectionBlockTopLeft()[0]
            self.br = self.GetSelectionBlockBottomRight()[0]
            top = self.tl[0]
            left = self.tl[1]
            bot = self.br[0] + 1
            right = self.br[1] + 1
            data = ''
            for row in range(top, bot):
                line = []
                for col in range(left, right):
                    val = str(self.GetCellValue(row, col))
                    self.SetCellValue(row, col, '')
                    line.append(val)
                data = data + '\t'.join(line) + '\r'
        else:
            data = self.GetCellValue(currentrow, currentcol)
        if (wx.TheClipboard.Open()):
            buffer.SetText(data)
            wx.TheClipboard.SetData(buffer)
            wx.TheClipboard.Close()
            self.SetCellValue(currentrow, currentcol, '')
            self.Saved = False

    def CopyData(self, event):
        buffer = wx.TextDataObject()
        currentcol = self.GetGridCursorCol()
        currentrow = self.GetGridCursorRow()
        if self.IsSelection(): # extend this only if SalStat can paste lists
            self.tl = self.GetSelectionBlockTopLeft()[0]
            self.br = self.GetSelectionBlockBottomRight()[0]
            top = self.tl[0]
            left = self.tl[1]
            bot = self.br[0] + 1
            right = self.br[1] + 1
            data = ''
            for row in range(top, bot):
                line = []
                for col in range(left, right):
                    val = str(self.GetCellValue(row, col))
                    line.append(val)
                data = data + '\t'.join(line) + '\r'
        else:
            data = self.GetCellValue(currentrow, currentcol)
        if (wx.TheClipboard.Open()):
            buffer.SetText(data)
            wx.TheClipboard.SetData(buffer)
            wx.TheClipboard.Close()

    def PasteData(self, event):
        buffer = wx.TextDataObject()
        currentcol = self.GetGridCursorCol()
        currentrow = self.GetGridCursorRow()
        res = wx.TheClipboard.Open()
        if res:
            data = wx.TheClipboard.GetData(buffer)
            pastetext = buffer.GetText()
            wx.TheClipboard.Close()
            if pastetext:
                self.Saved = False
                rows = pastetext.split('\r')
                for row in range(len(rows)):
                    cells = rows[row].split('\t')
                    for col in range(len(cells)):
                        val = cells[col]
                        self.SetCellValue(currentrow+row, currentcol+col, val)

    def EditGrid(self, event, numrows):
        insert = self.AppendRows(numrows)

    def DeleteCurrentCol(self, event):
        currentcol = self.GetGridCursorCol()
        self.DeleteCols(currentcol, 1)
        self.AdjustScrollbars()
        xmlevt = '<deleteColumn>'+str(currentcol)+'</deleteColumn>\n'
        hist.AppendEvent(xmlevt)

    def DeleteCurrentRow(self, event):
        currentrow = self.GetGridCursorRow()
        self.DeleteRows(currentrow, 1)
        self.AdjustScrollbars()
        xmlevt = '<deleteRow>'+str(currentrow)+'</deleteRow>\n'
        hist.AppendEvent(xmlevt)

    def SelectAllCells(self, event):
        self.SelectAll()

    def ResizeGrid(self, ncols, nrows):
        spare = 10 # extra spaces
        # check that data is saved before clearing!
        self.ClearGrid()
        self.AppendCols(ncols + spare)
        self.AppendRows(nrows + spare)
    
    # adds columns and rows to the grid
    def AddNCells(self, numcols, numrows):
        insert = self.AppendCols(numcols)
        insert = self.AppendRows(numrows)
        for i in range(self.GetNumberCols() - numcols):
            self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_BOTTOM)
            self.SetColFormatFloat(i, 8, 4)
        self.AdjustScrollbars()
        xmlevt = '<appendColumn>'+str(numcols)+'</appendColumn>\n'
        hist.AppendEvent(xmlevt)
        xmlevt = '<appendRow>'+str(numrows)+'</appendRow>\n'
        hist.AppendEvent(xmlevt)

    # function finds out how many cols contain data - all in a list
    #(ColsUsed) which has col #'s
    def GetUsedCols(self):
        ColsUsed = []
        colnums = []
        cols = self.GetNumberCols()
        for i in range(cols):
            dat = self.GetCellValue(0, i)
            if (dat!=''):
                ColsUsed.append(self.GetColLabelValue(i))
                colnums.append(i)
        return ColsUsed, colnums

    def GetColsUsedList(self):
        colsusedlist = []
        for i in range(self.GetNumberCols()):
            try:
                tmp = float(self.GetCellValue(0,i))
                colsusedlist.append(i)
            except ValueError:
                colsusedlist.append(0)
        return colsusedlist

    def GetUsedColsType(self):
        ColsUsedIV = []
        ColsUsedDV = []
        colnumsIV = []
        colnumsDV = []
        ColsUsed, Colnums = self.GetUsedCols()
        for idx, col in enumerate(Colnums):
            if self.meta[col].ivdv == 'IV':
                ColsUsedIV.append(ColsUsed[idx])
                colnumsIV.append(col)
            elif self.meta[col].ivdv == 'DV':
                ColsUsedDV.append(ColsUsed[idx])
                colnumsDV.append(col)
        return ColsUsedIV, ColsUsedDV, colnumsIV, colnumsDV

    def GetUsedRows(self):
        RowsUsed = []
        for i in range(self.GetNumberCols()):
            if (self.GetCellValue(0, i) != ''):
                for j in range(self.GetNumberRows()):
                    if (self.GetCellValue(j,i) == ''):
                        RowsUsed.append(j)
                        break
        return RowsUsed

    def SaveAsDataASCII(self, event):
        default = inits.get('savedir')
        dlg = wx.FileDialog(self, "Save Data File", default,"",\
                                    "CSV text (*.csv)|*.csv|Plain text (*.txt)|*.txt", wx.SAVE)
        dlg.SetIcon(ico)
        if dlg.ShowModal() == wx.ID_OK:
            inits.update({'savedir': dlg.GetDirectory()})
            filename = dlg.GetPath()
            fout = open(filename, "w")
            cols,waste = self.GetUsedCols()
            if (dlg.GetFilterIndex() == 0):
                #save as plain text
                rows = self.GetUsedRows()
                maxrows = max(rows) 
                for i in range(len(cols)):
                    for j in range(maxrows):
                        if (self.GetCellValue(j,i) == ''):
                            self.SetCellValue(j,i,'.')
                for i in range(maxrows):
                    datapoint=[]
                    for j in range(len(cols)):
                        try:
                            datapoint.append(self.GetCellValue(i, j))
                        except:
                            datapoint.append("0")
                        line = string.join(datapoint)
                    fout.write(line)
                    fout.write('\n')
            elif (dlg.GetFilterIndex() == 1):
                # save as native format
                print "cannot do this just yet!"
            fout.close
            self.Saved = True
            self.named = True
            path, self.filename = os.path.split(filename)
            self.parent.SetTitle(self.filename)

    def SaveDataASCII(self, event):
        if self.named:
            defaultDir = inits.get('savedir')
            fout = open(defaultDir + os.sep + self.filename, "w")
            cols, waste = self.GetUsedCols()
            rows = self.GetUsedRows()
            maxrows = max(rows) + 1
            for i in range(maxrows):
                datapoint=[]
                for j in range(len(cols)):
                    try:
                        datapoint.append(self.GetCellValue(i, j))
                    except:
                        datapoint.append("0")
                line = string.join(datapoint)
                fout.write(line)
                fout.write('\n')
            fout.close
            self.Saved = True
        else:
            self.SaveAsDataASCII(None)

    # Loads an ASCII data file - only with all datapoints filled though!
    # also does csv values as well
    def LoadDataASCII(self, event):
        default = inits.get('opendir')
        dlg = wx.FileDialog(self, "Open Data File", "","",\
                                #self.wildcard, wx.OPEN)
                                "All files (*.*)|*.*|", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        dlg.SetIcon(ico)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if filename[-3:] == 'xml':
                self.LoadNativeXML(filename)
            if filename[-3:] == "xls" or filename[-4:] == "xlsx":
                self.LoadExcel(filename)
            else:
                inits.update({'opendir': dlg.GetDirectory()})
                self.ClearGrid()
                # exception handler here!
                try:
                    fin = open(filename, "r")
                except IOError:
                    pass # what to do if they filename isn't visible? Messagebox?
                gridline = 0
                self.Freeze()
                for i in fin.readlines():
                    words = string.split(i)
                    if len(words) > self.GetNumberCols():
                        NumberCols = len(words) - self.GetNumberCols() + 10
                        self.AddNCells(NumberCols, 0)
                    for j in range(len(words)):
                        self.SetCellValue(gridline, j, words[j])
                    gridline = gridline + 1
                    if (gridline == self.GetNumberRows()):
                        self.AddNCells(0,10)
                fin.close()
                self.Thaw()
            self.ForceRefresh()
            self.Saved = False
            self.named = True
            path, self.filename = os.path.split(filename)
            self.parent.SetTitle(self.filename)

    def LoadExcel(self, filename):
        try:
            workbook = xlrd.open_workbook(filename)
        except: # get proper exception
            pass # could not open file
        try:
            # numsheets = workbook.nsheets
            # user should decide here which sheet.
            # temp code: Default to first
            worksheet = workbook.sheet_by_index(0)
            nrows = worksheet.nrows
            ncols = worksheet.ncols
            self.ResizeGrid(ncols, nrows)
            for idx_row in range(nrows):
                for idx_col in range(ncols):
                    val = unicode(worksheet.cell(idx_row, idx_col).value)
                    self.SetCellValue(idx_row, idx_col, val)
        except:
            pass

    def getData(self, x):
        for i in range(len(x)):
            try:
                row = int(x[i].attributes["row"].value)
                col = int(x[i].attributes["column"].value)
                datavalue = float(self.getText(x[i].childNodes))
                self.SetCellValue(row, col, str(datavalue))
            except ValueError:
                print "problem importing the xml"

    def getText(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc

    def LoadNativeXML(self, filename):
        # also get rid of the old history
        if os.path.isfile(filename) == 0:
            pass
        else:
            # now start the XML processing
            self.ClearGrid()
            self.Freeze()
            xmldoc = minidom.parse(filename)
            datatags = xmldoc.getElementsByTagName('data')
            self.getData(datatags)
            deleteRowTags = xmldoc.getElementsByTagName('deleteRow')
            for i in range(len(deleteRowTags)):
                rownum = int(self.getText(deleteRowTags[i].childNodes))
                self.DeleteRows(rownum, 1)
            deleteColTags = xmldoc.getElementsByTagName('deleteColumn')
            for i in range(len(deleteColTags)):
                colnum = int(self.getText(deleteColTags[i].childNodes))
                self.DeleteCols(colnum, 1)
            appendRowTags = xmldoc.getElementsByTagName('appendRow')
            for i in range(len(appendRowTags)):
                rownum = int(self.getText(appendRowTags[i].childNodes))
                self.AppendRows()
            appendColTags = xmldoc.getElementsByTagName('appendColumn')
            for i in range(len(appendColTags)):
                colnum = int(self.getText(appendRowTags[i].childNodes))
                self.AppendCols()
            deleteColTags = xmldoc.getElementsByTagName('deleteColumn')
            for i in range(len(deleteColTags)):
                colnum = int(self.getText(deleteColTags[i].childNodes))
                self.DeleteCurrentCol(colnum)
            deleteRowTags = xmldoc.getElementsByTagName('deleteRow')
            for i in range(len(deleteRowTags)):
                rownum = int(self.getText(deleteRowTags[i].childNodes))
                self.DeleteCurrentRow(rownum)
            # there is a problem here - the html tags embedded between the <results> tags
            # are parsed as XML, but I want the whole lot available as a string.
            output.Addhtml('<P><B>SalStat Statistics</B></P>')
            output.htmlpage.WholeOutString = ''
            resultsTags = xmldoc.getElementsByTagName('results')
            for i in range(len(resultsTags)):
                outputText = self.getText(resultsTags[i].childNodes)
                #print "out" + outputText # debugging!
                output.Addhtml(outputText)
            #describeTags = xmldoc.getElementsByTagName('describe')
            #for i in range(len(describeTags)):
            self.Thaw()

    def LoadNumericData(self, event):
        default = inits.get('opendir')
        dlg = wx.FileDialog(self, "Load Data File", default,"","*.\
                                    dat|*.*", wx.OPEN)
        dlg.SetIcon(ico)
        if dlg.ShowModal() == wx.ID_OK:
            inits.update({'opendir': dlg.GetDirectory()})
            filename = dlg.GetPath()
            self.ClearGrid()
            # exception handler here!
            fin = open(filename, "r")
            p = pickle.Unpickler(fin)
            dataset = p.load()
            fin.close()
            # put dataset into grid

    def CleanRowData(self, row):
        indata = []
        for i in range(self.GetNumberCols()):
            datapoint = self.GetCellValue(row, i)
            if (datapoint != ''):
                value = float(datapoint)
                if (value != missingvalue):
                    indata.append(value)
        return indata

    # Routine to return a "clean" list of data from one column
    def CleanData(self, col):
        indata = []
        self.missing = 0
        for i in range(self.GetNumberRows()):
            datapoint = self.GetCellValue(i, col)
            if (datapoint != '') and (datapoint != '.'):
                try:
                    value = float(datapoint)
                    if (value != missingvalue):
                        indata.append(value)
                    else:
                        self.missing = self.missing + 1
                except ValueError:
                    pass
        return indata

    def GetColumnData(self, col):
        indata = []
        self.missing = 0
        for i in range(self.GetNumberRows()):
            val = self.GetCellValue(i, col)
            if val != "":
                if val != missingvalue:
                    try:
                        indata.append(float(val))
                    except ValueError:
                        indata.append(val)
                else:
                    self.missing += 1
        try:
            return numpy.array(indata)
        except TypeError:
            return indata

    def GetEntireDataSet(self, numcols):
        """Returns the data specified by a list 'numcols' in a Numpy
        array"""
        biglist = []
        for i in range(len(numcols)):
            smalllist = frame.grid.CleanData(numcols[i])
            biglist.append(smalllist)
        return numpy.array((biglist), numpy.Float)

#---------------------------------------------------------------------------
# DescChoice-wx.CheckListBox with list of descriptive stats in it
class DescChoiceBox(wx.CheckListBox):
    def __init__(self, parent, id):
        wx.CheckListBox.__init__(self, parent, -1, pos=(250,30), \
                                    size=(240,310), choices=DescList)

    def SelectAllDescriptives(self, event):
        for i in range(len(DescList)):
            self.Check(i, True)

    def SelectNoDescriptives(self, event):
        for i in range(len(DescList)):
            self.Check(i, False)

#---------------------------------------------------------------------------
# base class for getting number of columns/rows to add
class EditGridFrame(wx.Dialog):
    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, "Change Grid Size", \
                                    size=(205, 100+wind))
        self.SetIcon(ico)
        l1 = wx.StaticText(self, -1, 'Add Columns',pos=(10,15))
        l2 = wx.StaticText(self, -1, 'Add Rows',pos=(10,55))
        self.numnewcols = wx.SpinCtrl(self, -1, "", wx.Point(110,10), wx.Size(80,25))
        self.numnewcols.SetRange(0, 100)
        self.numnewcols.SetValue(0)
        self.numnewRows = wx.SpinCtrl(self, -1, "", wx.Point(110, 50), wx.Size(80,25))
        self.numnewRows.SetRange(0, 100)
        self.numnewRows.SetValue(0)
        okaybutton = wx.Button(self, 421, "Okay", wx.Point(10, 90),\
                                    wx.Size(BWidth, BHeight))
        cancelbutton = wx.Button(self, 422, "Cancel", wx.Point(110,90), \
                                    wx.Size(BWidth, BHeight))
        wx.EVT_BUTTON(self, 421, self.OkayButtonPressed)
        wx.EVT_BUTTON(self, 422, self.CancelButtonPressed)

    def OkayButtonPressed(self, event):
        colswanted = self.numnewcols.GetValue()
        rowswanted = self.numnewRows.GetValue()
        frame.grid.AddNCells(colswanted, rowswanted)
        self.Close(True)

    def CancelButtonPressed(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# grid preferences - set row & col sizes
class GridPrefs(wx.Dialog):
    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, "Cell Size", \
                                    size=(205,100+wind))
        self.SetIcon(ico)
        self.colwidth = wx.SpinCtrl(self, -1, "", wx.Point(110,10), wx.Size(80,25))
        self.colwidth.SetRange(1,200)
        self.colwidth.SetValue(frame.grid.GetDefaultColSize())
        self.rowheight= wx.SpinCtrl(self, -1, "", wx.Point(110,50), wx.Size(80,25))
        self.rowheight.SetRange(1,100)
        self.rowheight.SetValue(frame.grid.GetDefaultRowSize())
        l1 = wx.StaticText(self, -1, 'Column Width:',pos=(10,15))
        l2 = wx.StaticText(self, -1, 'Row Height:',pos=(10,55))
        okaybutton = wx.Button(self, 321, "Okay", wx.Point(10, 90), \
                                    wx.Size(BWidth, BHeight))
        cancelbutton = wx.Button(self, 322, "Cancel", wx.Point(110,90),\
                                    wx.Size(BWidth, BHeight))
        wx.EVT_BUTTON(self, 321, self.OkayButtonPressed)
        wx.EVT_BUTTON(self, 322, self.OnCloseGridPrefs)

    def OkayButtonPressed(self, event):
        frame.grid.SetDefaultColSize(self.colwidth.GetValue(), True)
        frame.grid.SetDefaultRowSize(self.rowheight.GetValue(), True)
        frame.grid.ForceRefresh()
        self.Close(True)

    def OnCloseGridPrefs(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# shows the scripting window for entering Python syntax commands
class ScriptFrame(wx.Frame):
    def __init__(self, parent, id):
        dimx = int(inits.get('scriptsizex'))
        dimy = int(inits.get('scriptsizey'))
        posx = int(inits.get('scriptposx'))
        posy = int(inits.get('scriptposy'))
        wx.Frame.__init__(self, parent, id, "Scripting Window", \
                                    size=(dimx, dimy), pos=(posx,posy))
        #set icon for frame (needs x-platform separator!
        self.SetIcon(ico)
        self.scripted = wx.Editor(self,-1)
        GoIcon = images.getApplyBitmap()
        OpenIcon = images.getOpenBitmap()
        SaveIcon = images.getSaveBitmap()
        SaveAsIcon = images.getSaveAsBitmap()
        PrintIcon = images.getPrintBitmap()
        CutIcon = images.getCutBitmap()
        CopyIcon = images.getCopyBitmap()
        PasteIcon = images.getPasteBitmap()
        HelpIcon = images.getHelpBitmap()
        toolBar = self.CreateToolBar(wx.TB_HORIZONTAL|wx.NO_BORDER| \
                                    wx.TB_3DBUTTONS|wx.TB_TEXT)
        toolBar.AddSimpleTool(710, GoIcon,"Run Script","Run the Script")
        toolBar.AddSimpleTool(711, OpenIcon,"Open","Open Script from a File")
        toolBar.AddSimpleTool(712, SaveIcon,"Save","Save Script to a file")
        toolBar.AddSimpleTool(713, SaveAsIcon,"Save As","Save Script under \
                                    a new filename")
        toolBar.AddSimpleTool(714, PrintIcon,"Print","Print Out Script")
        toolBar.AddSimpleTool(715, CutIcon, "Cut", "Cut selection to \
                                    clipboard")
        toolBar.AddSimpleTool(716, CopyIcon, "Copy", "Copy selection to \
                                    clipboard")
        toolBar.AddSimpleTool(717, PasteIcon, "Paste", "Paste selection \
                                    from clipboard")
        toolBar.AddSimpleTool(718, HelpIcon, "Help", "Get some help!")
        toolBar.SetToolBitmapSize((24,24))
        toolBar.Realize()
        wx.EVT_TOOL(self, 710, self.ExecuteScript)
        wx.EVT_TOOL(self, 711, self.OpenScript)
        wx.EVT_TOOL(self, 713, self.SaveScriptAs)
        wx.EVT_TOOL(self,715, self.CutSelection)
        wx.EVT_TOOL(self, 716, self.CopySelection)
        wx.EVT_TOOL(self, 717, self.PasteSelection)
        wx.EVT_TOOL(self, 718, self.ShowHelp)

    def ExecuteScript(self, event):
        mainscript = self.scripted.GetText()
        execscript = string.join(mainscript, '\n')
        exec(execscript)

    def CutSelection(self, event):
        self.scripted.OnCutSelection(event)

    def CopySelection(self, event):
        self.scripted.OnCopySelection(event)

    def PasteSelection(self, event):
        self.scripted.OnPaste(event)

    def ShowHelp(self, event):
        win = AboutFrame(frame, -1, 2)
        win.Show(True)

    # the open script method needs work
    def OpenScript(self, event):
        default = inits.get('opendir')
        dlg = wx.FileDialog(self, "Open Script File",default,"",\
                                    "Any (*)|*",wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            fin = file(filename, "r")
            TextIn = fin.readlines()
            
            self.scripted.SetText(TextIn)
            fin.close()

    def SaveScriptAs(self, event):
        default = inits.get('savedir')
        dlg = wx.FileDialog(self, "Save Script File", default,"",\
                                    "Any (*)|*", wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            fout = open(filename, "w")
            script = self.scripted.GetText()
            for i in range(len(script)):
                fout.write(script[i]+'\n')
            fout.close
#---------------------------------------------------------------------------
# Simply display the About box w/html frame in it
class AboutFrame(wx.Frame):
    def __init__(self, parent, id, tabnumber):
        dimx = int(inits.get('scriptsizex'))
        dimy = int(inits.get('scriptsizey'))
        posx = int(inits.get('scriptposx'))
        posy = int(inits.get('scriptposy'))
        wx.Frame.__init__(self, parent, id, "About SalStat", \
                                    size=(dimx, dimy), pos=(posx, posy))
        #set icon for frame (needs x-platform separator!
        self.SetIcon(ico)
        GoIcon = images.getApplyBitmap()

        BackIcon = images.getLeftBitmap()
        ForeIcon = images.getRightBitmap()
        HomeIcon = images.getHomeBitmap()
        toolBar = self.CreateToolBar(wx.TB_HORIZONTAL|wx.NO_BORDER| \
                                    wx.TB_3DBUTTONS)
        toolBar.AddSimpleTool(210, BackIcon, "Back","")
        toolBar.AddSimpleTool(211, ForeIcon, "Forward","")
        toolBar.AddSimpleTool(212, HomeIcon, "Home","")
        toolBar.SetToolBitmapSize((24,24))
        toolBar.Realize()
        self.SetToolBar(toolBar)
        self.tabs = wx.Notebook(self, -1)
        self.wizard = MyHtmlWindow(self.tabs, -1)
        self.topics = MyHtmlWindow(self.tabs, -1)
        self.scripting = MyHtmlWindow(self.tabs, -1)
        licence = MyHtmlWindow(self.tabs, -1)
        peeps = MyHtmlWindow(self.tabs, -1)
        self.tabs.AddPage(self.wizard, "Help Choosing a test!")
        self.wizard.LoadPage('help/wizard.html')
        self.tabs.AddPage(self.topics, "Topics")
        self.topics.LoadPage('help/index.html')
        self.tabs.AddPage(licence, "Licence")
        licence.LoadPage('help/COPYING')
        self.tabs.AddPage(peeps, "People")
        peeps.LoadPage('help/about.html')
        self.tabs.SetSelection(tabnumber)
        wx.EVT_TOOL(self, 210, self.GoBackPressed)
        wx.EVT_TOOL(self, 211, self.GoForwardPressed)
        wx.EVT_TOOL(self, 212, self.GoHomePressed)

    def GoBackPressed(self, event):
        pagenum = self.tabs.GetSelection()
        if (pagenum == 0):
            self.wizard.GoBack(event)
        if (pagenum == 1):
            self.topics.GoBack(event)

    def GoForwardPressed(self, event):
        pagenum = self.tabs.GetSelection()
        if (pagenum == 0):
            self.wizard.GoForward(event)
        if (pagenum == 1):
            self.topics.GoForward(event)

    def GoHomePressed(self, event):
        pagenum = self.tabs.GetSelection()
        if (pagenum == 0):
            self.wizard.LoadPage('wizard.html')
        if (pagenum == 1):
            self.topics.LoadPage('help/index.html')

    def OnCloseAbout(self, event):
        self.Close(True)

    def OnCloseWindow(self, event):
        self.Destroy()

#---------------------------------------------------------------------------
# user can change settings like variable names, decimal places, missing no.s
# using a SimpleGrid Need event handler - when new name entered, must be
#checked against others so no match each other

class VariablesFrame(wx.Dialog):
    def __init__(self,parent,id):
        wx.Dialog.__init__(self, parent,id,"SalStat - Variables", \
                                    size=(500,185+wind))
        #set icon for frame (needs x-platform separator!
        self.SetIcon(ico)
        okaybutton = wx.Button(self, 2001, "Okay",wx.Point(10,170),\
                                    wx.Size(BWidth, BHeight))
        cancelbutton = wx.Button(self, 2002, "Cancel",wx.Point(100,170),\
                                    wx.Size(BWidth, BHeight))
        self.vargrid = gridlib.Grid(self,-1,size=(480,130),pos=(10,10))
        self.vargrid.SetRowLabelSize(120)
        self.vargrid.SetDefaultRowSize(27, True)
        maxcols = frame.grid.GetNumberCols()
        self.vargrid.CreateGrid(3,maxcols)
        for i in range(maxcols):
            oldlabel = frame.grid.GetColLabelValue(i)
            self.vargrid.SetCellValue(0, i, oldlabel)
        self.vargrid.SetRowLabelValue(0,"Variable Name")
        self.vargrid.SetRowLabelValue(1,"Decimal Places")
        self.vargrid.SetRowLabelValue(2,"Missing Value")
        wx.EVT_BUTTON(self, 2001, self.OnOkayVariables)
        wx.EVT_BUTTON(self, 2002, self.OnCloseVariables)

    # this method needs to work out the other variables too
    def OnOkayVariables(self, event):
        for i in range(frame.grid.GetNumberCols()-1):
            newlabel = self.vargrid.GetCellValue(0, i)
            if (newlabel != ''):
                frame.grid.SetColLabelValue(i, newlabel)
            newsig = self.vargrid.GetCellValue(1, i)
            if (newsig != ''):
                try:
                    frame.grid.SetColFormatFloat(i, -1, int(newsig))
                except ZeroDivisionError:
                    pass
        frame.grid.ForceRefresh()
        self.Close(True)

    def OnCloseVariables(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# base html window class
class MyHtmlWindow(htmllib.HtmlWindow):
    def __init__(self, parent, id):
        htmllib.HtmlWindow.__init__(self, parent, id)
        wx.Image_AddHandler(wx.JPEGHandler()) # just in case!
        self.WholeOutString = ''
        self.Saved = True

    def Addhtml(self, htmlline):
        self.Saved = False
        self.AppendToPage(htmlline)
        self.WholeOutString = self.WholeOutString+htmlline + '\n'
        r = self.scroll.GetScrollRange(wx.VERTICAL)
        self.scroll.Scroll(0, r+10) 

    def write(self, TextIn):
        TextIn = '<br>'+TextIn
        self.Addhtml(TextIn)

    def LoadHtmlPage(self, event):
        dlg = wx.FileDialog(self, "Load Output File", "","","*.html|*.*", \
                                    wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            outputfilename = dlg.GetPath()
            self.LoadPage(outputfilename)
            inits.update({'opendir': dlg.GetDirectory()})

    def SaveHtmlPage(self, event):
        dlg = wx.FileDialog(self, "Save Output","","","*.html|*>*",wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            outputfilename = dlg.GetPath()
            fout = open(outputfilename, "w")
            fout.write(self.WholeOutString)
            fout.close()
            inits.update({'savedir': dlg.GetDirectory()})
            self.Saved = True

    def PrintHtmlPage(self, event):
        dlg = wx.PrintDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            null

    def GoBack(self, event):
        if self.HistoryCanBack():
            self.HistoryBack()

    def GoForward(self, event):
        if self.HistoryCanForward():
            self.HistoryForward()

#---------------------------------------------------------------------------
# output window w/html class for output. Also has status bar and menu.Opens
# in new frame
class OutputSheet(wx.Frame):
    def __init__(self, parent, id):
        dimx = int(inits.get('outputsizex'))
        dimy = int(inits.get('outputsizey'))
        posx = int(inits.get('outputposx'))
        posy = int(inits.get('outputposy'))
        wx.Frame.__init__(self, parent, -1, "SalStat Statistics - Output", \
                                    size=(dimx, dimy), pos=(posx, posy))
        #set icon for frame (needs x-platform separator!
        #icon = images.getIconIcon()
        self.SetIcon(ico)
        self.WholeOutString = CreateHTMLDoc()
        file_menu = wx.Menu()
        edit_menu = wx.Menu()
        pref_menu = wx.Menu()
        help_menu = wx.Menu()
        file_menu.Append(ID_OFILE_NEW, '&New\tCTRL+N')
        file_menu.Append(ID_OFILE_OPEN, '&Open...\tCTRL+O')
        file_menu.Append(ID_OFILE_SAVE, '&Save\tCTRL+S')
        file_menu.Append(ID_OFILE_SAVEAS, 'Save &As...\tSHIFT+CTRL+S')
        file_menu.Append(ID_OFILE_PRINT, '&Print...\tCTRL+P')
        file_menu.Append(ID_OFILE_CLOSE, '&Close\tCTRL+Q')
        edit_menu.Append(ID_OEDIT_CUT, 'Cu&t\tCTRL+X')
        edit_menu.Append(ID_OEDIT_COPY, '&Copy\tCTRL+C')
        edit_menu.Append(ID_OEDIT_PASTE, '&Paste\tCTRL+V')
        edit_menu.Append(ID_OEDIT_SELECTALL, 'Select &All\tCTRL+A')
        help_menu.Append(ID_HELP_WIZARD, '&What Test Should I Use...')
        help_menu.Append(ID_HELP_TOPICS, '&Topics...')
        help_menu.Append(ID_HELP_LICENCE, '&Licence...')
        help_menu.Append(wx.ID_ABOUT, '&About...')
        omenuBar = wx.MenuBar()
        omenuBar.Append(file_menu, '&File')
        omenuBar.Append(edit_menu, '&Edit')
        omenuBar.Append(pref_menu, '&Pref')
        omenuBar.Append(help_menu, '&Help')
        self.SetMenuBar(omenuBar)
        #wx.InitAllImageHandlers()
        NewIcon = images.getNewBitmap()
        OpenIcon = images.getOpenBitmap()
        SaveAsIcon = images.getSaveAsBitmap()
        PrintIcon = images.getPrintBitmap()
        HelpIcon = images.getHelpBitmap()
        toolBar = self.CreateToolBar(wx.TB_HORIZONTAL|wx.NO_BORDER| \
                                    wx.TB_3DBUTTONS|wx.TB_TEXT)
        toolBar.AddSimpleTool(401, NewIcon,"New","New Data Sheet in \
                                    separate window")
        toolBar.AddSimpleTool(402, OpenIcon,"Open","Open Data from a File")
        toolBar.AddSimpleTool(403, SaveAsIcon,"Save As","Save Data under \
                                    a new filename")
        toolBar.AddSimpleTool(404, PrintIcon,"Print","Print Out Results")
        toolBar.AddSimpleTool(405, HelpIcon, "Help", "Get some help!")
        toolBar.SetToolBitmapSize((24,24))
        # more toolbuttons are needed: New Output, Save, Print, Cut, \
        # Variables, and Wizard creates the toolbar
        toolBar.Realize()
        self.SetToolBar(toolBar)
        self.CreateStatusBar()
        self.SetStatusText('Salstat statistics - results')
        self.htmlpage = html2lib.WebView.New(self)
        self.htmlpage.SetEditable(True)
        self.Addhtml('')
        self.printer = wx.Printout()
        wx.EVT_MENU(self, ID_OEDIT_CUT, self.CutHTML)
        wx.EVT_MENU(self, ID_OEDIT_COPY, self.CopyHTML)
        wx.EVT_MENU(self, ID_OEDIT_PASTE, self.PasteHTML)
        wx.EVT_MENU(self, ID_OFILE_SAVEAS, self.SaveHtmlPage)
        wx.EVT_CLOSE(self, self.DoNothing)
        wx.EVT_MENU(self, ID_OFILE_NEW, self.ClearAll)
        wx.EVT_MENU(self, ID_OFILE_PRINT, self.PrintOutput)
        wx.EVT_MENU(self, ID_OFILE_OPEN, self.LoadHtmlPage)
        wx.EVT_MENU(self, wx.ID_ABOUT, frame.GoHelpAboutFrame)
        wx.EVT_MENU(self, ID_HELP_WIZARD, frame.GoHelpWizardFrame)
        wx.EVT_MENU(self, ID_HELP_TOPICS, frame.GoHelpTopicsFrame)
        wx.EVT_MENU(self, ID_HELP_LICENCE, frame.GoHelpLicenceFrame)
        wx.EVT_TOOL(self, 401, self.ClearAll)
        wx.EVT_TOOL(self, 402, self.LoadHtmlPage)
        wx.EVT_TOOL(self, 403, self.SaveHtmlPage)
        wx.EVT_TOOL(self, 404, self.htmlpage.Print)
        wx.EVT_TOOL(self, 405, frame.GoHelpTopicsFrame)

    def CutHTML(self, arg):
        self.htmlpage.Cut()

    def CopyHTML(self, arg):
        self.htmlpage.Copy()

    def PasteHTML(self, arg):
        self.htmlpage.Paste()

    def LoadHtmlPage(self, event):
        dlg = wx.FileDialog(self, "Load Output File", "","","*.html|*.*", \
                            wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            inputfilename = dlg.GetPath()
            fin = open(inputfilename, 'r')
            data = fin.read()
            fin.close()
            self.htmlpage.SetPage(data,"")
            inits.update({'opendir': dlg.GetDirectory()})
    
    def SaveHtmlPage(self):
        dlg = wx.FileDialog(self, "Save Output","","","*.html|*>*", \
                            wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            outputfilename = dlg.GetPath()
            fout = open(outputfilename, "w")
            fout.write(self.WholeOutString)
            fout.close()
            inits.update({'savedir': dlg.GetDirectory()})
            self.Saved = True

    def Addhtml(self, htmlline):
        self.WholeOutString = self.WholeOutString + htmlline
        htmlend = "\n\t</body>\n<html>"
        self.htmlpage.SetPage(self.WholeOutString+htmlend,"")
        #r = self.scroll.GetScrollRange(wx.VERTICAL)
        #self.scroll.Scroll(0, r+10) 

    def PrintOutput(self, event):
        data = wx.PrintDialogData()
        data.EnablePrintToFile(True)
        data.EnablePageNumbers(True)
        data.EnableSelection(True)
        dlg = wx.PrintDialog(output, data)
        if dlg.ShowModal() == wx.ID_OK:
            #print out html
            self.printer.PrintText(self.htmlpage.WholeOutString)
        dlg.Destroy()

    def DoNothing(self, event):
        pass

    def ClearAll(self, event):
        # check output has been saved
        self.htmlpage.WholeOutString = CreateHTMLDoc()
        htmlend = "\n\t</body>\n</html>"
        self.htmlpage.SetPage(self.WholeOutString+htmlend,"")

#---------------------------------------------------------------------------
# user selects which cols to analyse, and what stats to have
class DescriptivesFrame(wx.Dialog):
    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, \
                                    "Descriptive Statistics", \
                                    size=(500,400+wind))
        x = self.GetClientSize()
        winheight = x[1]
        self.SetIcon(ico)
        ColumnList, self.colnums  = frame.grid.GetUsedCols()
        # ColumnList is the col headings, colnums is the column numbers
        l0 = wx.StaticText(self,-1,"Select Column(s) to Analyse",pos=(10,10))
        l4 = wx.StaticText(self,-1,"Select Descriptive Statistics",pos=(250,10))
        self.DescChoice = DescChoiceBox(self, 1107)
        self.ColChoice = wx.CheckListBox(self,1102, wx.Point(10,30), \
                                    wx.Size(230,(winheight * 0.8)), ColumnList)
        okaybutton = wx.Button(self,1103,"Okay",wx.Point(10,winheight-35),\
                                    wx.Size(BWidth, BHeight))
        cancelbutton = wx.Button(self,1104,"Cancel",wx.Point(100,winheight-35),\
                                    wx.Size(BWidth, BHeight))
        if wx.Platform == '__WXMSW__':
            # Darn! Some cross-platform voodoo needed...
            allbutton = wx.Button(self, 105, "Select All", wx.Point(250,winheight-70),\
                                    wx.Size(BWidth, BHeight))
            nonebutton = wx.Button(self, 106, "Select None", wx.Point(360,winheight-70),\
                                    wx.Size(BWidth, BHeight))
        else:
            allbutton = wx.Button(self, 105, "Select All", wx.Point(250,winheight-50),\
                                    wx.Size(BWidth, BHeight))
            nonebutton = wx.Button(self, 106, "Select None", wx.Point(360,winheight-50),\
                                    wx.Size(BWidth, BHeight))
        wx.EVT_BUTTON(okaybutton, 1103, self.OnOkayButton)
        wx.EVT_BUTTON(cancelbutton, 1104, self.OnCloseContDesc)
        wx.EVT_BUTTON(allbutton, 105, self.DescChoice.SelectAllDescriptives)
        wx.EVT_BUTTON(nonebutton, 106, self.DescChoice.SelectNoDescriptives)

    def OnOkayButton(self, event):
        descs = []
        for i in range(len(self.colnums)):
            if self.ColChoice.IsChecked(i):
                colnum = self.colnums[i]
                name = frame.grid.GetColLabelValue(colnum)
                descs.append(salstat_stats.FullDescriptives( \
                                    frame.grid.CleanData(colnum), name, \
                                    frame.grid.missing))
        ManyDescriptives(self, descs)
        self.Close(True)

    def OnCloseContDesc(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# Same as DescriptivesContinuousFrame, but for nominal descriptives
class OneConditionTestFrame(wx.Dialog):
    def __init__(self, parent, id, ColumnList):
        wx.Dialog.__init__(self, parent, id, "One Condition Tests", \
                          size=(500,400+wind))
        x = self.GetClientSize()
        winheight = x[1]
        self.SetIcon(ico)
        ColumnList, self.colnums = frame.grid.GetUsedCols()
        self.ColBox = wx.Choice(self, 101,(10,30), (110,20), choices = ColumnList)
        self.ColBox.SetSelection(0)
        cID = wx.NewId()
        l0 = wx.StaticText(self,-1,"Select Column to Analyse",pos=(10,10))
        l1 = wx.StaticText(self,-1,"Choose Test(s):", pos=(10,60))
        if wx.Platform == '__WXMSW__':
            l3a = wx.StaticText(self,-1,'User Hypothesised', pos=(10,335))
            l3b = wx.StaticText(self,-1,'Mean:',pos=(10,352))
            self.UserMean = wx.TextCtrl(self,219,pos=(140,345),size=(70,20))
            allbutton = wx.Button(self, 105, "Select All", wx.Point(250,winheight-70),\
                                    wx.Size(BWidth, BHeight))
            nonebutton = wx.Button(self, 106, "Select None", wx.Point(360,winheight-70),\
                                    wx.Size(BWidth, BHeight))
        else:
            l3a = wx.StaticText(self,-1,'User Hypothesised', pos=(10,325))
            l3b = wx.StaticText(self,-1,'Mean:',pos=(10,342))
            self.UserMean = wx.TextCtrl(self,219,pos=(140,335),size=(70,20))
            allbutton = wx.Button(self, 105, "Select All", wx.Point(250,winheight-50),\
                                    wx.Size(BWidth, BHeight))
            nonebutton = wx.Button(self, 106, "Select None", wx.Point(360,winheight-50),\
                                    wx.Size(BWidth, BHeight))
        l4 = wx.StaticText(self,-1,"Select Descriptive Statistics",pos=(250,10))
        Tests = ['t-test','Sign test','Chi square test for variance']
        self.TestChoice = wx.CheckListBox(self,213,wx.Point(10,80),\
                                    wx.Size(230,180),Tests)
        self.hypchoice=wx.RadioBox(self, 205,"Select Hypothesis",\
                                    wx.Point(10,270),wx.DefaultSize,HypList)
        self.hypchoice.SetSelection(1)
        self.okaybutton = wx.Button(self,103,"Okay",wx.Point(10,winheight-35),\
                                    wx.Size(BWidth, BHeight))
        #self.okaybutton.Enable(False)
        cancelbutton = wx.Button(self,104,"Cancel",wx.Point(100,winheight-35),\
                                    wx.Size(BWidth, BHeight))
        self.DescChoice = DescChoiceBox(self, 104)
        wx.EVT_BUTTON(self.okaybutton, 103, self.OnOkayButton)
        wx.EVT_BUTTON(cancelbutton, 104, self.OnCloseOneCond)
        wx.EVT_BUTTON(allbutton, 105, self.DescChoice.SelectAllDescriptives)
        wx.EVT_BUTTON(nonebutton, 106, self.DescChoice.SelectNoDescriptives)
        # enable the okay button if something is entered as a hyp mean.
        # Can the wx.TextCtrl allow only numbers to be entered?
        #wx.EVT_TEXT(self.UserMean, 107, self.EnteredText) # doesn't work on Windows!

    def EnteredText(self, event):
        self.okaybutton.Enable(True)

    def OnOkayButton(self, event):
        x1 = self.ColBox.GetSelection()
        name = frame.grid.GetColLabelValue(x1)
        if (x1 < 0): # add top limits of grid to this
            self.Close(True)
            return
        try:
            umean = float(self.UserMean.GetValue())
        except:
            output.Addhtml('<p class="text-warning">Cannot do test - no user \
                                    hypothesised mean specified')
            self.Close(True)
            return
        x = frame.grid.CleanData(x1)
        TBase = salstat_stats.OneSampleTests(frame.grid.CleanData(x1), name, \
                                    frame.grid.missing)
        d=[0]
        d[0] = TBase.d1
        x2=ManyDescriptives(self, d)
        # One sample t-test
        if self.TestChoice.IsChecked(0):
            output.Addhtml('<h3>One sample t-test</h3>')
            TBase.OneSampleTTest(umean)
            if (TBase.prob == -1.0):
                output.Addhtml('<p class="text-warning">All elements are the same, \
                                    test not possible</p>')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                vars = [['Variable', name1],
                        ['df', TBase.df],
                        ['t',TBase.t],
                        ['p',TBase.prob]]
                ln = tabler.table(vars)
                output.Addhtml(ln)
                #now draw up the xml history stuff
                xmlevt = '<analyse test="one sample t-test" column = "'+str(x1)
                xmlevt = xmlevt+' hyp_value = "'+str(umean)+'" tail="'
                if (self.hypchoice.GetSelection() == 0):
                    xmlevt = xmlevt+'1">'
                else:
                    xmlevt = xmlevt+'2">'
                xmlevt = xmlevt+'t ('+str(TBase.df)+') = '+str(TBase.t)+', p = '+str(TBase.prob)
                xmlevt = xmlevt+'</analyse>'
                hist.AppendEvent(xmlevt)
        # One sample sign test
        if self.TestChoice.IsChecked(1):
            output.Addhtml('<H3>One sample sign test</H3>')
            TBase.OneSampleSignTest(x, umean)
            if (TBase.prob == -1.0):
                output.Addhtml('<p class="text-warning">All data are the same - no \
                                    analysis is possible</p>')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                vars = [['Variable', name1],
                        ['Total N', TBase.ntotal],
                        ['Z',TBase.z],
                        ['p',TBase.prob]]
                ln = tabler.table(vars)
                output.Addhtml(ln)
        # chi square test for variance
        if self.TestChoice.IsChecked(2):
            output.Addhtml('<H3>One sample chi square</H3>')
            TBase.ChiSquareVariance(umean)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            if (TBase.prob == None):
                TBase.prob = 1.0
                vars = [['Variable', name1],
                        ['df', TBase.df],
                        ['Chi',TBase.chisquare],
                        ['p',TBase.prob]]
                ln = tabler.table(vars)
                output.Addhtml(ln)

        self.Close(True)
            
    def OnCloseOneCond(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
#dialog for 2 sample tests
class TwoConditionTestFrame(wx.Dialog):
    def __init__(self, parent, id, ColumnList):
        wx.Dialog.__init__(self, parent, id, "Two Condition Tests", \
                                    size=(500,400+wind))
        #set icon for frame (needs x-platform separator!
        x = self.GetClientSize()
        winheight = x[1]
        x = self.GetClientSize()
        self.SetIcon(ico)
        colsselected =  frame.grid.GetColsUsedList()
        l0 = wx.StaticText(self,-1,"Select Columns to Analyse",pos=(10,10))
        l1 = wx.StaticText(self, -1, "Select Test(s) to Perform:", pos=(10,60))
        if wx.Platform == '__WXMSW__':
            l3a = wx.StaticText(self,-1,'User Hypothesised', pos=(10,335))
            l3b = wx.StaticText(self,-1,'Mean:',pos=(10,352))
            self.UserMean = wx.TextCtrl(self,219,pos=(140,345),size=(70,20))
            allbutton = wx.Button(self, 218, "Select All", wx.Point(250,winheight-70),\
                                    wx.Size(BWidth, BHeight))
            nonebutton = wx.Button(self, 220, "Select None", wx.Point(360,winheight-70),\
                                    wx.Size(BWidth, BHeight))
        else:
            l3a = wx.StaticText(self,-1,'User Hypothesised', pos=(10,325))
            l3b = wx.StaticText(self,-1,'Mean:',pos=(10,342))
            self.UserMean = wx.TextCtrl(self,219,pos=(140,335),size=(70,20))
            allbutton = wx.Button(self, 218, "Select All", wx.Point(250,winheight-50),\
                                    wx.Size(BWidth, BHeight))
            nonebutton = wx.Button(self, 220, "Select None", wx.Point(360,winheight-50),\
                                    wx.Size(BWidth, BHeight))
        l4 = wx.StaticText(self,-1,"Select Descriptive Statistics",pos=(250,10))
        self.ColBox1 = wx.Choice(self,211, (10,30), (110,20), ColumnList)
        self.ColBox2 = wx.Choice(self,212, (130,30), (110,20), ColumnList)
        x1 = 0
        x2 = 1
        self.ColBox1.SetSelection(x1)
        self.ColBox2.SetSelection(x2)
        x1len = len(frame.grid.CleanData(x1))
        x2len = len(frame.grid.CleanData(x2))
        if (x1len != x2len):
            self.equallists = False
        else:
            self.equallists = True
        # list of tests in alphabetical order
        Tests = ['chi square','F test','Kolmogorov-Smirnov', \
                'Linear Regression', 'Mann-Whitney U', \
                'Paired Sign', 't-test paired','t-test unpaired', \
                'Wald-Wolfowitz Runs', 'Wilcoxon Rank Sums', \
                'Wilcoxon Signed Ranks'] # nb, paired permutation test missing
        self.paratests = wx.CheckListBox(self,213,wx.Point(10,80),\
                                    wx.Size(230,180),Tests)
        self.hypchoice=wx.RadioBox(self, 205,"Select Hypothesis",\
                                    wx.Point(10,270),wx.DefaultSize,HypList)
        self.hypchoice.SetSelection(1)
        self.DescChoice = DescChoiceBox(self, 215)
        okaybutton = wx.Button(self,216,"Okay",wx.Point(10,winheight-35), \
                                    wx.Size(BWidth, BHeight))
        cancelbutton = wx.Button(self,217,"Cancel",wx.Point(100,winheight-35), \
                                    wx.Size(BWidth, BHeight))
        self.UserMean = wx.TextCtrl(self,219,pos=(140,345),size=(70,20))
        # using self.equallists, if True, enable all items in the checklist \
        # box, otherwise set the within subs and correlations to be
        # disabled as they cannot be used with unequal list lengths!
        # Also disble the f-test unless something is entered into the
        # user hyp variance box
        wx.EVT_BUTTON(okaybutton, 216, self.OnOkayButton)
        wx.EVT_BUTTON(cancelbutton, 217, self.OnCloseTwoCond)
        wx.EVT_BUTTON(allbutton, 218, self.DescChoice.SelectAllDescriptives)
        wx.EVT_BUTTON(nonebutton, 220, self.DescChoice.SelectNoDescriptives)
        #wx.EVT_CHOICE(self.ColBox1, 211, self.ChangeCol1)
        #wx.EVT_CHOICE(self.ColBox2, 212, self.ChangeCol1)
        wx.EVT_TEXT(self.UserMean, 219, self.ChangeText)

    def ChangeText(self, event):
        pass

    def ChangeCol1(self, event):
        # check that len of 2 cols is equal, if not disable choices of test
        x1 = len(frame.grid.CleanData(self.ColBox1.GetSelection()))
        x2 = len(frame.grid.CleanData(self.ColBox2.GetSelection()))
        if (x1 != x2):
            # disable some tests in the listbox
            self.paratests.Check(0,False)
        else:
            pass
            # enable all tests in the listbox

    def ChangeCol2(self, event):
        # check that len of 2 cols is equal, if not disable choices of test
        x1 = len(frame.grid.CleanData(self.ColBox1.GetSelection()))
        x2 = len(frame.grid.CleanData(self.ColBox2.GetSelection()))
        if (x1 != x2):
            pass
        else:
            pass

    def OnOkayButton(self, event):
        x1 = self.ColBox1.GetSelection()
        y1 = self.ColBox2.GetSelection()
        name1 = frame.grid.GetColLabelValue(x1)
        name2 = frame.grid.GetColLabelValue(y1)
        if (x1 < 0) or (y1 < 0):
            self.Close(True)
            return
        x = frame.grid.CleanData(x1)
        xmiss = frame.grid.missing
        y = frame.grid.CleanData(y1)
        ymiss = frame.grid.missing
        TBase = salstat_stats.TwoSampleTests(x, y, name1, name2,xmiss,ymiss)
        d = [0,0]
        d[0] = TBase.d1
        d[1] = TBase.d2
        x2 = ManyDescriptives(self, d)

        # chi square test
        if self.paratests.IsChecked(0):
            output.Addhtml('<H3>Chi square</H3>')
            TBase.ChiSquare(x, y)
            if (TBase.prob == -1.0):
                output.Addhtml('<p class="text-warning">Cannot do chi square - unequal data sizes</p>')
            else:
                vars = [['Variable 1', name1],
                        ['Variable 2', name2],
                        ['df', TBase.df],
                        ['Chi',TBase.chisq],
                        ['p',TBase.prob]]
                ln = tabler.table(vars)
                output.Addhtml(ln)

        # F-test for variance ratio's
        if self.paratests.IsChecked(1):
            output.Addhtml('<H3>F test for variance ratio (independent samples)</H3>')
            try:
                umean = float(self.UserMean.GetValue())
            except:
                output.Addhtml('<p class="text-warning">Cannot do test - no user \
                                    hypothesised mean specified')
            else:
                TBase.FTest(umean)
                if (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                vars = [['Variable 1', name1],
                        ['Variable 2', name2],
                        ['df', '%d, %d'%(TBase.df1, TBase.df2)],
                        ['F',TBase.f],
                        ['p',TBase.prob]]
                ln = tabler.table(vars)
                output.Addhtml(ln)

        # Kolmorogov-Smirnov 2 sample test
        if self.paratests.IsChecked(2):
            output.Addhtml('<h3>Kolmogorov-Smirnov test (unpaired)</h3>')
            TBase.KolmogorovSmirnov()
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            vars = [['Variable 1', name1],
                    ['Variable 2', name2],
                    ['d', TBase.d],
                    ['p',TBase.prob]]
            ln = tabler.table(vars)
            output.Addhtml(ln)

        # Linear Regression
        if self.paratests.IsChecked(3):
            output.Addhtml('<h3>Linear Regression</h3>')
            TBase.LinearRegression(x,y)
            #s, i, r, prob, st = salstat_stats.llinregress(x, y)
            if (TBase.prob == -1.0):
                output.Addhtml('<h3>Cannot do linear regression - unequal data sizes</p>')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    self.prob = self.prob / 2
                vars = [['Variable 1 on', name1],
                        ['Variable 2', name2],
                        ['Slope', TBase.slope],
                        ['Intercept',TBase.intercept],
                        ['R', TBase.r],
                        ['Est. Standard Error',TBase.sterrest],
                        ['df', TBase.df],
                        ['t',TBase.t],
                        ['p',TBase.prob]]
                ln = tabler.table(vars)
                output.Addhtml(ln)

        # Mann-Whitney U
        if self.paratests.IsChecked(4):
            output.Addhtml('<h3>Mann-Whitney U test (unpaired samples)</h3>')
            TBase.MannWhitneyU(x, y)
            if (TBase.prob == -1.0):
                output.Addhtml('<p class="text-warning">Cannot do Mann-Whitney U test - all numbers are identical<p>')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                vars = [['Variable 1', name1],
                        ['Variable 2', name2],
                        ['df', TBase.z],
                        ['Small U',TBase.smallu],
                        ['Big U',TBase.bigu],
                        ['p',TBase.prob]]
                ln = tabler.table(vars)
                output.Addhtml(ln)

        # Paired permutation test
        """if self.paratests.IsChecked(5):
            output.Addhtml('<P><B>Paired Permutation test</B></P>')
            TBase.PairedPermutation(x, y)
            if (TBase.prob == -1.0):
                output.Addhtml('<BR>Cannot do test - not paired \
                                    samples')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                output.Addhtml('<BR>Utail = %5.0f, nperm = %5.3f, \
                        crit = %5.3f, p = %1.6f'%(TBase.utail, TBase.nperm, \
                        TBase.crit, TBase.prob))"""

        # Paired sign test
        if self.paratests.IsChecked(5):
            output.Addhtml('<h3>Paired sign test</h3>')
            TBase.TwoSampleSignTest(x, y)
            if (TBase.prob == -1.0):
                output.Addhtml('<p class="text-warning">Cannot do test - not paired samples</p>')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                vars = [['Variable 1', name1],
                        ['Variable 2', name2],
                        ['N (total)', TBase.ntotal],
                        ['Z',TBase.z],
                        ['p',TBase.prob]]
                ln = tabler.table(vars)
                output.Addhtml(ln)

        # Paired t-test
        if self.paratests.IsChecked(6):
            output.Addhtml('<h3>t-test paired</h3>')
            TBase.TTestPaired(x, y)
            if (TBase.prob == -1.0):
                output.Addhtml('<p class="text-warning">Cannot do paired t test - unequal data sizes</p>')
            else:
                if self.hypchoice.GetSelection() == 0:
                    TBase.prob = TBase.prob / 2
                vars = [['Variable 1', name1],
                        ['Variable 2', name2],
                        ['df', TBase.df],
                        ['t',TBase.t],
                        ['p',TBase.prob]]
                ln = tabler.table(vars)
                output.Addhtml(ln)

        # unpaired t-test
        if self.paratests.IsChecked(7):
            output.Addhtml('<h3>t-test unpaired</h3>')
            TBase.TTestUnpaired()
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            vars = [['Variable 1', name1],
                    ['Variable 2', name2],
                    ['df', TBase.df],
                    ['t',TBase.t],
                    ['p',TBase.prob]]
            ln = tabler.table(vars)
            output.Addhtml(ln)

        # Wald-Wolfowitz runs test (no yet coded)
        if self.paratests.IsChecked(8):
            pass

        # Wilcoxon Rank Sums
        if self.paratests.IsChecked(9):
            output.Addhtml('<h3>Rank Sums test (unpaired samples)</h3>')
            TBase.RankSums(x, y)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            vars = [['Variable 1', name1],
                    ['Variable 2', name2],
                    ['z', TBase.z],
                    ['p',TBase.prob]]
            ln = tabler.table(vars)
            output.Addhtml(ln)
            output.Addhtml('<BR>t = %5.3f, p = %1.6f'%(TBase.z, \
                                    TBase.prob))

        # Wilcoxon Signed Ranks
        if self.paratests.IsChecked(10):
            output.Addhtml('<h3>Wilcoxon t (paired samples)</h3>')
            TBase.SignedRanks(x, y)
            if (TBase.prob == -1.0):
                output.Addhtml('<p class="text-warning">Cannot do Wilcoxon t test - unequal data sizes</p>')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                vars = [['Variable 1', name1],
                        ['Variable 2', name2],
                        ['z', TBase.z],
                        ['wt',TBase.wt],
                        ['p',TBase.prob]]
                ln = tabler.table(vars)
                output.Addhtml(ln)
        self.Close(True)

    def OnCloseTwoCond(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# dialog for single factor tests with 3+ conditions
class ThreeConditionTestFrame(wx.Dialog):
    def __init__(self, parent, id, ColumnList):
        wx.Dialog.__init__(self, parent, id, "Three Condition Tests", \
                                    size = (500,400+wind))
        x = self.GetClientSize()
        winheight = x[1]
        self.SetIcon(ico)
        alltests = ['anova between subjects','anova within subjects',\
                                    'Kruskall Wallis','Friedman test',\
                                    'Cochranes Q']
        ColumnList, self.colnums = frame.grid.GetUsedCols()
        l0 = wx.StaticText(self,-1,"Select Columns to Analyse",pos=(10,10))
        #l1 = wx.StaticText(self, -1, "Select IV:", pos=(10,60))
        l2 = wx.StaticText(self, -1, "Select Data", pos=(10,170))
        l4 = wx.StaticText(self,-1,"Select Descriptive Statistics",pos=(250,10))
        if wx.Platform == '__WXMSW__':
            allbutton = wx.Button(self, 518, "Select All", wx.Point(250,winheight-70),\
                                    wx.Size(BWidth, BHeight))
            nonebutton = wx.Button(self, 520, "Select None", wx.Point(360,winheight-70),\
                                    wx.Size(BWidth, BHeight))
        else:
            allbutton = wx.Button(self, 518, "Select All", wx.Point(250,winheight-50),\
                                    wx.Size(BWidth, BHeight))
            nonebutton = wx.Button(self, 520, "Select None", wx.Point(360,winheight-50),\
                                    wx.Size(BWidth, BHeight))

        self.TestChoice = wx.CheckListBox(self, 514,wx.Point(10,190), \
                                    wx.Size(230,120),alltests)
        self.hypchoice=wx.RadioBox(self, 205,"Select Hypothesis",\
                                    wx.Point(10,320),wx.DefaultSize,HypList)
        self.hypchoice.SetSelection(1)
        self.ColChoice = wx.CheckListBox(self,511, wx.Point(10,30), \
                                    wx.Size(230,130), ColumnList)
        for i in range(len(self.colnums)):
            self.ColChoice.Check(i, True)
        self.DescChoice = DescChoiceBox(self, 512)
        okaybutton = wx.Button(self,516,"Okay",wx.Point(10,winheight-35), \
                                    wx.Size(BWidth, BHeight))
        cancelbutton = wx.Button(self,517,"Cancel",wx.Point(100,winheight-35), \
                                    wx.Size(BWidth, BHeight))
        wx.EVT_BUTTON(okaybutton, 516, self.OnOkayButton)
        wx.EVT_BUTTON(cancelbutton, 517, self.OnCloseThreeCond)
        wx.EVT_BUTTON(allbutton, 518, self.DescChoice.SelectAllDescriptives)
        wx.EVT_BUTTON(nonebutton, 520, self.DescChoice.SelectNoDescriptives)

    def OnOkayButton(self, event):
        biglist = []
        ns = []
        sums = []
        means = []
        names = []
        miss = []
        k = 0
        for i in range(len(self.colnums)):
            if self.ColChoice.IsChecked(i):
                k = k + 1
                tmplist = frame.grid.CleanData(self.colnums[i])
                miss.append(frame.grid.missing)
                biglist.append(tmplist)
                names.append(frame.grid.GetColLabelValue(i))
        k = len(biglist)
        d = []
        for i in range(k):
            x2=salstat_stats.FullDescriptives(biglist[i], names[i], miss[i])
            ns.append(x2.N)
            sums.append(x2.sum)
            means.append(x2.mean)
            d.append(x2)
        x2=ManyDescriptives(self, d)
        if (len(biglist) < 2):
            output.Addhtml('<p><b>Not enough columns selected for \
                                    test!</b>')
            self.Close(True)
            return
        TBase = salstat_stats.ThreeSampleTests()
        #single factor between subjects anova
        if self.TestChoice.IsChecked(0):
            cols = []
            output.Addhtml('<P><B>Single Factor anova - between \
                                    subjects</B></P>')
            output.Addhtml('<P><i>Warning!</i> This test is based \
                                    on the following assumptions:')
            output.Addhtml('<P>1) Each group has a normal \
                                    distribution of observations')
            output.Addhtml('<P>2) The variances of each observation \
                                    are equal across groups (homogeneity of \
                                    variance)')
            output.Addhtml('<P>3) The observations are statistically \
                                    independent')
            TBase.anovaBetween(d)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            output.Addhtml('<table class="table table-striped" border="1"><tr><td></td><td>SS \
                                    </td><td>df</td><td>MS</td><td>F</td>  \
                                    <td>p-value</TD></tr>')
            output.Addhtml('<tr><td>FACTOR</td><td>%5.3f</td><td> \
                                    %5d</td><td>%5.3f</td><td>%5.3f</td>   \
                                    <td>%1.6f</td></tr>'%(TBase.SSbet,     \
                                    TBase.dfbet, TBase.MSbet, TBase.F,\
                                    TBase.prob))
            output.Addhtml('<tr><td>Error</td><td>%5.3f</td><td>  \
                                    %5d</td><td>%5.3f</td><td></td><td>    \
                                    </td></tr>'%(TBase.SSwit, TBase.dferr, \
                                    TBase.MSerr))
            output.Addhtml('<tr><td>Total</td><td>%5.3f</td><td>  \
                                    %5d</td><td></td><td></td><td></td></tr>\
                                    </table>'%(TBase.SStot, TBase.dftot))
        # single factor within subjects anova
        if self.TestChoice.IsChecked(1):
            output.Addhtml('<P><B>Single Factor anova - within  \
                                    subjects</b></P>')
            output.Addhtml('<P><i>Warning!</i> This test is based \
                                    on the following assumptions:')
            output.Addhtml('<P>1) Each group has a normal \
                                    distribution of observations')
            output.Addhtml('<P>2) The variances of each observation \
                                    are equal across groups (homogeneity of \
                                    variance)')
            output.Addhtml('<P>3) The observations are statistically \
                                    indpendent')
            output.Addhtml('<P>4) The variances of each participant \
                                    are equal across groups (homogeneity of \
                                    covariance)')
            TBase.anovaWithin(biglist, ns, sums, means)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            output.Addhtml('<table class="table table-striped" border="1"><tr><td></td><td>SS \
                                    </td><td>df</td><td>MS</td><td>F</td>  \
                                    <td>p-value</TD></tr>')
            output.Addhtml('<tr><td>FACTOR</td><td>%5.3f</td><td> \
                                    %5d</td><td>%5.3f</td><td>%5.3f</td>   \
                                    <td>%1.6f</td></tr>'%(TBase.SSbet,  \
                                    TBase.dfbet, TBase.MSbet, TBase.F,  \
                                    TBase.prob))
            output.Addhtml('<tr><td>Within</td><td>%5.3f</td><td>%5d\
                                    </td><td>%5.3f</td><td></td><td></td> \
                                    </tr>'%(TBase.SSwit, TBase.dfwit,     \
                                    TBase.MSwit))
            output.Addhtml('<tr><td>Error</td><td>%5.3f</td><td> \
                                    %5d</td><td>%5.3f</td><td></td><td></td> \
                                    </tr>'%(TBase.SSres, TBase.dfres,   \
                                    TBase.MSres))
            output.Addhtml('<tr><td>Total</td><td>%5.3f</td><td>%5d \
                                    </td><td></td><td></td><td></td>'% \
                                    (TBase.SStot, TBase.dftot))
            output.Addhtml('</table>')

        # Kruskal wallis H
        if self.TestChoice.IsChecked(2):
            output.Addhtml('<p><b>Kruskal Wallis H Test</b>')
            TBase.KruskalWallisH(biglist)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            vars = [['df', TBase.df],
                    ['H',TBase.h],
                    ['p',TBase.prob]]
            ln = tabler.table(vars)
            output.Addhtml(ln)

        # Friedman test
        if self.TestChoice.IsChecked(3):
            output.Addhtml('<p><b>Friedman Chi Square</b>')
            TBase.FriedmanChiSquare(biglist)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
                alpha = 0.10
            else:
                alpha = 0.05
            vars = [['df', TBase.df],
                    ['Chi',TBase.chisq],
                    ['p',TBase.prob]]
            ln = tabler.table(vars)
            output.Addhtml(ln)
            # the next few lines are commented out & are experimental. They
            # help perform multiple comparisons for the Friedman test.
            #outstring = '<a href="friedman,'
            #for i in range(k):
            #    outstring = outstring+'M,'+str(TBase.sumranks[i])+','
            #outstring = outstring+'k,'+str(k)+','
            #outstring = outstring+'n,'+str(d[0].N)+','
            #outstring = outstring+'p,'+str(alpha)+'">Multiple Comparisons</a>'
            #output.Addhtml('<p>'+outstring+'</p>')

        # Cochranes Q
        if self.TestChoice.IsChecked(4):
            output.Addhtml('<p><b>Cochranes Q</b>')
            TBase.CochranesQ(biglist)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            vars = [['df', TBase.df],
                    ['Q',TBase.q],
                    ['p',TBase.prob]]
            ln = tabler.table(vars)
            output.Addhtml(ln)
        self.Close(True)

    def OnCloseThreeCond(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
class CorrelationTestFrame(wx.Dialog):
    def __init__(self, parent, id, ColumnList):
        winheight = 500 + wind
        wx.Dialog.__init__(self, parent, id, "Correlations", \
                                    size=(500,400+wind))
        #set icon for frame (needs x-platform separator!
        x = self.GetClientSize()
        winheight = x[1]
        self.SetIcon(ico)
        colsselected =  frame.grid.GetColsUsedList()
        l0 = wx.StaticText(self,-1,"Select Columns to Analyse",pos=(10,10))
        l1 = wx.StaticText(self, -1, "Select Test(s) to Perform:", pos=(10,60))
        # No user hypothesised mean / variance needed here!
        if wx.Platform == '__WXMSW__':
            allbutton = wx.Button(self, 218, "Select All", wx.Point(250,winheight-70),\
                                    wx.Size(BWidth, BHeight))
            nonebutton = wx.Button(self, 220, "Select None", wx.Point(360,winheight-70),\
                                    wx.Size(BWidth, BHeight))
        else:
            allbutton = wx.Button(self, 218, "Select All", wx.Point(250,winheight-50),\
                                    wx.Size(BWidth, BHeight))
            nonebutton = wx.Button(self, 220, "Select None", wx.Point(360,winheight-50),\
                                    wx.Size(BWidth, BHeight))
        l4 = wx.StaticText(self,-1,"Select Descriptive Statistics",pos=(250,10))
        self.ColBox1 = wx.ComboBox(self,211,"Select Column", wx.Point(10,30),\
                                    wx.Size(110,20),ColumnList)
        self.ColBox2 = wx.ComboBox(self,212,"Select Column",wx.Point(130,30),\
                                    wx.Size(110,20),ColumnList)
        x1 = 0
        x2 = 1
        self.ColBox1.SetSelection(x1)
        self.ColBox2.SetSelection(x2)
        x1len = len(frame.grid.CleanData(x1))
        x2len = len(frame.grid.CleanData(x2))
        if (x1len != x2len):
            self.equallists = False
        else:
            self.equallists = True
        # list of tests in alphabetical order
        Tests = ['Kendalls tau','Pearsons correlation','Point Biserial r', \
                'Spearmans rho']
        self.paratests = wx.CheckListBox(self,213,wx.Point(10,80),\
                                    wx.Size(230,180),Tests)
        self.hypchoice=wx.RadioBox(self, 205,"Select Hypothesis",\
                                    wx.Point(10,270),wx.DefaultSize,HypList)
        self.hypchoice.SetSelection(1)
        self.DescChoice = DescChoiceBox(self, 215)
        okaybutton = wx.Button(self,216,"Okay",wx.Point(10,winheight-35), \
                                    wx.Size(BWidth, BHeight))
        cancelbutton = wx.Button(self,217,"Cancel",wx.Point(100,winheight-35), \
                                    wx.Size(BWidth, BHeight))
        wx.EVT_BUTTON(okaybutton, 216, self.OnOkayButton)
        wx.EVT_BUTTON(cancelbutton, 217, self.OnCloseTwoCond)
        wx.EVT_BUTTON(allbutton, 218, self.DescChoice.SelectAllDescriptives)
        wx.EVT_BUTTON(nonebutton, 220, self.DescChoice.SelectNoDescriptives)
        wx.EVT_COMBOBOX(self.ColBox1, 211, self.ChangeCol1)
        wx.EVT_COMBOBOX(self.ColBox2, 212, self.ChangeCol1)

    def ChangeCol1(self, event):
        # check that len of 2 cols is equal, if not disable choices of test
        x1 = len(frame.grid.CleanData(self.ColBox1.GetSelection()))
        x2 = len(frame.grid.CleanData(self.ColBox2.GetSelection()))
        if (x1 != x2):
            print "unequal"
            # disable some tests in the listbox
        else:
            print "equal"
            # enable all tests in the listbox

    def ChangeCol2(self, event):
        # check that len of 2 cols is equal, if not disable choices of test
        x1 = len(frame.grid.CleanData(self.ColBox1.GetSelection()))
        x2 = len(frame.grid.CleanData(self.ColBox2.GetSelection()))
        if (x1 != x2):
            print "unequal"
        else:
            print "equal"

    def OnOkayButton(self, event):
        x1 = self.ColBox1.GetSelection()
        y1 = self.ColBox2.GetSelection()
        name1 = frame.grid.GetColLabelValue(x1)
        name2 = frame.grid.GetColLabelValue(y1)
        if (x1 < 0) or (y1 < 0):
            self.Close(True)
            return
        x = frame.grid.CleanData(x1)
        xmiss = frame.grid.missing
        y = frame.grid.CleanData(y1)
        ymiss = frame.grid.missing
        TBase = salstat_stats.TwoSampleTests(x, y, name1, name2,xmiss,ymiss)
        d = [0,0]
        d[0] = TBase.d1
        d[1] = TBase.d2
        x2 = ManyDescriptives(self, d)
        
        # Kendalls tau correlation
        if self.paratests.IsChecked(0):
            output.Addhtml('<h3>Kendalls Tau correlation</h3>')
            TBase.KendallsTau(x, y)
            if (TBase.prob == -1.0):
                output.Addhtml('<p class="text-warning">Cannot do Kendall&#39;s tau correlation \
                                    - the data have unequal sizes')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                vars = [['Variable 1', name1],
                        ['Variable 2', name2],
                        ['Tau', TBase.tau],
                        ['z',TBase.z],
                        ['p',TBase.prob]]
                ln = tabler.table(vars)
                output.Addhtml(ln)

        # Pearsons r correlation
        if self.paratests.IsChecked(1):
            output.Addhtml('<H3>Pearsons correlation</H3>')
            TBase.PearsonsCorrelation(x, y)
            if (TBase.prob == -1.0):
                output.Addhtml('<p class="text-warning">Cannot do Pearson&#39;s correlation \
                                    - the data have unequal sizes')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                vars = [['Variable 1', name1],
                        ['Variable 2', name2],
                        ['df', TBase.df],
                        ['r',TBase.r],
                        ['t',TBase.t],
                        ['p',TBase.prob]]
                ln = tabler.table(vars)
                output.Addhtml(ln)

        # Point Biserial r
        if self.paratests.IsChecked(2):
            pass
        # Spearmans rho correlation
        if self.paratests.IsChecked(3):
            output.Addhtml('<H3>Spearmans rho correlation</H3>')
            TBase.SpearmansCorrelation(x, y)
            if (TBase.prob == -1.0):
                output.Addhtml('<p class="text-warning">Cannot do Spearmans correlation \
                                    - the data have unequal sizes')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                vars = [['Variable 1', name1],
                        ['Variable 2', name2],
                        ['df', TBase.df],
                        ['Rho',TBase.rho],
                        ['p',TBase.prob]]
                ln = tabler.table(vars)
                output.Addhtml(ln)

        self.Close(True)

    def OnCloseTwoCond(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
class MFanovaFrame(wx.Dialog):
    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, "Multi-factorial anova", \
                        size=(500,400+wind))
        #set icon for frame (needs x-platform separator!
        x = self.GetClientSize()
        winheight = x[1]
        self.SetIcon(ico)
        ColumnList, self.colnums = frame.grid.GetUsedCols()
        l0 = wx.StaticText(self,-1,"Select Columns to Analyse",pos=(10,10))
        l1 = wx.StaticText(self, -1, "Select IV:", pos=(10,60))
        l2 = wx.StaticText(self, -1, "Select DV", pos=(10,170))
        l4 = wx.StaticText(self,-1,"Select Descriptive Statistics",pos=(250,10))
        self.IVbox = wx.CheckListBox(self, 413,wx.Point(10,30),\
                                    wx.Size(230,130),ColumnList)
        self.DVbox = wx.CheckListBox(self, 414,wx.Point(10,190), \
                                    wx.Size(230,120),ColumnList)
        self.hypchoice=wx.RadioBox(self, 205,"Select Hypothesis",\
                                    wx.Point(10,320),wx.DefaultSize,HypList)
        self.hypchoice.SetSelection(1)
        #self.DescChoice = DescChoiceBox(self, 215)
        # I might leave the descriptives out and implement a feedback box
        # that tells the user about the analysis (eg, how many factors, # 
        # levels per factor, # interactions etc which might be useful. It
        # would be updated whenever the user changes a selection.
        okaybutton = wx.Button(self,216,"Okay",wx.Point(10,winheight-35), \
                                    wx.Size(BWidth, BHeight))
        cancelbutton = wx.Button(self,217,"Cancel",wx.Point(100,winheight-35), \
                                    wx.Size(BWidth, BHeight))
        allbutton = wx.Button(self, 218,"Select All",wx.Point(250,winheight-70),\
                                    wx.Size(BWidth, BHeight))
        nonebutton = wx.Button(self, 220, "Select None", wx.Point(360, \
                                    winheight-70),wx.Size(BWidth, BHeight))
        self.DescChoice = DescChoiceBox(self, 104)
        wx.EVT_BUTTON(okaybutton, 216, self.OnOkayButton)
        wx.EVT_BUTTON(cancelbutton, 217, self.OnCloseTwoCond)
        wx.EVT_BUTTON(allbutton, 218, self.DescChoice.SelectAllDescriptives)
        wx.EVT_BUTTON(nonebutton, 220, self.DescChoice.SelectNoDescriptives)
        # Need to check that a col ticked in one box is not ticked in the other
        #EVT_CHECKLISTBOX(self.IVbox, 413, self.CheckforIXbox)
        #EVT_CHECKLISTBOX(self.DVbox,414,self.CheckforDVbox)

    def OnOkayButton(self, event):
        self.Close(True)

    def OnCloseTwoCond(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# instance of the tool window that contains the test buttons
# note this is experimental and may not be final
class TestFrame(wx.MiniFrame):
    def __init__(self, parent, title):
        self.parent = parent
        wx.MiniFrame.__init__(self, parent, -1, 'Tests', size=(120,400), pos=(5,5))
        descButton = wx.Button(self, 151,'Descriptives (F1)',wx.Point(0,0),wx.Size(115,40))
        sign1Button=wx.Button(self,153,'sign test 1 sample',wx.Point(0,40),wx.Size(115,40))
        ttestpairedButton=wx.Button(self,154,'t-test paired <F2>',wx.Point(0,80),wx.Size(115,40))
        ttestunpairedButton = wx.Button(self, 155, 't-test unpaired <F3>',wx.Point(0,120),wx.Size(115,40))
        chisquareButton = wx.Button(self,156,'Chi square <F4>',wx.Point(0,160),wx.Size(155,40))
        mannwhitneyButton=wx.Button(self,157,'Mann-Whitney U',wx.Point(0,200),wx.Size(115,40))
        kolmogorovButton=wx.Button(self,158,'Kolmogorov-Smirnov',wx.Point(0,240),wx.Size(115,40))
        anovaButton=wx.Button(self,159,'anova between',wx.Point(0,280),wx.Size(115,40))
        anovaWButton=wx.Button(self,160,'anova within',wx.Point(0,320),wx.Size(115,40))
        # and so on...
        # only put keyboard shortcuts for the most required ones. DONT allow the user to change this
        wx.EVT_CLOSE(self, self.DoNothing)
        wx.EVT_BUTTON(descButton, 151, self.GetDescriptives)

    def DoNothing(self, event):
        pass

    def GetDescriptives(self, event):
        print self.parent.grid.GetSelectedCols()

#---------------------------------------------------------------------------
class TransformFrame(wx.Dialog):
    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, "Transformations", \
                        size=(500,400+wind))
        #set icon for frame (needs x-platform separator!
        x = self.GetClientSize()
        winheight = x[1]
        self.SetIcon(ico)
        self.transform = ""
        self.transformName = ""
        self.ColumnList, self.colnums = frame.grid.GetUsedCols()
        self.cols = frame.grid.GetNumberCols()
        l0 = wx.StaticText(self,-1,"Select Columns to Transform",pos=(10,10))
        self.ColChoice = wx.CheckListBox(self,1102, wx.Point(10,30), \
                                    wx.Size(230,(winheight * 0.8)), self.ColumnList)
        okaybutton = wx.Button(self,1105,"Okay",wx.Point(10,winheight-35),\
                                    wx.Size(BWidth, BHeight))
        cancelbutton = wx.Button(self,1106,"Cancel",wx.Point(100,winheight-35),\
                                    wx.Size(BWidth, BHeight))
        # common transformations:
        l1 = wx.StaticText(self, -1, "Common Transformations:", pos=(250,30))
        squareRootButton = wx.Button(self, 1110, "Square Root", wx.Point(250, 60), \
                                    wx.Size(BWidth, BHeight))
        logButton = wx.Button(self, 1111, "Logarithmic",wx.Point(250, 100), \
                                    wx.Size(BWidth, BHeight))
        reciprocalButton = wx.Button(self, 1112, "Reciprocal", wx.Point(250,140), \
                                    wx.Size(BWidth, BHeight))
        squareButton = wx.Button(self, 1113, "Square", wx.Point(250,180), \
                                    wx.Size(BWidth, BHeight))
        l2 = wx.StaticText(self, -1, "Function :", wx.Point(250, 315))
        self.transformEdit = wx.TextCtrl(self,1114,pos=(250,335),size=(150,20))
        wx.EVT_BUTTON(okaybutton, 1105, self.OnOkayButton)
        wx.EVT_BUTTON(cancelbutton, 1106, self.OnCloseFrame)
        wx.EVT_BUTTON(squareRootButton, 1110, self.squareRootTransform)
        wx.EVT_BUTTON(logButton , 1111, self.logTransform)
        wx.EVT_BUTTON(reciprocalButton, 1112, self.reciprocalTransform)
        wx.EVT_BUTTON(squareButton, 1113, self.squareTransform)

    def squareRootTransform(self, event):
        self.transform = "math.sqrt(x)"
        self.transformEdit.SetValue(self.transform)
        self.transformName = " Square Root"

    def logTransform(self, event):
        self.transform = "math.log(x)"
        self.transformEdit.SetValue(self.transform)
        self.transformName = " Logarithm"

    def reciprocalTransform(self, event):
        self.transform = "1 / x"
        self.transformEdit.SetValue(self.transform)
        self.transformName = " Reciprocal"

    def squareTransform(self, event):
        self.transform = "x * x"
        self.transformEdit.SetValue(self.transform)
        self.transformName = " Square"

    def OnOkayButton(self, event):
        pass # start transforming!
        # process: collect each selected column, then pass the contents through the self.transform function
        # then put the resulting column into a new column, and retitle it with the original variable 
        # name plus the function.
        self.transform = self.transformEdit.GetValue()
        cols = range(self.cols)
        emptyCols = []
        for i in cols:
            if cols[i] not in self.colnums:
                emptyCols.append(cols[i])
        for i in range(len(self.colnums)):
            if self.ColChoice.IsChecked(i):
                oldcol = frame.grid.CleanData(i)
                newcol = [0]*len(oldcol)
                for j in range(len(oldcol)):
                    x = oldcol[j]
                    try:
                        newcol[j] = eval(self.transform)
                    except: # which exception would this be?
                        pass # need to do something here.
                PutData(emptyCols[i], newcol)
                # put in a nice new heading
                oldHead = frame.grid.GetColLabelValue(self.colnums[i])
                if self.transformName == "":
                    self.transformName = ' ' + self.transform
                oldHead = oldHead + self.transformName
                frame.grid.SetColLabelValue(emptyCols[i], oldHead)
                emptyCols.pop(emptyCols[i])
        self.Close(True)

    def OnCloseFrame(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# Plot Window
# This frame holds the plots using the wx.PlotCanvas widget
class PlotFrame(wx.Frame):
    def __init__(self, parent, log):
        wx.Frame.__init__(self, parent, -1,"SalStat Plot (Basic!)", \
                                    size=(500,400))
        file_menu = wx.Menu()
        edit_menu = wx.Menu()
        title_menu = wx.Menu()
        file_menu.Append(ID_FILE_GSAVEAS, 'Save &As...')
        file_menu.Append(ID_FILE_GPRINTSETUP, 'Page Setup...')
        file_menu.Append(ID_FILE_GPRINTPREVIEW, 'Print Preview...')
        file_menu.Append(ID_FILE_GPRINT, '&Pryint...')
        file_menu.Append(ID_FILE_GCLOSE, '&Close')
        title_menu.Append(ID_TITLE_GTITLE, '&Graph Title...')
        title_menu.Append(ID_TITLE_GXAXIS, '&X Axis Label...')
        title_menu.Append(ID_TITLE_GYAXIS, '&Y Axis Label...')
        title_menu.Append(ID_TITLE_LEGEND, '&Enable Legend', kind=wx.ITEM_CHECK)
        title_menu.Append(ID_TITLE_GRID, 'Enable &Grid', kind=wx.ITEM_CHECK)
        gmenuBar = wx.MenuBar()
        gmenuBar.Append(file_menu, '&File')
        gmenuBar.Append(edit_menu, '&Edit')
        gmenuBar.Append(title_menu, '&Plot')
        EVT_MENU(self, ID_FILE_GSAVEAS, self.SaveAs)
        EVT_MENU(self, ID_FILE_GPRINTSETUP, self.PrintSetup)
        EVT_MENU(self, ID_FILE_GPRINTPREVIEW, self.PrintPreview)
        EVT_MENU(self, ID_FILE_GPRINT, self.PrintGraph)
        EVT_MENU(self, ID_FILE_GCLOSE, self.CloseWindow)
        EVT_MENU(self, ID_TITLE_GTITLE, self.SetTitle)
        EVT_MENU(self, ID_TITLE_GXAXIS, self.SetXAxis)
        EVT_MENU(self, ID_TITLE_GYAXIS, self.SetYAxis)
        EVT_MENU(self, ID_TITLE_LEGEND, self.EnableLegend)
        EVT_MENU(self, ID_TITLE_GRID, self.EnableGrid)
        self.SetMenuBar(gmenuBar)
        self.client = wx.PyPlot.PlotCanvas(self)

    def EnableGrid(self, event):
        self.client.SetEnableGrid(event.IsChecked())

    def SetTitle(self, event):
        dlg = wx.TextEntryDialog(self, 'Enter the graph title','Graph Title')
        dlg.SetValue(self.client.getTitle())
        # the previous line doesn't work.
        if dlg.ShowModal() == wx.ID_OK:
            self.client.setTitle(dlg.GetValue())

    def SetXAxis(self, event):
        pass

    def SetYAxis(self, event):
        pass

    def EnableLegend(self, event):
        self.client.SetEnableLegend(event.IsChecked())

    def PrintSetup(self, event):
        self.client.PageSetup()

    def PrintPreview(self, event):
        self.client.PrintPreview()

    def PrintGraph(self, event):
        self.client.Printout()

    def SaveAs(self, event):
        self.client.SaveFile()

    def CloseWindow(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# call instance of DataGrid
# This is main interface of application
class DataFrame(wx.Frame):
    def __init__(self, parent, log, filename=None):
        # size the frame to 600x400 - will fit in any VGA screen
        self.hideDataGrid = False
        dimx = int(inits.get('gridsizex'))
        dimy = int(inits.get('gridsizey'))
        posx = int(inits.get('gridposx'))
        posy = int(inits.get('gridposy'))
        if filename == None:
            frameTitle = "Untitled"
        else:
            frameTitle = filename
        wx.Frame.__init__(self,parent,-1,frameTitle, size=(dimx,\
                                    dimy), pos=(posx,posy))
        #set icon for frame (needs x-platform separator!
        #icon = images.getIconIcon()
        self.SetIcon(ico)
        #set up menus
        file_menu = wx.Menu()
        edit_menu = wx.Menu()
        prefs_menu = wx.Menu()
        describe_menu = wx.Menu()
        analyse_menu = wx.Menu()
        #analyse2_menu = wx.Menu()
        preparation_menu = wx.Menu()
        chart_menu = wx.Menu()
        help_menu = wx.Menu()
        #add contents of menu
        file_menu.Append(ID_FILE_NEW,'&New Data\tCTRL+N')
        #file_menu.Append(ID_FILE_NEWOUTPUT, 'New &Output Sheet')
        file_menu.Append(ID_FILE_OPEN, '&Open...\tCTRL+O')
        file_menu.Append(ID_FILE_SAVE, '&Save\tCTRL+S')
        file_menu.Append(ID_FILE_SAVEAS, 'Save &As...\tSHIFT+CTRL+S')
        file_menu.AppendSeparator()
        file_menu.Append(ID_FILE_PRINT, '&Print...\tCTRL+P')
        file_menu.AppendSeparator()
        file_menu.Append(ID_FILE_EXIT, 'Q&uit\tCTRL+Q')
        edit_menu.Append(ID_EDIT_CUT, 'Cu&t\tCTRL+X')
        edit_menu.Append(ID_EDIT_COPY, '&Copy\tCTRL+C')
        edit_menu.Append(ID_EDIT_PASTE, '&Paste\tCTRL+V')
        edit_menu.Append(ID_EDIT_SELECTALL, 'Select &All\tCTRL+A')
        edit_menu.Append(ID_EDIT_FIND, '&Find and Replace...\tCTRL+F')
        edit_menu.AppendSeparator()
        edit_menu.Append(ID_EDIT_DELETECOL, 'Delete Current Column')
        edit_menu.Append(ID_EDIT_DELETEROW, 'Delete Current Row')
        prefs_menu.Append(ID_PREF_VARIABLES, 'Variables...')
        prefs_menu.Append(ID_PREF_GRID, 'Add Columns and Rows...')
        prefs_menu.Append(ID_PREF_CELLS, 'Change Cell Size...')
        prefs_menu.Append(ID_PREF_FONTS, 'Change the Font...')
        preparation_menu.Append(ID_PREPARATION_DESCRIPTIVES, 'Descriptive Statistics...')
        preparation_menu.Append(ID_PREPARATION_TRANSFORM, 'Transform Data...')
        #preparation_menu.Append(ID_PREPARATION_OUTLIERS, 'Check for Outliers...')
        #preparation_menu.Append(ID_PREPARATION_NORMALITY, 'Check for Normal Distribution...')
        analyse_menu.Append(ID_ANALYSE_1COND, '&1 Condition Tests...')
        analyse_menu.Append(ID_ANALYSE_2COND, '&2 Condition Tests...')
        analyse_menu.Append(ID_ANALYSE_3COND, '&3+ Condition Tests...')
        analyse_menu.Append(ID_ANALYSE_CORRELATION,'&Correlations...')
        #analyse_menu.Append(ID_ANALYSE_2FACT, '2+ &Factor Tests...')
        analyse_menu.AppendSeparator()
        analyse_menu.Append(ID_ANALYSE_SCRIPT, 'Scripting Window...')
        chart_menu.Append(ID_CHART_DRAW, 'Draw a chart...')
        # the bar chart is *not* ready yet!
        help_menu.Append(ID_HELP_WIZARD, '&What Test Should I Use...')
        help_menu.Append(ID_HELP_TOPICS, '&Topics...')
        help_menu.Append(ID_HELP_LICENCE, '&Licence...')
        help_menu.Append(wx.ID_ABOUT, '&About Salstat...')
        #set up menu bar
        menuBar = wx.MenuBar()
        menuBar.Append(file_menu, '&File')
        menuBar.Append(edit_menu, '&Edit')
        menuBar.Append(prefs_menu, '&Preferences')
        menuBar.Append(preparation_menu, 'P&reparation')
        menuBar.Append(analyse_menu, '&Analyse')
        menuBar.Append(chart_menu, '&Chart')
        menuBar.Append(help_menu, '&Help')
        #call menu bar (show it on the frame
        self.SetMenuBar(menuBar)
        #create small status bar
        self.CreateStatusBar()
        self.SetStatusText('SalStat Statistics')
        #Get icons for toolbar
        NewIcon = images.getNewBitmap()
        OpenIcon = images.getOpenBitmap()
        SaveIcon = images.getSaveBitmap()
        SaveAsIcon = images.getSaveAsBitmap()
        PrintIcon = images.getPrintBitmap()
        CutIcon = images.getCutBitmap()
        CopyIcon = images.getCopyBitmap()
        PasteIcon = images.getPasteBitmap()
        PrefsIcon = images.getPreferencesBitmap()
        HelpIcon = images.getHelpBitmap()
        #create toolbar (nothing to add yet!)
        toolBar = self.CreateToolBar(wx.TB_HORIZONTAL|wx.NO_BORDER| \
                                    wx.TB_FLAT|wx.TB_TEXT)
        toolBar.AddLabelTool(10, "New", wx.Bitmap("icons/IconNew.png"), shortHelp="Create a new data sheet")
        toolBar.AddLabelTool(20, "Open", wx.Bitmap("icons/IconOpen.png"), shortHelp="Open a data file")
        toolBar.AddLabelTool(30, "Save", wx.Bitmap("icons/IconSave.png"), shortHelp="Save these data to file")
        toolBar.AddLabelTool(40, "Save As", wx.Bitmap("icons/IconSaveAs.png"), shortHelp="Save these data to a new filename")
        toolBar.AddLabelTool(50, "Print", wx.Bitmap("icons/IconPrint.png"), shortHelp="Print this sheet")
        toolBar.AddLabelTool(60, "Cut", wx.Bitmap("icons/IconCut.png"), shortHelp="Cut selection to clipboard")
        toolBar.AddLabelTool(70, "Copy", wx.Bitmap("icons/IconCopy.png"), shortHelp="Copy selection to clipboard")
        toolBar.AddLabelTool(80, "Paste", wx.Bitmap("icons/IconPaste.png"), shortHelp="Paste selection from clipboard")
        toolBar.AddLabelTool(85, "Preferences", wx.Bitmap("icons/IconPrefs.png"), shortHelp="Set your preferences")
        toolBar.AddLabelTool(87, "Meta", wx.Bitmap("icons/IconHelp.png"), shortHelp="Set variables")
        toolBar.AddLabelTool(88, "Chart", wx.Bitmap("icons/IconHelp.png"), shortHelp="View the chart window")
        toolBar.AddLabelTool(90, "Help", wx.Bitmap("icons/IconHelp.png"), shortHelp="Get help")
        toolBar.SetToolBitmapSize((24,24))
        # more toolbuttons are needed: New Output, Save, Print, Cut, \
        # Variables, and Wizard creates the toolbar
        toolBar.Realize()
        self.SetToolBar(toolBar)
        #still need to define event handlers
        #set up the datagrid
        """
        self.grid = MetaGrid.metaGrid(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.metagrid = MetaGrid.metaGrid(self)
        self.sizer.Add(self.grid, 1, wx.EXPAND)
        self.sizer.Add(self.metagrid, 1, wx.EXPAND)
        self.metagrid.Hide()
        self.grid.Show()
        self.SetSizer(self.sizer)
        self.Layout()
        """
        self.grid = SimpleGrid(self, log)
        self.grid.SetDefaultColSize(60, True)
        self.grid.SetRowLabelSize(40)

        #self.setTitle('Go')
        #win2 = TestFrame(self, 'Tests')
        #win2.Show(True)

        #...and some events!
        wx.EVT_MENU(self, ID_FILE_NEW, self.GoClearData)
        wx.EVT_TOOL(self, 10, self.GoClearData)
        #wx.EVT_MENU(self, ID_FILE_NEWOUTPUT, self.GoNewOutputSheet)
        # unsure if I want this - maybe restrict user to just one?
        wx.EVT_MENU(self, ID_FILE_SAVE, self.grid.SaveDataASCII)
        wx.EVT_TOOL(self, 30, self.grid.SaveDataASCII)
        wx.EVT_MENU(self, ID_FILE_SAVEAS, self.grid.SaveAsDataASCII)
        wx.EVT_TOOL(self, 40, self.grid.SaveAsDataASCII)
        wx.EVT_MENU(self, ID_FILE_OPEN, self.grid.LoadDataASCII)
        #EVT_MENU(self, ID_FILE_OPEN, self.grid.LoadNumericData)
        wx.EVT_TOOL(self, 20, self.grid.LoadDataASCII)
        #EVT_TOOL(self, 20, self.grid.LoadNumericData)
        wx.EVT_MENU(self, ID_EDIT_CUT, self.grid.CutData)
        wx.EVT_TOOL(self, 60, self.grid.CutData)
        wx.EVT_MENU(self, ID_EDIT_COPY, self.grid.CopyData)
        wx.EVT_TOOL(self, 70, self.grid.CopyData)
        wx.EVT_MENU(self, ID_EDIT_PASTE, self.grid.PasteData)
        wx.EVT_TOOL(self, 80, self.grid.PasteData)
        wx.EVT_MENU(self, ID_EDIT_SELECTALL, self.grid.SelectAllCells)
        wx.EVT_MENU(self, ID_EDIT_FIND, self.GoFindDialog)
        wx.EVT_MENU(self, ID_EDIT_DELETECOL, self.grid.DeleteCurrentCol)
        wx.EVT_MENU(self, ID_EDIT_DELETEROW, self.grid.DeleteCurrentRow)
        wx.EVT_MENU(self, ID_PREF_VARIABLES, self.GoVariablesFrame)
        wx.EVT_TOOL(self, 85, self.GoVariablesFrame)
        wx.EVT_TOOL(self, 87, self.ToggleMetaGrid)
        wx.EVT_TOOL(self, 88, self.ToggleChartWindow)
        wx.EVT_MENU(self, ID_PREF_GRID, self.GoEditGrid)
        wx.EVT_MENU(self, ID_PREF_CELLS, self.GoGridPrefFrame)
        wx.EVT_MENU(self, ID_PREF_FONTS, self.GoFontPrefsDialog)
        wx.EVT_MENU(self, ID_PREPARATION_DESCRIPTIVES, self.GoContinuousDescriptives)
        wx.EVT_MENU(self, ID_PREPARATION_TRANSFORM, self.GoTransformData)
        wx.EVT_MENU(self, ID_PREPARATION_OUTLIERS, self.GoCheckOutliers)
        wx.EVT_MENU(self, ID_ANALYSE_1COND, self.GoOneConditionTest)
        wx.EVT_MENU(self, ID_ANALYSE_2COND, self.GoTwoConditionTest)
        wx.EVT_MENU(self, ID_ANALYSE_3COND, self.GetThreeConditionTest)
        wx.EVT_MENU(self, ID_ANALYSE_CORRELATION, self.GetCorrelationsTest)
        #wx.EVT_MENU(self, ID_ANALYSE_2FACT, self.GoMFanovaFrame)
        wx.EVT_MENU(self, ID_ANALYSE_SCRIPT, self.GoScriptWindow)
        wx.EVT_MENU(self, ID_CHART_DRAW, self.GoChartWindow)
        wx.EVT_MENU(self, ID_BARCHART_DRAW, self.GoBarChartWindow)
        wx.EVT_MENU(self, wx.ID_ABOUT, self.GoHelpAboutFrame)
        wx.EVT_MENU(self, ID_HELP_WIZARD, self.GoHelpWizardFrame)
        wx.EVT_MENU(self, ID_HELP_TOPICS, self.GoHelpTopicsFrame)
        wx.EVT_TOOL(self, 90, self.GoHelpAboutFrame)
        wx.EVT_MENU(self, ID_HELP_LICENCE, self.GoHelpLicenceFrame)
        wx.EVT_MENU(self, ID_FILE_EXIT, self.EndApplication)
        wx.EVT_CLOSE(self, self.EndApplication)

    def ToggleChartWindow(self, event):
        self.chartWindow = ChartWindow.ChartWindow(self.grid)
        self.chartWindow.Show(True)
        self.chartWindow.preview.SetPage(self.chartWindow.chartObject.page,"")
        #print frame.chartObject.page
        #frame.preview.SetPage(frame.chartObject.chartLine,"")

    def ToggleMetaGrid(self, event):
        self.metaGrid = MetaGrid.MetaFrame(self)
        self.metaGrid.Show(True)

    def MacOpenFile(self, filename):
        # overrides method to load file on OSX
        print filename

    def MacReopenApp(self):
        self.GetTopWindow().Raise()

    def setTitle(self, title):
        self.SetTitle(title)

    def GoClearData(self, evt):
        #shows a new data entry frame
        self.grid.filename = "Untitled"
        self.grid.Saved = True
        self.grid.named = False
        self.grid.ClearGrid()

    def GoNewOutputSheet(self, evt):
        #shows a new output frame
        SheetWin = OutputSheet(frame, -1)
        SheetWin.Show(True)

    def GoFindDialog(self, event):
        # Shows the find & replace dialog
        # NOTE - this doesn't appear to work on the grid, so I might be missing something...
        data = wx.FindReplaceData()
        dlg = wx.FindReplaceDialog(self.grid, data, 'Find and Replace', \
                                    wx.FR_REPLACEDIALOG)
        dlg.data = data
        dlg.Show(True)

    def GoEditGrid(self, event):
        #shows dialog for editing the data grid
        win = EditGridFrame(frame, -1)
        win.Show(True)

    def GoVariablesFrame(self, evt):
        # shows Variables dialog
        win = VariablesFrame(frame, -1)
        win.Show(True)

    def GoGridPrefFrame(self, evt):
        # shows Grid Preferences form
        win = GridPrefs(frame, -1)
        win.Show(True)

    def GoFontPrefsDialog(self, evt):
        # shows Font dialog for the data grid (output window has its own)
        data = wx.FontData()
        dlg = wx.FontDialog(frame, data)
        self.SetIcon(ico)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetFontData()
            #data2 = data.GetChosenFont()
            self.grid.SetDefaultCellFont(data.GetChosenFont())

    def GoContinuousDescriptives(self, evt):
        # shows the continuous descriptives dialog
        win = DescriptivesFrame(frame, -1)
        win.Show(True)

    def GoTransformData(self, event):
        win = TransformFrame(frame, -1)
        win.Show(True)

    def GoCheckOutliers(self, event):
        pass

    def GoOneConditionTest(self, event):
        # shows One Condition Test dialog
        ColumnList, waste = self.grid.GetUsedCols()
        if (len(ColumnList) > 0):
            win = OneConditionTestFrame(frame, -1, ColumnList)
            win.Show(True)
        else:
            self.SetStatusText('You need to enter 1 data column for this!')

    def GoTwoConditionTest(self,event):
        # show Two Conditions Test dialog
        ColumnList, waste = self.grid.GetUsedCols()
        if (len(ColumnList) > 1):
            win = TwoConditionTestFrame(frame, -1, ColumnList)
            win.Show(True)
        else:
            self.SetStatusText('You need 2 data columns for that!')

    def GetThreeConditionTest(self, event):
        # shows three conditions or more test dialog
        ColumnList, waste = self.grid.GetUsedCols()
        if (len(ColumnList) > 1):
            win = ThreeConditionTestFrame(frame, -1, ColumnList)
            win.Show(True)
        else:
            self.SetStatusText('You need some data for that!')

    def GetCorrelationsTest(self, event):
        # Shows the correlations dialog
        ColumnList, waste = self.grid.GetUsedCols()
        if (len(ColumnList) > 1):
            win = CorrelationTestFrame(frame, -1, ColumnList)
            win.Show(True)
        else:
            self.SetStatusText('You need 2 data columns for that!')

    def GoMFanovaFrame(self, event):
        win = MFanovaFrame(frame, -1)
        win.Show(True)

    def GoScriptWindow(self, event):
        # Shows the scripting window
        win = ScriptFrame(frame, -1)
        win.Show(True)

    def GoChartWindow(self, event):
        # Draws a line chart based on the means
        ChartWindow = charter.ChartWindow(self)
        ChartWindow.Show(True)
        waste, colnums = self.grid.GetUsedCols()
        if colnums != []:
            nameslist = [0]*len(colnums)
            meanlist = numpy.zeros(len(colnums)*2)
            meanlist.shape = (len(colnums),2)
            for i in range(len(colnums)):
                d = salstat_stats.FullDescriptives(self.grid.CleanData(colnums[i]))
                meanlist[i,1] = d.mean
                nameslist[i] = frame.grid.GetColLabelValue(i)
            meanlist[:,0] = numpy.arange(len(colnums))
            lines = wx.PyPlot.PolyLine(meanlist, legend="Red Line", colour='red')
            #lines2 = wx.PyPlot.PolyBars(meanlist)
            self.win = PlotFrame(self, -1)
            self.win.Show(True)
            self.win.client.Draw(wx.PyPlot.PlotGraphics([lines],"Graph","X","Y"))
            #self.win.client.draw(lines2,'automatic','automatic',None, nameslist)
        else:
            self.SetStatusText('You need some data to draw a graph!')

    def GoBarChartWindow(self, event):
        # Draws a bar chart based on the means
        waste, colnums = self.grid.GetUsedCols()
        if colnums != []:
            nameslist = [0]*len(colnums)
            meanlist = numpy.zeros(len(colnums)*2)
            meanlist.shape = (len(colnums),2)
            for i in range(len(colnums)):
                d = salstat_stats.FullDescriptives(self.grid.CleanData(colnums[i]))
                meanlist[i,1] = d.mean
                nameslist[i] = frame.grid.GetColLabelValue(i)
            meanlist[:,0] = numpy.arange(len(colnums))
            lines = PolyBars(meanlist)
            self.win = PlotFrame(self, -1)
            self.win.Show(True)
            self.win.client.draw(lines,'automatic','automatic',None, nameslist)
        else:
            self.SetStatusText('You need some data to draw a graph!')

    def GoHelpWizardFrame(self, event):
        # shows the "wizard" in the help box
        win = AboutFrame(frame, -1, 0)
        win.Show(True)

    def GoHelpTopicsFrame(self, event):
        # shows the help topics in the help box
        win = AboutFrame(frame, -1, 1)
        win.Show(True)

    def GoHelpLicenceFrame(self, evt):
        # shows the licence in the help box
        win = AboutFrame(frame, -1, 2)
        win.Show(True)

    def GoHelpAboutFrame(self, evt):
        # Shows the "About" thing in the help box
        win = AboutFrame(frame, -1, 3)
        win.Show(True)

    def EndApplication(self, evt):
        if self.grid.Saved:
            self.FinalExit()
        else:
            dlg = SaveDialog2(self, -1)
            val = dlg.ShowModal()
            #val = dlg.ShowWindowModal()
            if val == 3:
                self.FinalExit()
            elif val == 2:
                if self.grid.named:
                    self.grid.SaveDataASCII(None)
                    self.FinalExit()
                else:
                    defDir = inits['savedir']
                    dlg = wx.FileDialog( \
                            self, message="Save file as...", defaultDir=defDir,
                            defaultFile="Untitled", style=wx.SAVE)
                    if dlg.ShowModal() == wx.ID_OK:
                        path, self.filename = os.path.split(dlg.GetPath())
                        self.grid.SaveDataASCII(None)
                        self.FinalExit()
                    else:
                        return
            else:
                return

    def FinalExit(self):
        dims = self.GetSizeTuple()
        inits.update({'gridsizex': dims[0]})
        inits.update({'gridsizey': dims[1]})
        dims = self.GetPositionTuple()
        inits.update({'gridposx': dims[0]})
        inits.update({'gridposy': dims[1]})
        dims = output.GetSizeTuple()
        inits.update({'outputsizex': dims[0]})
        inits.update({'outputsizey': dims[1]})
        dims = output.GetPositionTuple()
        inits.update({'outputposx': dims[0]})
        inits.update({'outputposy': dims[1]})
        initskeys = inits.keys()
        initsvalues = inits.values()
        initfilename = ini.initfile
        fout = file(initfilename,'w')
        for i in range(len(initskeys)):
            fout.write(str(initskeys[i])+' '+str(initsvalues[i])+'\n')
        fout.close()
        frame.Destroy()

#---------------------------------------------------------------------------
# Scripting API is defined here. So far, only basic (but usable!) stuff.
def GetData(column):
    """This function enables the user to extract the data from the data grid.
    The data are "clean" and ready for analysis."""
    return frame.grid.CleanData(column)

def GetDataName(column):
    """This function returns the name of the data variable - in other words,
    the column label from the grid."""
    return frame.grid.GetColLabelValue(column)

def Display(text):
    """writes the text onto the html page. Handles lists and numerics"""
    text = str(text)
    output.htmlpage.write(string.join(text, ""))

def Describe(datain):
    """Provides OO descriptive statistics. Called by >>>x = Describe(a)
    and then a.N for the N, a.sum for the sum etc"""
    if (type(datain) == int):
        datain = frame.grid.CleanData(col2)
    return salstat_stats.FullDescriptives(datain)


def PutData(column, data):
    """This routine takes a list of data, and puts it into the datagrid
    starting at row 0. The grid is resized if the list is too large. This
    routine desparately needs to be updated to prevent errors"""
    n = len(data)
    if (n > frame.grid.GetNumberRows()):
        frame.grid.AddNCols(-1, (datawidth - gridwidth + 5))
    for i in range(n):
        frame.grid.SetCellValue(i, column, str(data[i]))

#---------------------------------------------------------------------------
# API statistical analysis functions
#One sample tests:
def DoOneSampleTTest(col1, usermean, tail = 2):
    """This routine performs a 1 sample t-test using the given data and
    a specified user mean."""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for column 1\n'
    TBase = salstat_stats.OneSampleTests(col1, umean)
    TBase.OneSampleTTest(usermean)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.t, TBase.df, TBase.prob
    else:
        return Error

def DoOneSampleSignTest(col1, usermean, tail = 2):
    """This routine performs a 1 sample sign-test using the given data and
    a specified user mean."""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for column 1\n'
    TBase = salstat_stats.OneSampleTests(col1, umean)
    TBase.OneSampleSignTest(usermean)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.nplus, TBase.nminus, TBase.z, TBase.prob
    else:
        return Error

def DoChiSquareVariance(col1, usermean, tail = 2):
    """This routine performs a chi square for variance ratio test using 
    the given data and a specified user mean."""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for column 1\n'
    TBase = salstat_stats.OneSampleTests(col1, umean)
    TBase.ChiSquareVariance(usermean)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.chisquare, TBase.df, TBase.prob
    else:
        return Error

#Two sample tests:
def DoPairedTTest(col1, col2, tail = 2):
    """This routine performs a paired t-test using the data contained in
    col1 and col2 on the grid, with the passed alpha value which defaults
    to 0.05 (5%). If col1 and col2 are lists, then the data contained in the
    lists are used instead. There is a modicum of bounds checking on the
    passed variables to ensure that they are the right types (and bounds)"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for column 1\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col2)
    elif (type(col2) != list):
        error = error +'Invalid information for column 2\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.TTestPaired(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.t, TBase.df, TBase.prob
    else:
        return Error

def DoUnpairedTTest(col1, col2, tail = 2):
    """This function performs an unpaired t-test on the data passed. If the
    passed parameters are a list, then that is used as the data, otherwise
    if the parameters are an integer, then that integers columns data are
    retrieved."""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.TTestUnpaired()
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.t, TBase.df, TBase.prob
    else:
        return error

def DoPearsonsCorrelation(col1, col2, tail = 2):
    """This function performs a Pearsons correlation upon 2 data sets."""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.PearsonsCorrelation(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.t, TBase.r, TBase.df, TBase.prob
    else:
        return error

def DoFTest(col1, col2, uservar, tail = 2):
    """This performs an F-test for variance ratios upon 2 data sets. Passed
    in addition to the datasets is the user variance"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.TwoSampleSignTextCorrelation(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.t, TBase.r, TBase.df, TBase.prob
    else:
        return error

def DoSignTest(col1, col2, tail = 2):
    """This function performs a 2-sample sign test on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.TwoSampleSignTextCorrelation(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.z, TBase.prob
    else:
        return error

def DoKendallsCorrelation(col1, col2, tail = 2):
    """This function performs a Kendalls tau correlation"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.KendalssTau(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.tau, TBase.z, TBase.prob
    else:
        return error

def DoKSTest(col1, col2, tail = 2):
    """This function performs a Komogorov-Smirnov test on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.KolmogorovSmirnov(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.d, TBase.prob
    else:
        return error

def DoSpearmansCorrelation(col1, col2, tail = 2):
    """This function performs a Spearmans correlation on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.SpearmansCorrelation(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.rho, TBase.t, TBase.df, TBase.prob
    else:
        return error

def DoRankSums(col1, col2, tail = 2):
    """This function performs a Wilcoxon rank sums test on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.RankSums(col1, col2)
    TBase.TwoSampleSignTextCorrelation(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.z, TBase.prob
    else:
        return error

def DoSignedRanks(col1, col2, tail = 2):
    """This function performs a Wilcoxon signed ranks test on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.SignedRanks(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.z, TBase.wt, TBase.prob
    else:
        return error

def DoMannWhitneyTest(col1, col2, tail = 2):
    """This function performs a Mann-Whitney U test on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.MannWhitneyU(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.bigu, TBase.smallu, TBase.z, TBase.prob
    else:
        return error

def DoLinearRegression(col1, col2, tail = 2):
    """This function performs a 2-sample sign test on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.LinearRegression(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.df, TBase.r, TBase.slope, TBase.intercept, \
                                    TBase.sterrest, TBase.prob
    else:
        return error

def DoPairedPermutation(col1, col2, tail = 2):
    """This function performs a 2-sample sign test on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.PairedPermutation(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.nperm, TBase.prob
    else:
        return error

# Three+ sample tests:

# Probability values
def GetChiProb(chisq, df):
    """This function takes the chi square value and the df and returns the
    p-value"""
    return salstat_stats.chisqprob(chisq, df)

def GetInverseChiProb(prob, df):
    """This function returns a chi value that matches the probability and
    df passed"""
    return salstat_stats.inversechi(prob, df)

def GetZProb(z):
    """This function returns the probability of z"""
    return salstat_stats.zprob(z)

def GetKSProb(ks):
    """This function returns the probability of a Kolmogorov-Smirnov test
    being significant"""
    return salstat_stats.ksprob(ks)

def GetTProb(t, df):
    """Gets the p-value for the passed t statistic and df"""
    return salstat_stats.betai(0.5*self.df,0.5,float(self.df)/(self.df+ \
                                    self.t*self.t))

def GetFProb(f, df1, df2):
    """This returns the p-value of the F-ratio and the 2 df's passed"""
    return salstat_stats.fprob(df1, df2, f)

def GetInverseFProb(prob, df1, df2):
    """Returns the f-ratio of the given p-value and df's"""
    return salstat_stats.inversef(prob, df1, df2)

#---------------------------------------------------------------------------
# Creating HTML document
def CreateHTMLDoc():
    try:
        fin = open("htmlbase.html",'r')
        page = fin.read()
        fin.close()
    except IOError:
        page = """<!DOCTYPE html>\n<html>\n    <head>\n        <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>\n        <script src="http://code.highcharts.com/highcharts.js"></script>\n        <script src="http://code.highcharts.com/modules/exporting.js"></script>\n        <script src="/js/themes/gray.js"></script>\n        <style>\n            body { font-family: helvectica, arial, \'lucida sans\'; }\n        </style>\n    </head>\n    <body>\n        <a href="http://www.salstat.com" alt="Go to the Salstat home page"><img src="http://bit.ly/1fqFdQm" alt="Salstat Statistics" style="float: right;"></a>\n        <h2>Salstat Statistics</h2>\n\n\n"""   
    return page

#---------------------------------------------------------------------------
# main loop
if __name__ == '__main__':
    import sys
    # find init file and read otherwise create it
    try:
        fname = sys.argv[1]
    except IndexError:
        fname = None
    ini = GetInits()
    historyClass = History()
    hist = historyClass
    app = wx.App()
    ico = wx.Icon('icons/PurpleIcon05_32.png',wx.BITMAP_TYPE_PNG)
    frame = DataFrame(None, sys.stdout, filename=fname)
    frame.grid.SetFocus()
    output = OutputSheet(frame, -1)
    output.Show(True)
    frame.Show(True)
    app.MainLoop()

#--------------------------------------------------------------------------
