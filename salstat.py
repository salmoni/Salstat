#!/usr/local/bin/python

"""SalStat Statistics Package. Copyright 2002 Alan James Salmoni. Licensed 
under the GNU General Public License (GPL). See the file COPYING for full
details of this license. """

# import wx stuff
from __future__ import unicode_literals
import codecs
import wx
from wx.stc import *
import wx.grid as gridlib
import gridbase 
import wx.html as htmllib
import wx.html2 as html2lib
import BeautifulSoup as BS
#import xlrd, xlwt # import xls format
import string, os, os.path, pickle, csv, sys
import urlparse, urllib, requests

# import SalStat specific modules
import salstat_stats, images, tabler, ChartWindow
import DescriptivesFrame, PrefsFrame
import MetaGrid, AllRoutines, ImportCSV, ImportSS, ImportHTML, Inferentials
import sas7bdat as sas
import TestThreeConditions
import exportSQLite
import numpy, math
import numpy.ma as ma

from xml.dom import minidom

#---------------------------------------------------------------------------
# set up id's for menu events - all on menu, some also available elsewhere
ID_FILE_NEW = wx.NewId()
ID_FILE_NEWOUTPUT = wx.NewId()
ID_FILE_OPEN = wx.NewId()
ID_FILE_URL = wx.NewId()
ID_FILE_DB = wx.NewId()
ID_FILE_SAVE = wx.NewId()
ID_FILE_SAVEAS = wx.NewId()
ID_FILE_EXPORT = wx.NewId()
ID_FILE_PRINT = wx.NewId()
ID_FILE_EXIT = wx.NewId()
ID_EDIT_UNDO = wx.NewId()
ID_EDIT_REDO = wx.NewId()
ID_EDIT_CUT = wx.NewId()
ID_EDIT_COPY = wx.NewId()
ID_EDIT_PASTE = wx.NewId()
ID_EDIT_SELECTALL = wx.NewId()
ID_EDIT_FIND = wx.NewId()
ID_EDIT_DELETECOL = wx.NewId()
ID_EDIT_DELETEROW = wx.NewId()
ID_EDIT_INSERTCOL = wx.NewId()
ID_EDIT_INSERTROW = wx.NewId()
ID_PREF_DATA = wx.NewId()
ID_PREF_VARIABLES = wx.NewId()
ID_PREF_GRID = wx.NewId()
ID_PREF_CELLS = wx.NewId()
ID_PREF_FONTS = wx.NewId()
ID_PREF_GEN = wx.NewId()
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
ID_OFILE_QUIT = wx.NewId()
ID_OEDIT_UNDO = wx.NewId()
ID_OEDIT_REDO = wx.NewId()
ID_OEDIT_CUT = wx.NewId()
ID_OEDIT_COPY = wx.NewId()
ID_OEDIT_PASTE = wx.NewId()
ID_OEDIT_SELECTALL = wx.NewId()
ID_OEDIT_FIND = wx.NewId()
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
ID_FIND_STRING = wx.NewId()

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
HOME = os.getcwd()+'/'
base_file_name = os.path.abspath(__file__)
basedir, script_name = os.path.split(base_file_name)

if wx.Platform == '__WXMSW__':
    face1 = 'Courier New'
    face2 = 'Times New Roman'
    face3 = 'Courier New'
    fontsizes = [7,8,10,12,16,22,30]
    pb = 12
    wind = 50
    DOCDIR = 'c:\My Documents'
    INITDIR = os.getcwd()
    # I got the following lines from the wxPython group but it's a red herring
    # it was to ensure Javascript files would load properly.
    # The solution was to use WebView.LoadURL not WebView.SetPage :-)
    import _winreg as wreg
    current_file = __file__
    key = wreg.CreateKey(wreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Internet Explorer\\Main\\FeatureControl\\FEATURE_BROWSER_EMULATION")
    wreg.SetValueEx(key, current_file, 0, wreg.REG_DWORD, 10001)
else:
    face1 = 'Helvetica'
    face2 = 'Times'
    face3 = 'Courier'
    fontsizes = [10,12,14,16,19,24,32]
    pb = 12
    wind = 50
    DOCDIR = os.environ['HOME']
    INITDIR = DOCDIR

def FileToURL(path):
    return urlparse.urljoin('file:', urllib.pathname2url(path))

class History:
    def __init__(self):
        self.history = '' # change this for the proper DTD please!

    def AppendEvent(self, xmltags):
        self.history = self.history + xmltags

    def ClearHistory(self):
        self.history = ''

class SaveDialog(wx.Dialog):
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
        saveButton.SetDefault()
        self.Layout()
        wx.EVT_BUTTON(self, 331, self.SaveData)
        wx.EVT_BUTTON(self, 332, self.DiscardData)
        wx.EVT_BUTTON(self, 333, self.CancelDialog)

    def SaveData(self, event):
        self.EndModal(2)
        self.ExitVal = 2

    def DiscardData(self, event):
        self.EndModal(3)
        self.ExitVal = 3

    def CancelDialog(self, event):
        self.EndModal(4)
        self.ExitVal = 4

    def GetVals(self):
        return self.ExitVal

################################################
# wx.FileDialog to retrieve file name. Needed before we can do anything

class GetFilename(object):
    def __init__(self, parent, startDir):
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
# method to calculate the descriptives with multiple grouping variables
def GetGroups(groupingvars):
    groups = []
    k = len(groupingvars)
    N = len(groupingvars[0])
    for idx in range(N):
        row = [var[idx] for var in groupingvars]
        if row not in groups:
            groups.append(row)
    groups.sort()
    return groups

def ExtractGroupsData(group, groupingvars, variable):
    N = len(variable)
    if isinstance(variable, list):
        data = []
        for idx in range(N):
            row = [element[idx] for element in groupingvars]
            if group == row:
                data.append(variable[idx])
        return data
    else:
        indices = []
        for idx in range(N):
            row = [element[idx] for element in groupingvars]
            if group == row:
                indices.append(True)
            else:
                indices.append(False)
        indices = ma.array(indices)
        return variable[indices]

def ConvertToNumbers(dataIn, missingvalues=[]):
    maxIdx = len(dataIn)
    data = ma.zeros(maxIdx,dtype='float')
    for row in range(maxIdx):
        val = dataIn[row]
        if (val in missingvalues):
            data[row] = ma.masked
        else:
            try:
                data[row] = float(val)
                if math.isnan(data[row]):
                    data[row] = ma.masked
            except ValueError:
                data[row] = ma.masked
    return data


def GroupedDescriptives(groups, groupingvars, variables, stats, groupnames, varnames,alpha):
    notests = ['Frequencies','Proportions','Percentages', 'Relative frequency of the mode', \
            'Trimmed mean', 'Bi-trimmed mean', 'Mode', 'Moment']
    table = '<h3>Descriptive statistics</h3>\n<table class="table table-striped">\n'
    table += '\t<tr><th>Variable</th>'
    for groupname in groupnames:
        table += '<th>%s</th>'%(groupname)
    for stat in stats:
        if stat not in notests:
            table += '<th>%s</th>'%(stat)
            if stat == "Count":
                table += '<th>%s</th>'%("Missing")
    table += '</tr>\n'
    k = len(groups)
    for idx, var in enumerate(variables):
        table += '\t<tr>'
        #for varname in scorenames:
        table += '<td rowspan="%d">%s</td>'%(k, varnames[idx])
        for group in groups:
            for element in group:
                table += '<td>%s</td>'%element
            data = ExtractGroupsData(group, groupingvars, var)
            data = ConvertToNumbers(data)
            if "Count" in stats:
                val = AllRoutines.Count(data)
                table += '<td>%s</td>'%str(val)
            if "Count" in stats:
                val = AllRoutines.NumberMissing(data)
                table += '<td>%s</td>'%str(val)
            if "Sum" in stats:
                val = AllRoutines.Sum(data)
                table += '<td>%s</td>'%str(val)
            if "Minimum" in stats:
                val = AllRoutines.Minimum(data)
                table += '<td>%s</td>'%str(val)
            if "Maximum" in stats:
                val = AllRoutines.Maximum(data)
                table += '<td>%s</td>'%str(val)
            if "Range" in stats:
                val = AllRoutines.Range(data)
                table += '<td>%s</td>'%str(val)
            if "Cumulative sum" in stats:
                val = AllRoutines.CumSum(data)
                table += '<td>%s</td>'%str(val)
            if "Cumulative product" in stats:
                val = AllRoutines.CumProd(data)
                table += '<td>%s</td>'%str(val)
            if "Cumulative percent" in stats:
                val = AllRoutines.CumPercent(data)
                table += '<td>%s</td>'%str(val)
            if "Mean" in stats:
                val = AllRoutines.Mean(data)
                table += '<td>%s</td>'%str(val)
            if "Median" in stats:
                val = AllRoutines.Median(data)
                table += '<td>%s</td>'%str(val)
            if "Quartiles" in stats:
                val = AllRoutines.Quartiles(data)
                table += '<td>%s, %s</td>'%(str(val[0]), str(val[1]))
            if "Tukey's hinges" in stats:
                val = AllRoutines.TukeyQuartiles(data)
                table += '<td>%s, %s</td>'%(str(val[0]), str(val[1]))
            if "Moore & McCabe's hinges" in stats:
                val = AllRoutines.MooreQuartiles(data)
                table += '<td>%s, %s</td>'%(str(val[0]),str(val[1]))
            if "S-Plus quantiles" in stats:
                val = AllRoutines.SPQuantile(data,alpha)
                table += '<td>%s</td>'%str(val)
            if "SPSS quantiles" in stats:
                val = AllRoutines.TradQuantile(data,alpha)
                table += '<td>%s</td>'%str(val)
            if "Mid-step quantiles" in stats:
                val = AllRoutines.MidstepQuantile(data,alpha)
                table += '<td>%s</td>'%str(val)
            if "Quantile 1 (Hyndman & Fan)" in stats:
                val = AllRoutines.Q1(data,alpha)
                table += '<td>%s</td>'%str(val)
            if "Quantile 2 (Hyndman & Fan)" in stats:
                val = AllRoutines.Q2(data,alpha)
                table += '<td>%s</td>'%str(val)
            if "Quantile 3 (Hyndman & Fan)" in stats:
                val = AllRoutines.Q3(data,alpha)
                table += '<td>%s</td>'%str(val)
            if "Quantile 4 (Hyndman & Fan)" in stats:
                val = AllRoutines.Q4(data,alpha)
                table += '<td>%s</td>'%str(val)
            if "Quantile 5 (Hyndman & Fan)" in stats:
                val = AllRoutines.Q5(data,alpha)
                table += '<td>%s</td>'%str(val)
            if "Quantile 6 (Hyndman & Fan)" in stats:
                val = AllRoutines.Q6(data,alpha)
                table += '<td>%s</td>'%str(val)
            if "Quantile 7 (Hyndman & Fan)" in stats:
                val = AllRoutines.Q7(data,alpha)
                table += '<td>%s</td>'%str(val)
            if "Quantile 8 (Hyndman & Fan)" in stats:
                val = AllRoutines.Q8(data,alpha)
                table += '<td>%s</td>'%str(val)
            if "Quantile 9 (Hyndman & Fan)" in stats:
                val = AllRoutines.Q9(data,alpha)
                table += '<td>%s</td>'%str(val)
            if "Interquartile range" in stats:
                val = AllRoutines.InterquartileRange(data)
                table += '<td>%s</td>'%str(val)
            if "Sum of squares" in stats:
                val = AllRoutines.SS(data)
                table += '<td>%s</td>'%str(val)
            if "Sum of squared deviations" in stats:
                val = AllRoutines.SSDevs(data)
                table += '<td>%s</td>'%str(val)
            if "Variance (sample)" in stats:
                val = AllRoutines.SampVar(data)
                table += '<td>%s</td>'%str(val)
            if "Variance (population)" in stats:
                val = AllRoutines.PopVar(data)
                table += '<td>%s</td>'%str(val)
            if "Standard deviation (sample)" in stats:
                val = AllRoutines.SampStdDev(data)
                table += '<td>%s</td>'%str(val)
            if "Standard deviation (population)" in stats:
                val = AllRoutines.PopStdDev(data)
                table += '<td>%s</td>'%str(val)
            if "Standard error" in stats:
                val = AllRoutines.StdErr(data)
                table += '<td>%s</td>'%str(val)
            if "Coefficient of variation" in stats:
                val = AllRoutines.CoeffVar(data)
                table += '<td>%s</td>'%str(val)
            if "Median absolute deviation" in stats:
                val = AllRoutines.MAD(data)
                table += '<td>%s</td>'%str(val)
            if "Geometric mean" in stats:
                val = AllRoutines.GeometricMean(data)
                table += '<td>%s</td>'%str(val)
            if "Harmonic mean" in stats:
                val = AllRoutines.HarmonicMean(data)
                table += '<td>%s</td>'%str(val)
            if "Mean of successive squared differences" in stats:
                val = AllRoutines.MSSD(data)
                table += '<td>%s</td>'%str(val)
            if "Skewness" in stats:
                val = AllRoutines.Skewness(data)
                table += '<td>%s</td>'%str(val)
            if "Kurtosis" in stats:
                val = AllRoutines.Kurtosis(data)
                table += '<td>%s</td>'%str(val)
            """
            if "Trimmed mean" in stats:
                val = AllRoutines.TrimmedMean(data,alpha)
                table += '<td>%s</td>'%str(val)
            """

            table += '</tr>\n'
        table += '</tr>\n'
    table += '</table>\n<p /><br />\n'
    output.Addhtml(table)

#---------------------------------------------------------------------------
# class to output the results of several "descriptives" in one table
class ManyDescriptives:
    def __init__(self, stats, variables, variablesr, names, alpha):
        #__x__ = len(ds)
        str2 = '<h3>Descriptive statistics</h3>\n<table class="table table-striped">'
        outlist = ['Statistic']
        for name in names:
            outlist.append(name)
        ln = tabler.vtable(outlist)
        str2 = str2 + ln

        if "Count" in stats:
            outlist = ['N']
            for var in variables:
                #outlist.append(i.N)
                outlist.append(AllRoutines.Count(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln
            outlist = ["Missing"]
            for var in variables:
                outlist.append(AllRoutines.NumberMissing(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Sum" in stats:
            outlist = ['Sum']
            for var in variables:
                outlist.append(AllRoutines.Sum(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Minimum" in stats:
            outlist = ['Minimum']
            for var in variables:
                outlist.append(AllRoutines.Minimum(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Maximum" in stats:
            outlist = ['Maximum']
            for var in variables:
                outlist.append(AllRoutines.Maximum(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Range" in stats:
            outlist = ['Range']
            for var in variables:
                outlist.append(AllRoutines.Range(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Midrange" in stats:
            outlist = ['Midrange']
            for var in variables:
                outlist.append(AllRoutines.Midrange(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Relative frequency of the mode" in stats:
            outlist = ['RelFreqMode']
            for var in variables:
                outlist.append(AllRoutines.RelFreqMode(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Cumulative sum" in stats:
            outlist = ['CumSum']
            for var in variables:
                outlist.append(AllRoutines.CumSum(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Cumulative product" in stats:
            outlist = ['CumProduct']
            for var in variables:
                outlist.append(AllRoutines.CumProduct(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Cumulative percent" in stats:
            outlist = ['CumPercent']
            for var in variables:
                outlist.append(AllRoutines.CumPercent(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Mean" in stats:
            outlist = ['Mean']
            for var in variables:
                outlist.append(AllRoutines.Mean(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Median" in stats:
            outlist = ['Median']
            for var in variables:
                outlist.append(AllRoutines.Median(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Tukey's hinges" in stats:
            outlist = ["Tukey's hinges"]
            for var in variables:
                outlist.append(AllRoutines.TukeyQuartiles(var))
            ln = tabler.tableHinges(outlist)
            str2 = str2 + ln

        if "Moore & McCabe's hinges" in stats:
            outlist = ["Moore & McCabe's hinges"]
            for var in variables:
                outlist.append(AllRoutines.MooreQuartiles(var))
            ln = tabler.tableHinges(outlist)
            str2 = str2 + ln

        if "Interquartile range" in stats:
            outlist = ["Interquartile range"]
            for var in variables:
                outlist.append(AllRoutines.InterquartileRange(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Sum of squares" in stats:
            outlist = ["Sum of squares"]
            for var in variables:
                outlist.append(AllRoutines.SS(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Sum of squared deviations" in stats:
            outlist = ["Sum of squared deviations"]
            for var in variables:
                outlist.append(AllRoutines.SSDevs(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Variance (sample)" in stats:
            outlist = ['Variance (sample)']
            for var in variables:
                outlist.append(AllRoutines.SampVar(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Variance (population)" in stats:
            outlist = ['Variance (population)']
            for var in variables:
                outlist.append(AllRoutines.PopVar(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Standard deviation (sample)" in stats:
            outlist = ['Standard Deviation (sample)']
            for var in variables:
                outlist.append(AllRoutines.SampStdDev(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Standard deviation (population)" in stats:
            outlist = ['Standard deviation (population)']
            for var in variables:
                outlist.append(AllRoutines.PopStdDev(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Standard error" in stats:
            outlist = ['Standard error']
            for var in variables:
                outlist.append(AllRoutines.StdErr(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Quartiles" in stats:
            outlist = ['Quartiles']
            for var in variables:
                val = AllRoutines.Quartiles(var)
                outlist.append((val[0], val[2]))
            ln = tabler.tableHinges(outlist)
            str2 = str2 + ln

        if "Coefficient of variation" in stats:
            outlist = ['Coefficient of variation']
            for var in variables:
                outlist.append(AllRoutines.CoeffVar(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Median absolute deviation" in stats:
            outlist = ['Median absolute deviation']
            for var in variables:
                outlist.append(AllRoutines.MAD(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Trimmed mean" in stats:
            outlist = ['Trimmed mean']
            for var in variables:
                outlist.append(AllRoutines.TrimmedMean(var,alpha))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Geometric mean" in stats:
            outlist = ['Geometric mean']
            for var in variables:
                outlist.append(AllRoutines.GeometricMean(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Harmonic mean" in stats:
            outlist = ['Harmonic mean']
            for var in variables:
                outlist.append(AllRoutines.HarmonicMean(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Mean of subsequent squared differences" in stats:
            outlist = ['Mean of subsequent squared differences']
            for var in variables:
                outlist.append(AllRoutines.MSSD(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Skewness" in stats:
            outlist = ['Skewness']
            for var in variables:
                outlist.append(AllRoutines.Skewness(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "Kurtosis" in stats:
            outlist = ['Kurtosis']
            for var in variables:
                outlist.append(AllRoutines.Kurtosis(var))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        if "S-Plus quantiles" in stats:
            outlist = ['S-Plus quantiles']
            for var in variables:
                outlist.append(AllRoutines.SPQuantile(var,alpha))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln
        if "SPSS quantiles" in stats:
            outlist = ['SPSS quantiles']
            for var in variables:
                outlist.append(AllRoutines.TradQuantile(var,alpha))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln
        if "Mid-step quantiles" in stats:
            outlist = ['Mid-step quantiles']
            for var in variables:
                outlist.append(AllRoutines.MidstepQuantiles(var,alpha))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln
        if "Quantile 1 (Hyndman & Fan)" in stats:
            outlist = ['Quantile 1 (Hyndman & Fan)']
            for var in variables:
                outlist.append(AllRoutines.Q1(var,alpha))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln
        if "Quantile 2 (Hyndman & Fan)" in stats:
            outlist = ['Quantile 2 (Hyndman & Fan)']
            for var in variables:
                outlist.append(AllRoutines.Q2(var,alpha))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln
        if "Quantile 3 (Hyndman & Fan)" in stats:
            outlist = ['Quantile 3 (Hyndman & Fan)']
            for var in variables:
                outlist.append(AllRoutines.Q3(var,alpha))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln
        if "Quantile 4 (Hyndman & Fan)" in stats:
            outlist = ['Quantile 4 (Hyndman & Fan)']
            for var in variables:
                outlist.append(AllRoutines.Q4(var,alpha))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln
        if "Quantile 5 (Hyndman & Fan)" in stats:
            outlist = ['Quantile 5 (Hyndman & Fan)']
            for var in variables:
                outlist.append(AllRoutines.Q5(var,alpha))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln
        if "Quantile 6 (Hyndman & Fan)" in stats:
            outlist = ['Quantile 6 (Hyndman & Fan)']
            for var in variables:
                outlist.append(AllRoutines.Q6(var,alpha))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln
        if "Quantile 7 (Hyndman & Fan)" in stats:
            outlist = ['Quantile 7 (Hyndman & Fan)']
            for var in variables:
                outlist.append(AllRoutines.Q7(var,alpha))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln
        if "Quantile 8 (Hyndman & Fan)" in stats:
            outlist = ['Quantile 8 (Hyndman & Fan)']
            for var in variables:
                outlist.append(AllRoutines.Q8(var,alpha))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln
        if "Quantile 9 (Hyndman & Fan)" in stats:
            outlist = ['Quantile 9 (Hyndman & Fan)']
            for var in variables:
                outlist.append(AllRoutines.Q9(var,alpha))
            ln = tabler.vtable(outlist)
            str2 = str2 + ln

        """
        if "Trimmed mean" in stats:
            val = AllRoutines.TrimmedMean(data,alpha)
            table += '<td>%s</td>'%str(val)
        """

        str2 += '</table>\n'

        if ("Frequencies" in stats) \
                or ("Proportions" in stats) \
                or ("Percentages" in stats):
            for idx, var in enumerate(variablesr):
                vals = {}
                if "Frequencies" in stats:
                    values, freqs = AllRoutines.Frequencies(var)
                    ln = tabler.vtable(['Number of items',len(values)])
                    str2 += ln
                    vals['values'] = values
                    vals['freqs'] = freqs
                else:
                    vals['freqs'] = None
                if "Proportions" in stats:
                    values, props = AllRoutines.Proportions(var)
                    vals['props'] = props
                else:
                    vals['props'] = None
                if "Percentages" in stats:
                    values, percs = AllRoutines.Percentages(var)
                    vals['percs'] = percs
                else:
                    vals['percs'] = None
                ln = tabler.tableMultiples(vals, names[idx])
                str2 += ln

        if "Mode" in stats:
            outlist = []
            for var in variables:
                outlist.append(AllRoutines.Mode(var))
            ln = tabler.tableMode(outlist)
            str2 = str2 + ln

        str2 += '<p /><br />\n'
        output.Addhtml(str2)

#---------------------------------------------------------------------------
# DescChoice-wx.CheckListBox with list of descriptive stats in it
class DescChoiceBox(wx.CheckListBox):
    def __init__(self, parent, id):
        self.test_list = AllRoutines.GetMostUsedTests()
        wx.CheckListBox.__init__(self, parent, -1, pos=(250,30), \
                                    size=(240,310), choices=self.test_list)
        self.SetChecked([0,1,2,5,6,7])

    def SelectAllDescriptives(self, event):
        for i in range(len(self.test_list)):
            self.Check(i, True)

    def SelectNoDescriptives(self, event):
        for i in range(len(self.test_list)):
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
        #self.scripted = wx.Editor(self,-1)
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
        toolBar.AddLabelTool(710, "Run script", wx.Bitmap("icons/IconNew.png"), shortHelp="Run this script now")
        toolBar.AddLabelTool(711, "Open", wx.Bitmap("icons/IconOpen.png"), shortHelp="Open a script from a file")
        toolBar.AddLabelTool(712, "Save", wx.Bitmap("icons/IconSave.png"), shortHelp="Save this script to file")
        toolBar.AddLabelTool(713, "Save As", wx.Bitmap("icons/IconSaveAs.png"), shortHelp="Save this script to a file")
        toolBar.AddLabelTool(714, "Print", wx.Bitmap("icons/IconPrint.png"), shortHelp="Print out this script")
        toolBar.AddLabelTool(715, "Cut", wx.Bitmap("icons/IconCut.png"), shortHelp="Cut selection to clipboard")
        toolBar.AddLabelTool(716, "Copy", wx.Bitmap("icons/IconCopy.png"), shortHelp="Copy selection to clipboard")
        toolBar.AddLabelTool(717, "Paste", wx.Bitmap("icons/IconPaste.png"), shortHelp="Paste selection from clipboard")
        toolBar.AddLabelTool(718, "Help", wx.Bitmap("icons/IconHelp.png"), shortHelp="See the help documents")
        """
        toolBar.AddLabelTool(710, "Run Script",GoIcon,"Run the Script")
        toolBar.AddLabelTool(711, OpenIcon,"Open","Open Script from a File")
        toolBar.AddLabelTool(712, SaveIcon,"Save","Save Script to a file")
        toolBar.AddLabelTool(713, SaveAsIcon,"Save As","Save Script under \
                                    a new filename")
        toolBar.AddLabelTool(714, PrintIcon,"Print","Print Out Script")
        toolBar.AddLabelTool(715, CutIcon, "Cut", "Cut selection to \
                                    clipboard")
        toolBar.AddLabelTool(716, CopyIcon, "Copy", "Copy selection to \
                                    clipboard")
        toolBar.AddLabelTool(717, PasteIcon, "Paste", "Paste selection \
                                    from clipboard")
        toolBar.AddLabelTool(718, HelpIcon, "Help", "Get some help!")
        """
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
        wx.EVT_TOOL(self, 210, self.GoBackPressed)
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
        wx.EVT_TOOL(self, 210, self.GoBackPressed)
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
        self.parent = parent
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
        file_menu.Append(ID_OFILE_QUIT, '&Quit\tCTRL+Q')
        edit_menu.Append(ID_OEDIT_UNDO, 'Undo\tCTRL+Z')
        edit_menu.Append(ID_OEDIT_REDO, 'Redo\tSHIFT+CTRL+Z')
        edit_menu.Append(ID_OEDIT_CUT, 'Cu&t\tCTRL+X')
        edit_menu.Append(ID_OEDIT_COPY, '&Copy\tCTRL+C')
        edit_menu.Append(ID_OEDIT_PASTE, '&Paste\tCTRL+V')
        edit_menu.Append(ID_OEDIT_SELECTALL, 'Select &All\tCTRL+A')
        edit_menu.Append(ID_OEDIT_FIND, "&Find...")
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
                                    wx.TB_FLAT|wx.TB_TEXT)
        toolBar.AddLabelTool(401, "New", wx.Bitmap("icons/IconNew.png"), shortHelp="Create a new data sheet")
        toolBar.AddLabelTool(402, "Open", wx.Bitmap("icons/IconOpen.png"), shortHelp="Open a data file")
        toolBar.AddLabelTool(403, "Save As", wx.Bitmap("icons/IconSaveAs.png"), shortHelp="Save these data to a new filename")
        toolBar.AddLabelTool(404, "Print", wx.Bitmap("icons/IconPrint.png"), shortHelp="Print this sheet")
        toolBar.AddLabelTool(405, "Help", wx.Bitmap("icons/IconHelp.png"), shortHelp="See help documentation")
        toolBar.SetToolBitmapSize((24,24))
        # more toolbuttons are needed: New Output, Save, Print, Cut, \
        # Variables, and Wizard creates the toolbar
        toolBar.Realize()
        self.SetToolBar(toolBar)
        self.CreateStatusBar()
        self.SetStatusText('Salstat statistics - results')
        self.htmlpage = html2lib.WebView.New(self)
        self.htmlpage.SetEditable(False)
        self.Addhtml('')
        self.printer = wx.Printout()
        wx.EVT_MENU(self, ID_OEDIT_UNDO, self.Undo)
        wx.EVT_MENU(self, ID_OEDIT_REDO, self.Redo)
        wx.EVT_MENU(self, ID_OEDIT_CUT, self.CutHTML)
        wx.EVT_MENU(self, ID_OEDIT_COPY, self.CopyHTML)
        wx.EVT_MENU(self, ID_OEDIT_PASTE, self.PasteHTML)
        wx.EVT_MENU(self, ID_OFILE_SAVEAS, self.SaveHtmlPage)
        wx.EVT_MENU(self, ID_OFILE_QUIT, self.parent.EndApplication)
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
        self.Bind(html2lib.EVT_WEBVIEW_NAVIGATING, self.OnWebViewNavigating, self.htmlpage)

    def OnWebViewNavigating(self, evt):
        """
        Interrupts an event when a user clicks on a hyperlink in the results page.
        It then uses this link to perform its next action. 
        This, of course, means I need to create a table of possible actions and
        ensure Salstat does the right thing.
        """
        action = evt.GetURL()
        #evt.Veto()

    def Undo(self, event):
        self.htmlpage.Undo()

    def Redo(self, event):
        self.htmlpage.Redo

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
            self.htmlpage.SetPage(data,HOME)
            self.htmlpage.Reload() # hack to make content appear
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
        htmlend = "\n\t</body>\n</html>"
        fout = codecs.open('tmp/output.html','w', encoding="utf-8")
        fout.write(self.WholeOutString+htmlend.encode('UTF-8'))
        fout.close()
        file_loc = FileToURL(basedir+os.sep+'tmp/output.html')
        self.htmlpage.LoadURL(file_loc)
        #self.htmlpage.SetPage(self.WholeOutString+htmlend,HOME)

    def PrintOutput(self, event):
        self.htmlpage.Print()

    def DoNothing(self, event):
        pass

    def ClearAll(self, event):
        # check output has been saved
        self.WholeOutString = CreateHTMLDoc()
        htmlend = "\n\t</body>\n</html>"
        self.htmlpage.SetPage(self.WholeOutString+htmlend,HOME)
        #self.htmlpage.Reload()

    def NewHTML(self, html):
        self.ClearAll(None)
        self.WholeOutString = html
        htmlend = "\n\t</body>\n</html>"
        self.htmlpage.SetPage(self.WholeOutString+htmlend,HOME)

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
        self.okaybutton.SetDefault()
        cancelbutton = wx.Button(self,104,"Cancel",wx.Point(100,winheight-35),\
                                    wx.Size(BWidth, BHeight))
        self.DescChoice = DescChoiceBox(self, 104)
        self.stats = []
        wx.EVT_BUTTON(self.okaybutton, 103, self.OnOkayButton)
        wx.EVT_BUTTON(cancelbutton, 104, self.OnCloseOneCond)
        wx.EVT_BUTTON(allbutton, 105, self.DescChoice.SelectAllDescriptives)
        wx.EVT_BUTTON(nonebutton, 106, self.DescChoice.SelectNoDescriptives)
        # enable the okay button if something is entered as a hyp mean.
        # Can the wx.TextCtrl allow only numbers to be entered?
        #wx.EVT_TEXT(self.UserMean, 107, self.EnteredText) # doesn't work on Windows!

    def OnOkayButton(self, event):
        colNum = self.ColBox.GetSelection()
        name = frame.grid.GetColLabelValue(colNum)
        if (colNum < 0): # add top limits of grid to this
            self.Close(True)
            return
        try:
            umean = float(self.UserMean.GetValue())
        except:
            output.Addhtml('<p class="text-warning">Cannot do test - no user \
                                    hypothesised mean specified')
            self.Close(True)
            return
        #x = frame.grid.GetVariableData(x1,'float')
        data = frame.grid.GetVariableData(colNum,'float')
        raw_data = frame.grid.GetVariableData(colNum,'string')
        self.stats = self.DescChoice.GetCheckedStrings()
        ManyDescriptives(self.stats, [data], [raw_data], [name], None)
        # One sample t-test
        if self.TestChoice.IsChecked(0):
            output.Addhtml('<h3>One sample t-test</h3>')
            df, t, prob, d = Inferentials.OneSampleTTest(data, umean)
            if (prob == -1.0):
                output.Addhtml('<p class="text-warning">All elements are the same, \
                                    test not possible</p>')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    prob = prob / 2
                variables = [['Variable', name],
                        ['Hypothetic mean', umean],
                        ['df', df],
                        ['t',t],
                        ['p',prob],
                        ["Cohen's d",d]]
                quote = "<b>Quote:</b> <i>t</i>(%d)=%2.3f, <i>p</i>=%1.3f, <i>d</i>=%1.3f<br />"%\
                        (df, t, prob, d)
                ln = '<br />' + tabler.table(variables) + quote + '<p /><br />'
                output.Addhtml(ln)
                #now draw up the xml history stuff
                xmlevt = '<analyse test="one sample t-test" column = "'+str(colNum)
                xmlevt = xmlevt+' hyp_value = "'+str(umean)+'" tail="'
                if (self.hypchoice.GetSelection() == 0):
                    xmlevt = xmlevt+'1">'
                else:
                    xmlevt = xmlevt+'2">'
                xmlevt = xmlevt+'t ('+str(df)+') = '+str(t)+', p = '+str(prob)
                xmlevt = xmlevt+'</analyse>'
                hist.AppendEvent(xmlevt)
        # One sample sign test
        if self.TestChoice.IsChecked(1):
            output.Addhtml('<H3>One sample sign test</H3>')
            nplus, nminus, nequal, z, prob = Inferentials.OneSampleSignTest(data, umean)
            if (prob == -1.0):
                output.Addhtml('<p class="text-warning">All data are the same - no \
                                    analysis is possible</p>')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    prob = prob / 2
                variables = [['Variable', name],
                        ['Hypothetic mean', umean],
                        ['Positive',nplus],
                        ['Negative',nminus],
                        ['Equal',nequal],
                        ['Total N', nplus+nminus+nequal],
                        ['Z',z],
                        ['p',prob]]
                quote = "<i>Z</i>=%1.3f, <i>p</i>=%1.3f<br />"%(z, prob)
                ln = '<br />' + tabler.table(variables) + quote + '<p /><br />'
                output.Addhtml(ln)
        # chi square test for variance
        if self.TestChoice.IsChecked(2):
            output.Addhtml('<H3>One sample chi square</H3>')
            df, chisquare, prob = Inferentials.ChiSquareVariance(data, umean)
            if (self.hypchoice.GetSelection() == 0):
                prob = prob / 2
            if (prob == None):
                prob = 1.0
                df = 0
                chisquare = 0.0
            variables = [['Variable', name],
                    ['Hypothetic mean', umean],
                    ['df', df],
                    ['Chi',chisquare],
                    ['p',prob]]
            ln = tabler.table(variables)
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
        okaybutton.SetDefault()
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

    def OnOkayButton(self, event):
        x1 = self.ColBox1.GetSelection()
        y1 = self.ColBox2.GetSelection()
        name1 = frame.grid.GetColLabelValue(x1)
        name2 = frame.grid.GetColLabelValue(y1)
        if (x1 < 0) or (y1 < 0):
            self.Close(True)
            return
        x = frame.grid.GetVariableData(x1, 'float')
        y = frame.grid.GetVariableData(y1,'float')
        xr = frame.grid.GetVariableData(x1, 'string')
        yr = frame.grid.GetVariableData(y1,'string')
        self.stats = self.DescChoice.GetCheckedStrings()
        ManyDescriptives(self.stats, [x,y], [xr, yr], [name1,name2], None)

        # chi square test
        if self.paratests.IsChecked(0):
            output.Addhtml('<H3>Chi square</H3>')
            N, chisq, df, prob = Inferentials.ChiSquare(x)
            if (prob == -1.0):
                output.Addhtml('<p class="text-warning">Cannot do chi square - unequal data sizes</p>')
            else:
                variables = [['Variable 1', name1],
                        ['Variable 2', name2],
                        ['df', df],
                        ['Chi',chisq],
                        ['p',prob]]
                quote = "<i>&Chi;</i><sup>2</sup> (%d, N=%d) = %2.3f, <i>p</i>=%1.4f"%(df, N, chisq, prob)
                ln = '<br />' + tabler.table(variables) + quote + '<p /><br />'
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
                df1, df2, f, prob = Inferentials.FTest(x, y, umean)
                if (self.hypchoice.GetSelection() == 0):
                    prob = prob / 2
                variables = [['Variable 1', name1],
                        ['Variable 2', name2],
                        ['df', '%d, %d'%(df1, df2)],
                        ['F',f],
                        ['p',prob]]
                quote = ""
                ln = '<br />' + tabler.table(variables) + quote + '<p /><br />'
                output.Addhtml(ln)

        # Kolmorogov-Smirnov 2 sample test
        if self.paratests.IsChecked(2):
            output.Addhtml('<h3>Kolmogorov-Smirnov test (unpaired)</h3>')
            d, prob = Inferentials.KolmogorovSmirnov(x, y)
            if (self.hypchoice.GetSelection() == 0):
                prob = prob / 2
            variables = [['Variable 1', name1],
                    ['Variable 2', name2],
                    ['d', d],
                    ['p',prob]]
            quote = ""
            ln = '<br />' + tabler.table(variables) + quote + '<p /><br />'
            output.Addhtml(ln)

        # Linear Regression
        if self.paratests.IsChecked(3):
            output.Addhtml('<h3>Linear Regression</h3>')
            slope, intercept, r, prob, st = Inferentials.linregress(x,y)
            #s, i, r, prob, st = salstat_stats.llinregress(x, y)
            if (prob == -1.0):
                output.Addhtml('<h3>Cannot do linear regression - unequal data sizes</p>')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    prob = prob / 2
                variables = [['Variable 1 on', name1],
                        ['Variable 2', name2],
                        ['Slope', slope],
                        ['Intercept',intercept],
                        ['R', r],
                        ['Est. Standard Error',st],
                        ['p',prob]]
                quote = ""
                ln = '<br />' + tabler.table(variables) + quote + '<p /><br />'
                output.Addhtml(ln)

        # Mann-Whitney U
        if self.paratests.IsChecked(4):
            output.Addhtml('<h3>Mann-Whitney U test (unpaired samples)</h3>')
            u, prob = Inferentials.MannWhitneyU(x, y)
            if (prob == -1.0):
                output.Addhtml('<p class="text-warning">Cannot do Mann-Whitney U test - all numbers are identical<p>')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    prob = prob / 2
                variables = [['Variable 1', name1],
                        ['Variable 2', name2],
                        ['U',u],
                        ['p',prob]]
                quote = "<b>Quote:</b> <i>U</i>=%2.3f, <i>p</i>=%1.3f<br />"%\
                        (u, prob)
                ln = '<br />' + tabler.table(variables) + quote + '<p /><br />'
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
            nplus, nminus, ntotal, z, prob = Inferentials.TwoSampleSignTest(x, y)
            if prob == -1.0:
                output.Addhtml('<p class="text-warning">Cannot do test - not paired samples</p>')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    prob = prob / 2
                variables = [['Variable 1', name1],
                        ['Variable 2', name2],
                        ['N (total)', ntotal],
                        ['Z',z],
                        ['p',prob]]
                #ln = '<br />' + tabler.table(variables) + quote + '<p /><br />'
                ln = '<br />' + tabler.table(variables) + '<p /><br />'
                output.Addhtml(ln)

        # Paired t-test
        if self.paratests.IsChecked(6):
            output.Addhtml('<h3>t-test paired</h3>')
            df, t, prob, d = Inferentials.TTestPaired(x, y)
            alpha = 0.95
            mean, meanm, meanp = Inferentials.ConfidenceIntervals(x-y, alpha)
            if (prob == -1.0):
                output.Addhtml('<p class="text-warning">Cannot do paired t test - unequal data sizes</p>')
            else:
                if self.hypchoice.GetSelection() == 0:
                    prob = TBase.prob / 2
                variables = [['Variable', "%s, %s"%(name1,name2)],
                        ['df', df],
                        ['t',t],
                        ['p',prob],
                        ["Cohen's d",d],
                        ["%d%% confidence intervals"%(alpha*100), "%s  %s"%(str(meanm), str(meanp))]]
                quote = "<b>Quote:</b> <i>t</i>(%d)=%2.3f, <i>p</i>=%1.3f, <i>d</i>=%1.3f<br />"%\
                        (df, t, prob, d)
                ln = '<br />' + tabler.table(variables) + quote + '<p /><br />'
                output.Addhtml(ln)

        # unpaired t-test
        if self.paratests.IsChecked(7):
            output.Addhtml('<h3>t-test unpaired</h3>')
            df, t, prob, d = Inferentials.TTestUnpaired(x, y)
            if (self.hypchoice.GetSelection() == 0):
                prob = prob / 2
            variables =[['Variable', "%s, %s"%(name1,name2)],
                    ['df', df],
                    ['t',t],
                    ['p',prob],
                    ["Cohen's d",d]]
            quote = "<b>Quote:</b> <i>t</i>(%d)=%2.3f, <i>p</i>=%1.3f, <i>d</i>=%1.3f<br />"%\
                    (df, t, prob, d)
            ln = '<br />' + tabler.table(variables) + quote + '<p /><br />'
            output.Addhtml(ln)

        # Wald-Wolfowitz runs test (no yet coded)
        if self.paratests.IsChecked(8):
            pass

        # Wilcoxon Rank Sums
        if self.paratests.IsChecked(9):
            output.Addhtml('<h3>Wilcoxon Rank Sums test (unpaired samples)</h3>')
            z, prob = Inferentials.RankSums(x, y)
            if (self.hypchoice.GetSelection() == 0):
                prob = prob / 2
            variables = [['Variable 1', name1],
                    ['Variable 2', name2],
                    ['z', z],
                    ['p',prob]]
            quote = "<b>Quote:</b> <i>z</i>=%2.3f, <i>p</i>=%1.3f<br />"%\
                    (z, prob)
            ln = '<br />' + tabler.table(variables) + quote + '<p /><br />'
            output.Addhtml(ln)

        # Wilcoxon Signed Ranks
        if self.paratests.IsChecked(10):
            output.Addhtml('<h3>Wilcoxon t (signed-ranks / paired samples)</h3>')
            T, prob = Inferentials.SignedRanks(x, y)
            if (prob == -1.0):
                output.Addhtml('<p class="text-warning">Cannot do Wilcoxon t test - unequal data sizes</p>')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    prob = prob / 2
                variables = [['Variable 1', name1],
                        ['Variable 2', name2],
                        ['T',T],
                        ['p',prob]]
                quote = "<b>Quote:</b> <i>U</i>=%2.3f, <i>p</i>=%1.3f<br />"%\
                        (T, prob)
                ln = '<br />' + tabler.table(variables) + quote + '<p /><br />'
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
        alltests = ['anova between subjects','anova within subjects']
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
        okaybutton.SetDefault()
        cancelbutton = wx.Button(self,517,"Cancel",wx.Point(100,winheight-35), \
                                    wx.Size(BWidth, BHeight))
        wx.EVT_BUTTON(okaybutton, 516, self.OnOkayButton)
        wx.EVT_BUTTON(cancelbutton, 517, self.OnCloseThreeCond)
        wx.EVT_BUTTON(allbutton, 518, self.DescChoice.SelectAllDescriptives)
        wx.EVT_BUTTON(nonebutton, 520, self.DescChoice.SelectNoDescriptives)

    def OnOkayButton(self, event):
        biglist = []
        biglistr = []
        names = []
        for i in range(len(self.colnums)):
            if self.ColChoice.IsChecked(i):
                tmplist = frame.grid.GetVariableData(self.colnums[i], 'float')
                biglist.append(tmplist)
                tmplist = frame.grid.GetVariableData(self.colnums[i], 'string')
                biglistr.append(tmplist)                
                names.append(frame.grid.GetColLabelValue(i))
        k = len(biglist)
        self.stats = self.DescChoice.GetCheckedStrings()
        ManyDescriptives(self, biglist, biglistr, names, None)
        if (len(biglist) < 2):
            output.Addhtml('<p><b>Not enough columns selected for \
                                    test!</b>')
            self.Close(True)
            return
        #single factor between subjects anova
        if self.TestChoice.IsChecked(0):
            # try to guess x and y
            anova = Inferentials.anovaBetweenPrep(biglist)
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
        okaybutton.SetDefault()
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
        x1 = len(frame.grid.GetVariableData(self.ColBox1.GetSelection(),'float'))
        x2 = len(frame.grid.GetVariableData(self.ColBox2.GetSelection(),'float'))
        if (x1 != x2):
            print "unequal"
            # disable some tests in the listbox
        else:
            print "equal"
            # enable all tests in the listbox

    def ChangeCol2(self, event):
        # check that len of 2 cols is equal, if not disable choices of test
        x1 = len(frame.grid.GetVariableData(self.ColBox1.GetSelection(),'float'))
        x2 = len(frame.grid.GetVariableData(self.ColBox2.GetSelection(),'float'))
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
        x = frame.grid.GetVariableData(x1, 'float')
        y = frame.grid.GetVariableData(y1, 'float')
        xr = frame.grid.GetVariableData(x1, 'string')
        yr = frame.grid.GetVariableData(y1, 'string')
        #TBase = salstat_stats.TwoSampleTests(x, y, name1, name2,xmiss,ymiss)
        self.stats = self.DescChoice.GetCheckedStrings()
        ManyDescriptives(self.stats, [x,y], [xr, yr], [name1,name2], None)
        
        # Kendalls tau correlation
        if self.paratests.IsChecked(0):
            output.Addhtml('<h3>Kendalls Tau correlation</h3>')
            tau, df, prob = Inferentials.KendallsTau(x, y)
            if (prob == -1.0):
                output.Addhtml('<p class="text-warning">Cannot do Kendall&#39;s tau correlation \
                                    - the data have unequal sizes<hr width="50%">')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    prob = prob / 2
                variables = [['Variable 1', name1],
                        ['Variable 2', name2],
                        ['Tau', tau],
                        ['df', df],
                        ['p',prob]]
                quote = "<b>Quote:</b> <i>Tau</i>(%d)=%1.3f, <i>p</i>=%1.4f<br />"%(df, tau, prob)
                ln = '<br />' + tabler.table(variables) + quote + '<p /><br />'
                output.Addhtml(ln)

        # Pearsons r correlation
        if self.paratests.IsChecked(1):
            output.Addhtml('<H3>Pearsons correlation</H3>')
            r, df, prob = Inferentials.PearsonR(x, y)
            if (prob == -1.0):
                output.Addhtml('<p class="text-warning">Cannot do Pearson&#39;s correlation \
                                    - the data have unequal sizes')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    prob = prob / 2
                variables = [['Variable 1', name1],
                        ['Variable 2', name2],
                        ['r',r],
                        ['df', df],
                        ['p',prob]]
                quote = "<b>Quote:</b> <i>r</i>(%d)=%1.3f, <i>p</i>=%1.4f<br />"%(df, r, prob)
                ln = '<br />' + tabler.table(variables) + quote + '<p /><br />'
                output.Addhtml(ln)

        # Point Biserial r
        if self.paratests.IsChecked(2):
            output.Addhtml('<H3>Point Biserial r correlation</H3>')
            r, df, prob = Inferentials.PointBiserial(x, y)
            if (prob == -1.0):
                output.Addhtml('<p class="text-warning">Cannot do Spearmans correlation \
                                    - the data have unequal sizes')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    prob = prob / 2
                variables = [['Variable 1', name1],
                        ['Variable 2', name2],
                        ['r',r],
                        ['df', df],
                        ['p',prob]]
                quote = "<b>Quote:</b> <i>r</i>(%d)=%1.3f, <i>p</i>=%1.4f<br />"%(df, r, prob)
                ln = '<br />' + tabler.table(variables) + quote + '<p /><br />'
                output.Addhtml(ln)

        # Spearmans rho correlation
        if self.paratests.IsChecked(3):
            output.Addhtml('<H3>Spearmans rho correlation</H3>')
            r, df, prob = Inferentials.SpearmanR(x, y)
            if (prob == -1.0):
                output.Addhtml('<p class="text-warning">Cannot do Spearmans correlation \
                                    - the data have unequal sizes')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    prob = prob / 2
                variables = [['Variable 1', name1],
                        ['Variable 2', name2],
                        ['r',r],
                        ['df', df],
                        ['p',prob]]
                quote = "<b>Quote:</b> <i>r</i>(%d)=%1.3f, <i>p</i>=%1.4f<br />"%(df, r, prob)
                ln = '<br />' + tabler.table(variables) + quote + '<p /><br />'
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
        self.menuNew = file_menu.Append(ID_FILE_NEW,'&New Data\tCTRL+N')
        #file_menu.Append(ID_FILE_NEWOUTPUT, 'New &Output Sheet')
        self.menuOpen = file_menu.Append(ID_FILE_OPEN, '&Open...\tCTRL+O')
        self.menuScrape = file_menu.Append(ID_FILE_URL, "Scrape URL...\tCTRL+U")
        self.menuOpenDB = file_menu.Append(ID_FILE_DB, "Open database...")
        file_menu.AppendSeparator()
        self.menuSave = file_menu.Append(ID_FILE_SAVE, '&Save\tCTRL+S')
        self.menuSaveAs = file_menu.Append(ID_FILE_SAVEAS, 'Save &As...\tSHIFT+CTRL+S')
        file_menu.AppendSeparator()
        self.menuPrint = file_menu.Append(ID_FILE_PRINT, '&Print...\tCTRL+P')
        file_menu.AppendSeparator()
        self.menuExit = file_menu.Append(ID_FILE_EXIT, 'Q&uit\tCTRL+Q')
        self.menuCut = edit_menu.Append(ID_EDIT_CUT, 'Cu&t\tCTRL+X')
        self.menuCopy = edit_menu.Append(ID_EDIT_COPY, '&Copy\tCTRL+C')
        self.menuPaste = edit_menu.Append(ID_EDIT_PASTE, '&Paste\tCTRL+V')
        self.menuSelectAll = edit_menu.Append(ID_EDIT_SELECTALL, 'Select &All\tCTRL+A')
        self.menuFind = edit_menu.Append(ID_EDIT_FIND, '&Find and Replace...\tCTRL+F')
        edit_menu.AppendSeparator()
        self.menuInsertCol = edit_menu.Append(ID_EDIT_INSERTCOL, "Insert column(s)")
        self.menuInsertRow = edit_menu.Append(ID_EDIT_INSERTROW, "Insert row(s)")
        edit_menu.AppendSeparator()
        self.menuDeleteCol = edit_menu.Append(ID_EDIT_DELETECOL, 'Delete Current Column')
        self.menuDeleteRow = edit_menu.Append(ID_EDIT_DELETEROW, 'Delete Current Row')
        self.menuData = prefs_menu.Append(ID_PREF_DATA, 'View data')
        self.menuVariables = prefs_menu.Append(ID_PREF_VARIABLES, 'View variables')
        self.menuPrefs = prefs_menu.Append(ID_PREF_GEN, 'Preferences...')
        self.menuDescribe = analyse_menu.Append(ID_PREPARATION_DESCRIPTIVES, 'Descriptive Statistics...')
        self.menuTransform = analyse_menu.Append(ID_PREPARATION_TRANSFORM, 'Transform Data...')
        analyse_menu.AppendSeparator()
        #preparation_menu.Append(ID_PREPARATION_OUTLIERS, 'Check for Outliers...')
        #preparation_menu.Append(ID_PREPARATION_NORMALITY, 'Check for Normal Distribution...')
        self.menuAnalyse1 = analyse_menu.Append(ID_ANALYSE_1COND, '&1 Condition Tests...')
        self.menuAnalyst2 = analyse_menu.Append(ID_ANALYSE_2COND, '&2 Condition Tests...')
        self.menuAnalyse3 = analyse_menu.Append(ID_ANALYSE_3COND, '&3+ Condition Tests...')
        self.menuAnalyseCorr = analyse_menu.Append(ID_ANALYSE_CORRELATION,'&Correlations...')
        #analyse_menu.Append(ID_ANALYSE_2FACT, '2+ &Factor Tests...')
        analyse_menu.AppendSeparator()
        #analyse_menu.Append(ID_ANALYSE_SCRIPT, 'Scripting Window...')
        self.menuChart = chart_menu.Append(ID_CHART_DRAW, 'Draw a chart...')
        # the bar chart is *not* ready yet!
        help_menu.Append(ID_HELP_WIZARD, '&What Test Should I Use...')
        help_menu.Append(ID_HELP_TOPICS, '&Topics...')
        help_menu.Append(ID_HELP_LICENCE, '&Licence...')
        help_menu.Append(wx.ID_ABOUT, '&About Salstat...')
        #set up menu bar
        menuBar = wx.MenuBar()
        menuBar.Append(file_menu, '&File')
        menuBar.Append(edit_menu, '&Edit')
        menuBar.Append(prefs_menu, '&Variables')
        #menuBar.Append(preparation_menu, 'P&reparation')
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
        TestIcon = images.getNewBitmap()
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
        toolBar.AddLabelTool(88, "Chart", wx.Bitmap("icons/IconChart.png"), shortHelp="View the chart window")
        toolBar.AddLabelTool(90, "Help", wx.Bitmap("icons/IconHelp.png"), shortHelp="Get help")
        toolBar.AddLabelTool(91, "TEST", wx.Bitmap("icons/IconNew.png"), shortHelp="Testing")
        self.menuData.Enable(False)
        toolBar.SetToolBitmapSize((24,24))
        # more toolbuttons are needed: New Output, Save, Print, Cut, \
        # Variables, and Wizard creates the toolbar
        toolBar.Realize()
        self.SetToolBar(toolBar)
        # Set up notebook tabs for data and variables
        self.choice = wx.Notebook(self, -1, size=(-1,-1))
        # set up the datagrid
        self.grid = gridbase.DataGrid(self.choice, inits)
        #self.grid.ResizeGrid(10,70)
        self.grid.SetDefaultColSize(60, True)
        self.grid.SetRowLabelSize(40)
        #self.grid.inits = inits
        numcols = self.grid.GetNumberCols()
        self.vargrid = gridbase.VariablesGrid(self.choice, self.grid, numcols)
        # Add both grids to the notebook control
        self.choice.AddPage(self.grid, text="Data")
        self.choice.AddPage(self.vargrid, text="Variables")

        #...and some events!
        wx.EVT_MENU(self, ID_FILE_NEW, self.GoClearData)
        wx.EVT_TOOL(self, 10, self.GoClearData)
        wx.EVT_TOOL(self, ID_FILE_URL, self.ScrapeURL)
        #wx.EVT_MENU(self, ID_FILE_NEWOUTPUT, self.GoNewOutputSheet)
        # unsure if I want this - maybe restrict user to just one?
        wx.EVT_MENU(self, ID_FILE_SAVE, self.SaveData)
        wx.EVT_TOOL(self, 30, self.SaveData)
        wx.EVT_MENU(self, ID_FILE_SAVEAS, self.SaveAsData)
        wx.EVT_TOOL(self, 40, self.SaveAsData)
        wx.EVT_MENU(self, ID_FILE_OPEN, self.OpenFile)
        #EVT_MENU(self, ID_FILE_OPEN, self.grid.LoadNumericData)
        wx.EVT_TOOL(self, 20, self.OpenFile)
        #EVT_TOOL(self, 20, self.grid.LoadNumericData)
        wx.EVT_MENU(self, ID_EDIT_CUT, self.grid.CutData)
        wx.EVT_TOOL(self, 60, self.grid.CutData)
        wx.EVT_MENU(self, ID_EDIT_COPY, self.grid.CopyData)
        wx.EVT_TOOL(self, 70, self.grid.CopyData)
        wx.EVT_MENU(self, ID_EDIT_PASTE, self.grid.PasteData)
        wx.EVT_TOOL(self, 80, self.grid.PasteData)
        wx.EVT_MENU(self, ID_EDIT_SELECTALL, self.grid.SelectAllCells)
        wx.EVT_MENU(self, ID_EDIT_FIND, self.GoFindDialog)
        wx.EVT_MENU(self, ID_EDIT_INSERTCOL, self.grid.InsertCol)
        wx.EVT_MENU(self, ID_EDIT_INSERTROW, self.grid.InsertRow)
        wx.EVT_MENU(self, ID_EDIT_DELETECOL, self.grid.DeleteCurrentCol)
        wx.EVT_MENU(self, ID_EDIT_DELETEROW, self.grid.DeleteCurrentRow)
        wx.EVT_MENU(self, ID_PREF_DATA, self.GoVariables)
        wx.EVT_MENU(self, ID_PREF_VARIABLES, self.GoVariables)
        wx.EVT_MENU(self, ID_PREF_GEN, self.NewPrefs)
        wx.EVT_TOOL(self, 85, self.GoVariables)
        wx.EVT_TOOL(self, 87, self.ToggleMetaGrid)
        wx.EVT_TOOL(self, 88, self.ToggleChartWindow)
        wx.EVT_MENU(self, ID_PREPARATION_DESCRIPTIVES, self.GoContinuousDescriptives)
        wx.EVT_MENU(self, ID_PREPARATION_TRANSFORM, self.GoTransformData)
        wx.EVT_MENU(self, ID_PREPARATION_OUTLIERS, self.GoCheckOutliers)
        wx.EVT_MENU(self, ID_ANALYSE_1COND, self.GoOneConditionTest)
        wx.EVT_MENU(self, ID_ANALYSE_2COND, self.GoTwoConditionTest)
        wx.EVT_MENU(self, ID_ANALYSE_3COND, self.GetThreeConditionTest)
        wx.EVT_MENU(self, ID_ANALYSE_CORRELATION, self.GetCorrelationsTest)
        #wx.EVT_MENU(self, ID_ANALYSE_2FACT, self.GoMFanovaFrame)
        wx.EVT_MENU(self, ID_ANALYSE_SCRIPT, self.GoScriptWindow)
        wx.EVT_MENU(self, ID_CHART_DRAW, self.ToggleChartWindow)
        wx.EVT_MENU(self, wx.ID_ABOUT, self.GoHelpAboutFrame)
        wx.EVT_MENU(self, ID_HELP_WIZARD, self.GoHelpWizardFrame)
        wx.EVT_MENU(self, ID_HELP_TOPICS, self.GoHelpTopicsFrame)
        wx.EVT_TOOL(self, 90, self.GoHelpAboutFrame)
        wx.EVT_MENU(self, ID_HELP_LICENCE, self.GoHelpLicenceFrame)
        wx.EVT_MENU(self, ID_FILE_EXIT, self.EndApplication)
        wx.EVT_CLOSE(self, self.EndApplication)
        wx.EVT_TOOL(self, 91, self.Test)
        self.choice.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.ChangedTab)
        #wx.EVT_FIND(self, ID_FIND_STRING, self.OnFind)
        #wx.EVT_FIND_NEXT(self, ID_FIND_STRING, self.on_find)
        #wx.EVT_FIND_REPLACE(self, ID_FIND_STRING, self.on_find)
        #wx.EVT_FIND_REPLACE_ALL(self, ID_FIND_STRING, self.on_find)
        if filename:
            frameTitle = filename
            self.grid.LoadFile(filename)

    def Test(self, event):
        print len(self.grid.meta)
        for item in self.grid.meta:
            print item['name']
        #exportSQLite.importfromSQLite("/Users/alan/Projects/SQLitefile.sqlite",self.grid, output)

    def GoVariables(self, evt):
        # shows Variables grid
        page = self.choice.GetSelection()
        if page == 0:
        	self.choice.SetSelection(1) # Should activate a notebook change event
        else:
        	self.choice.SetSelection(0) # ditto

    def ChangedTab(self, event):
    	# This is called when the tabs change. 
    	# From data -> variable, repopulate variable with data
    	# From variable -> data, save changes
    	page = self.choice.GetSelection()
    	if page == 0: # from data -> variables grid
    		self.DisplayDataToVariables()
    		#for i in self.grid.meta.keys():
    			#print self.grid.meta[i]
    	else: # from variables -> data grid
    		self.DisplayVariablesToData()

    def DisplayDataToVariables(self):
		self.menuCut.Enable(False)
		self.menuCopy.Enable(False)
		self.menuPaste.Enable(False)
		self.menuSelectAll.Enable(False)
		self.menuFind.Enable(False)
		self.menuInsertCol.Enable(False)
		self.menuInsertRow.Enable(False)
		self.menuDeleteCol.Enable(False)
		self.menuDeleteRow.Enable(False)
		self.menuData.Enable(True)
		self.menuVariables.Enable(False)
		self.menuPrefs.Enable(False)
		self.vargrid.ResetGrid()

    def DisplayVariablesToData(self):
		self.menuCut.Enable(True)
		self.menuCopy.Enable(True)
		self.menuPaste.Enable(True)
		self.menuSelectAll.Enable(True)
		self.menuFind.Enable(True)
		self.menuInsertCol.Enable(True)
		self.menuInsertRow.Enable(True)
		self.menuDeleteCol.Enable(True)
		self.menuDeleteRow.Enable(True)
		self.menuData.Enable(False)
		self.menuVariables.Enable(True)
		self.menuPrefs.Enable(True)
		self.vargrid.BackToData()

    def SaveData(self, event):
        if self.grid.named:
            filename = self.grid.filename
            filetype = os.path.splitext(filename)[1].lower()
            print filename, filetype
            if filetype in ['.salstat']: # native Salstat
                print "Salstat"
                exportSQLite.exporttoSQLite(filename, self.grid, output)
                self.saved = True
            elif filetype in ['.txt','csv']: # save as CSV
                ImportCSV.SaveCSV(filename, self.grid)
            elif filetype in ['.xls','xlsx']:
                pass # save as Excel
            elif filetype in ['.ods']:
                pass # save as LibreOffice
            elif filetype in ['.html','.htm']:
                ImportHTML.ExportHTML(filename, self.grid)
        else:
            self.SaveAsData(None)

    def SaveAsData(self, event):
        default = inits.get('savedir')
        wildcard = "Salstat database (.salstat)|*.salstat|"    \
                   "Comma separated values (.csv)|*.csv|"      \
                   "Excel workbook (.xls)|.xls|"             \
                   "Libre Office calc (.ods)|.ods|"             \
                   "Hypertext table (.html)|.html"
        dlg = wx.FileDialog(self, "Save File", defaultDir=default,defaultFile="",\
                                    wildcard=wildcard, style=wx.SAVE)
                                    #"Salstat (*.salstat)|*.salstat", \
        ico = wx.Icon('icons/PurpleIcon05_32.png',wx.BITMAP_TYPE_PNG)
        dlg.SetIcon(ico)
        if dlg.ShowModal() == wx.ID_OK:
            fileType = dlg.GetFilterIndex()
            inits.update({'savedir': dlg.GetDirectory()})
            filename = dlg.GetPath()
            if fileType == 0: # Save as Salstat SQLite database (.salstat)
                exportSQLite.exporttoSQLite(filename, self.grid, output)
            elif fileType == 1: # Save as CSV (.csv)
                ImportCSV.SaveCSV(filename, self.grid)
            elif fileType == 2: # Save as Excel (.xls)
                ImportSS.SaveToExcel(filename, self.grid)
            elif fileType == 3: # Save as Libre Office (.ods)
                ImportSS.SaveToLibre(filename, self.grid)
            elif fileType == 4: # Save as HTML table (.html)
                ImportHTML.ExportHTML(filename, self.grid)

    def OpenFile(self, event):
        startDir = inits.get('opendir')
        FileName = GetFilename(frame, startDir)
        if FileName.fileName == None:
            return None
        extension = os.path.splitext(FileName.fileName)[1].lower()
        spreads = ['.xls','.xlsx','.ods']
        csvs    = ['.csv','.txt','.prn','.dat']
        htmls   = ['.htm','.html','.xhtml','.dhtml']
        xmls    = ['.xml']
        sass    = ['.sas7bdat']
        spsss   = ['.sav']
        sqlites = ['.sqlite','.sqlite3','.db','.salstat']
        if extension in spreads: # file extension is for spreadsheet
            dlg = ImportSS.ImportDialog(FileName)
            self.grid.filename = FileName.fileName
        elif extension in csvs: # csv / txt format
            dlg = ImportCSV.ImportDialog(FileName)
            self.grid.filename = FileName.fileName
            self.grid.Saved = False
        elif extension in htmls: # HTML table
            dlg = None
            gridData = []
            variableNames = []
            fin = open(FileName.fileName,'r')
            data = fin.read()
            fin.close()
            soup = BS.BeautifulSoup(data)
            table = soup.find('table')
            headings = table.findAll('th')
            for heading in headings:
                variableNames.append(heading.text)
            rows = table.findAll('tr')
            for row in rows:
                line = []
                cols = row.findAll('td')
                for col in cols:
                    line.append(col.text)
                gridData.append(line)
            self.FillGrid((FileName.fileName, variableNames, gridData))
            self.grid.filename = FileName.fileName
            self.grid.Saved = False
        elif extension in xmls: # xml - unsure how to handle this
            dlg = None
        elif extension in sass: # SAS 8 and later
            allData = sas.SAS7BDAT(FileName.fileName)
            numcols = allData.header.colcount
            numrows = allData.header.rowcount
            self.grid.ResizeGrid(numcols, numrows)
            gridData = []
            for line in allData.readData():
                lineStr = [str(idx) for idx in line]
                gridData.append(lineStr)
            variableNames = gridData.pop(0)
            dlg = None
            self.FillGrid((FileName.fileName, variableNames, gridData), allData.header)
            self.grid.filename = FileName.fileName
            self.SetTitle(os.path.split(FileName.fileName)[1])
            self.grid.Saved = False
        elif extension in spsss: # SPSS
            dlg = None
        elif extension in sqlites: # sqlite database
            dlg = None
            exportSQLite.importfromSQLite(FileName.fileName, self.grid, output)
            self.grid.filename = FileName.fileName
            self.SetTitle(os.path.split(FileName.fileName)[1])
            self.grid.Saved = True
        else:
            dlg = None
        if dlg:
            if dlg.ShowModal():
                if dlg.FileName.fileName == None:
                    dlg.Destroy()
                    return None
                else:
                    fileName = dlg.FileName.fileName
                    variableNames = dlg.headers
                    gridData = dlg.gridData
                    dlg.Destroy()
                    self.FillGrid((fileName, variableNames, gridData))
            else:
                dlg.Destroy()
                return None
        self.grid.ForceRefresh()
        self.grid.named = True

    def ScrapeURL(self, event):
        # user enters URL
        dlg = wx.TextEntryDialog(
            self, "Enter a URL"
        )
        if dlg.ShowModal() == wx.ID_OK:
            URL = dlg.GetValue()
        else:
            return
        path = urlparse.urlparse(URL).path
        ext = os.path.splitext(path)[1]
        if ext == '.csv' or ext == '.txt':
            pass # import direct
        else:
            res = ImportHTML.ImportDialog(URL)
            if res.ShowModal():
                if res.URL:
                    headers = res.headers
                    gridData = res.gridData
                    dlg.Destroy()
                    self.FillGrid((URL, headers, gridData))
                dlg.Destroy()
                self.grid.Saved = False
                self.grid.named = True

    def FillGrid(self, res, meta=None):
        if res != None:
            fname = res[0]
            varnames = res[1]
            newdata = res[2]
            nRows = len(newdata)
            kCols = 0
            for row in range(nRows):
                if len(newdata[row]) > kCols:
                    kCols = len(newdata[row])
            # resize grid to accommodate data
            self.grid.ResizeGrid(kCols, nRows)
            try:
                for idxCol, colLabel in enumerate(varnames):
                    self.grid.SetColLabelValue(idxCol, colLabel)
                    self.grid.AddNewMeta(colLabel, pos=idxCol)
            except:
                pass
            for idxRow, dataRow in enumerate(newdata):
                n = len(dataRow)
                for idxCol, colValue in enumerate(dataRow):
                    if colValue.isspace() == False:
                        self.grid.SetCellValue(idxRow, idxCol, colValue)

    def ToggleChartWindow(self, event):
        self.chartWindow = ChartWindow.ChartWindow(self)
        self.chartWindow.Show(True)
        self.chartWindow.preview.SetPage(self.chartWindow.chartObject.page,HOME)
        self.chartWindow.preview.Reload()
        #print frame.chartObject.page
        #frame.preview.SetPage(frame.chartObject.chartLine,HOME)

    def ReceiveChart(self, chartString):
        output.Addhtml(chartString)

    def NewPrefs(self, event):
        PFrame = PrefsFrame.PFrame(None, -1, self.grid, inits['savedir'])
        PWin = PFrame.ShowModal()
        if PFrame.res == "ok":
            vals = PFrame.Vals
            self.grid.SetDefaultRowSize(vals.CellHeight)
            self.grid.SetDefaultColSize(vals.CellWidth)
            numcols = self.grid.GetNumberCols()
            numrows = self.grid.GetNumberRows()
            diff = vals.NumCols - numcols
            if diff > 0:
                self.grid.AppendCols(diff)
            elif diff < 0:
                self.grid.DeleteCols(vals.NumCols, -diff)
            diff = vals.NumRows - numrows
            if diff > 0:
                self.grid.AppendRows(diff)
            elif diff < 0:
                self.grid.DeleteRows(vals.NumRows, -diff)
            if vals.font:
                self.grid.SetDefaultCellFont(vals.font)
            self.grid.ForceRefresh()
            inits['opendir'] = vals.workingdir
            inits['savedir'] = vals.workingdir
        else:
            pass
        PFrame.Destroy()

    def GoNewOutputSheet(self, evt):
        #shows a new output frame
        SheetWin = OutputSheet(frame, -1)
        SheetWin.Show(True)

    def ToggleMetaGrid(self, event):
        self.metaGrid = MetaGrid.MetaFrame(self)
        self.metaGrid.Show(True)

    def GoClearData(self, evt):
        #shows a new data entry frame
        self.grid.filename = "Untitled"
        self.grid.Saved = True
        self.grid.named = False
        self.grid.ClearGrid()
        self.grid.ResizeGrid(10,70)

    def CheckMatch(self, val, fstring):
        if fstring in val:
            return True
        else:
            return False

    def SearchUp(self, fstring, rstring = None):
        maxrows = self.grid.GetNumberRows()
        maxcols = self.grid.GetNumberCols()
        if self.newsearch:
            self.srow = self.grid.GetGridCursorCol()
            self.scol = self.grid.GetGridCursorRow()
            self.newsearch = False
        val = self.grid. GetCellValue(self.srow, self.scol)
        res = self.CheckMatch(val, fstring)
        if res:
            self.grid.SetGridCursor(self.srow, self.scol)
            self.grid.SelectBlock(self.srow, self.scol,self.srow, self.scol)
            if self.srow > 0:
                self.srow = self.srow - 1
            return
        for idx_row in range(self.srow+1, 0, -1):
            val = self.grid. GetCellValue(idx_row, self.scol)
            res = self.CheckMatch(val, fstring)
            if res:
                self.srow = idx_row
                self.grid.SetGridCursor(self.srow, self.scol)
                self.grid.SelectBlock(self.srow, self.scol,self.srow, self.scol)
                return
        for idx_col in range(self.scol, 0, -1):
            for idx_row in range(maxrows, 0, -1):
                val = self.grid.GetCellValue(idx_row, idx_col)
                res = self.CheckMatch(val, fstring)
                if res:
                    self.srow = idx_row
                    self.scol = idx_col
                    self.grid.SetGridCursor(self.srow, self.scol)
                    self.grid.SelectBlock(self.srow, self.scol,self.srow, self.scol)
                    return
        self.scol = maxcols
        self.srow = maxrows

    def SearchDown(self, fstring, rstring = None):
        maxrows = self.grid.GetNumberRows()
        maxcols = self.grid.GetNumberCols()
        if self.newsearch:
            self.srow = self.grid.GetGridCursorCol()
            self.scol = self.grid.GetGridCursorRow()
            self.newsearch = False
        val = self.grid. GetCellValue(self.srow, self.scol)
        res = self.CheckMatch(val, fstring)
        if res:
            self.grid.SetGridCursor(self.srow, self.scol)
            self.grid.SelectBlock(self.srow, self.scol,self.srow, self.scol)
            if self.srow < maxrows:
                self.srow = self.srow + 1
            return
        for idx_row in range(self.srow+1, maxrows):
            val = self.grid. GetCellValue(idx_row, self.scol)
            res = self.CheckMatch(val, fstring)
            if res:
                self.srow = idx_row
                self.grid.SetGridCursor(self.srow, self.scol)
                self.grid.SelectBlock(self.srow, self.scol,self.srow, self.scol)
                return
        for idx_col in range(self.scol, maxcols):
            for idx_row in range(0, maxrows):
                val = self.grid.GetCellValue(idx_row, idx_col)
                res = self.CheckMatch(val, fstring)
                if res:
                    self.srow = idx_row
                    self.scol = idx_col
                    self.grid.SetGridCursor(self.srow, self.scol)
                    self.grid.SelectBlock(self.srow, self.scol,self.srow, self.scol)
                    return
        self.scol = 0
        self.srow = 0

    def OnFind(self, event):
        try:
            self.newsearch
        except AttributeError:
            self.newsearch = True
        fstring = event.GetFindString()
        Fdata = event.GetFlags()
        if Fdata in [0,2,4,6]:
            Fdown = False
        else:
            Fdown = True
        if Fdata in [0,1,4,5]:
            Fwhole = False
        else:
            Fwhole = True
        if Fdata in [0,1,2,3]:
            Fcase = False
        else:
            Fcase = True
        if Fdown:
            self.SearchDown(fstring)
        else:
            self.SearchUp(fstring)

    def OnFindNext(self, event):
        fstring = event.GetFindString()
        Fdata = event.GetFlags()
        if Fdata in [0,2,4,6]:
            Fdown = False
        else:
            Fdown = True
        if Fdata in [0,1,4,5]:
            Fwhole = False
        else:
            Fwhole = True
        if Fdata in [0,1,2,3]:
            Fcase = False
        else:
            Fcase = True
        if Fdown:
            self.SearchDown(fstring)
        else:
            self.SearchUp(fstring)

    def OnFindReplace(self, event):
        fstring = event.GetFindString()
        rstring = event.GetReplaceString()
        Fdata = event.GetFlags()

    def OnFindReplaceAll(self, event):
        fstring = event.GetFindString()
        rstring = event.GetReplaceString()
        Fdata = event.GetFlags()

    def GoFindDialog(self, event):
        # Shows the find & replace dialog
        # NOTE - this doesn't appear to work on the grid, so I might be missing something...
        data = wx.FindReplaceData()
        self.dlg = wx.FindReplaceDialog(self, data, 'Find and Replace', \
                                    wx.FR_REPLACEDIALOG)
        self.dlg.data = data
        self.dlg.Bind(wx.EVT_FIND, self.OnFind)
        self.dlg.Bind(wx.EVT_FIND_NEXT, self.OnFindNext)
        self.dlg.Bind(wx.EVT_FIND_REPLACE, self.OnFindReplace)
        self.dlg.Bind(wx.EVT_FIND_REPLACE_ALL, self.OnFindReplaceAll)
        res = self.dlg.Show(True)

    def GoContinuousDescriptives(self, evt):
        # shows the continuous descriptives dialog
        #win = DescriptivesFrame(frame, -1)
        win = DescriptivesFrame.DFrame(frame, -1, self.grid)
        res = win.ShowModal()
        if win.res == "ok":
            vals = win.GetValues()
            data = []
            datar = []
            names = []
            win.stats
            win.DVs
            if len(win.GRPs) > 0: # user's selected grouping variables
                #groupedVars = [self.grid.GetVariableData(col,'string') for col in win.GRPs]
                groupedVars = [self.grid.CleanData(col) for col in win.GRPs]
                groups = GetGroups(groupedVars)
                DVs = [self.grid.GetVariableData(col,'float') for col in win.DVs]
                groupnames = win.varListGRP.GetCheckedStrings()
                varnames = win.varListDV.GetCheckedStrings()
                alpha = win.alpha
                GroupedDescriptives(groups, groupedVars, DVs, win.stats, groupnames, varnames,alpha)
            else:
                for i in win.DVs:
                    colnum = win.ColNums[i]
                    vals = self.grid.GetVariableData(colnum,'float')
                    data.append(vals)
                    vals = self.grid.GetVariableData(colnum,'str')
                    datar.append(vals)
                    names.append(self.grid.GetColLabelValue(colnum))
                    alpha = win.alpha
                ManyDescriptives(win.stats, data, datar, names,alpha)
        win.Destroy()

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
            #win = ThreeConditionTestFrame(frame, -1, ColumnList)
            dlg = TestThreeConditions.TestDialog(ColumnList)
            win = dlg.ShowModal()
            if dlg.results:
                DoThreeConditionTests(self.grid, dlg.results)
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

    def GoScriptWindow(self, event):
        # Shows the scripting window
        win = ScriptFrame(frame, -1)
        win.Show(True)

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
            dlg = SaveDialog(self, -1)
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
        sys.exit()

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
def DoThreeConditionTests(grid, result):
    if result["testType"] == 'within':
        data = []
        for column in result["DV"]:
            vector = grid.GetVariableData(int(column), 'float')
            data.append(vector)
        result = Inferentials.anovaWithin(data)
        quotevars = (result["DFbet"],result["DFres"],result["F"],result["p"])
        quote = "<b>Quote:</b> <i>F</i>(%d, %d)=%.3f, <i>p</i>=%1.4f<br />"%(quotevars)
        ln = '<br />'+quote+'<br />'+tabler.tableANOVAWithin(result)
        output.Addhtml(ln)
    elif result["testType"] == 'between':
        #print "Between subs ",result['tests']
        vectorIV = grid.GetVariableData(int(result["IV"][0]), 'str')
        vectorDV = grid.GetVariableData(int(result["DV"][0]), 'float')
        vals, freqs = AllRoutines.UniqueVals(vectorIV)
        data = ma.zeros((len(freqs), max(freqs)))
        data.mask = True
        indices = [0] * len(freqs)
        for idx in range(len(vectorIV)):
            column = vals.index(vectorIV[idx])
            row = indices[column]
            data[column, row] = vectorDV[idx]
            indices[column] += 1
        result = Inferentials.anovaBetween(data)
        quotevars = (result["DFbet"],result["DFerr"],result["F"],result["p"])
        quote = "<b>Quote:</b> <i>F</i>(%d, %d)=%.3f, <i>p</i>=%1.4f<br />"%(quotevars)
        ln = '<br />'+quote+'<br />'+tabler.tableANOVABetween(result)
        output.Addhtml(ln)

#---------------------------------------------------------------------------
# Creating HTML document
def CreateHTMLDoc():
    try:
        fin = open("htmlbase.html",'r')
        page = fin.read()
        fin.close()
    except IOError:
        page = """<!DOCTYPE html>\n<html>\n\t<head>\n\t<script src="jquery/1.8.2/jquery.min.js"></script>\n\t<script src="highcharts/3.0.7/highcharts.js"></script>\n\t<script src="html/highcharts/3.0.7/highcharts-more.js"></script\n\t<script src="highcharts/3.0.7/exporting.js"></script>\n\t<script src="/js/themes/gray.js"></script>\n\t<style>\n\t\tbody { font-family: helvectica, arial, \'lucida sans\'; }\n\t</style>\n</head>\n<body>\n\t<a href="http://www.salstat.com" alt="Go to the Salstat home page"><img src="http://bit.ly/1fqFdQm" alt="Salstat Statistics" style="float: right;"></a>\n\t<h2>Salstat Statistics</h2>\n\n\n"""   
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

