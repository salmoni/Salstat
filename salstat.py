#!/usr/local/bin/python

"""SalStat Statistics Package. Copyright 2002 Alan James Salmoni. Licensed
under the GNU General Public License (GPL). See the file COPYING for full
details of this license. """

# import wx stuff
from __future__ import unicode_literals
import codecs
import numpy, math
import numpy.ma as ma
import wx
from wx.stc import *
import wx.grid as gridlib
import gridbase
import wx.html as htmllib
import wx.html2 as html2lib
import bs4 as BS
#import xlrd, xlwt # import xls format
import string, os, os.path, pickle, csv, sys
import urllib, requests #, urlparse,
import urllib.parse as urlparse

# import SalStat specific modules
import salstat_stats, images, tabler, ChartWindow
import DescriptivesFrame, PrefsFrame
import MetaGrid, AllRoutines, ImportCSV, ImportSS, ImportHTML, Inferentials
import sas7bdat as sas
import TestThreeConditions, TestTwoConditions, TestCorrelations, TestOneCondition
import exportSQLite

from xml.dom import minidom

#---------------------------------------------------------------------------
# set up id's for menu events - all on menu, some also available elsewhere
ID_FILE_NEW = wx.NewId()
ID_FILE_NEWOUTPUT = wx.NewId()
ID_FILE_OPEN = wx.NewId()
ID_FILE_URL = wx.NewId()
ID_FILE_DB = wx.NewId()
ID_FILE_APPEND = wx.NewId()
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
	return urlparse.urljoin('file:', urllib.request.pathname2url(path))

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
		icon = images.getIconBitmap()
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
		self.Bind(wx.EVT_BUTTON, self.SaveData, id=331)
		self.Bind(wx.EVT_BUTTON, self.DiscardData, id=332)
		self.Bind(wx.EVT_BUTTON, self.CancelDialog, id=333)

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
		try:
			fin = open(initfilename, 'r')
			for i in range(28):
				a = fin.readline()
				a = a.strip('\n').split(' ')
				tmpdict = {a[0]:a[1]}
				inits.update(tmpdict)
			fin.close()
		except IndexError:
			self.CreateInitFile(self.initfile)

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
		initskeys = list(inits.keys())
		initsvalues = list(inits.values())
		fout = open(initfilename,'w')
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
		self.SetCheckedItems([0,1,2,5,6,7])

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
		self.Bind(wx.EVT_BUTTON, self.OkayButtonPressed, id=421)
		self.Bind(wx.EVT_BUTTON, self.CancelButtonPressed, id=422)

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
		self.Bind(wx.EVT_TOOL, self.ExecuteScript, id=710)
		self.Bind(wx.EVT_TOOL, self.OpenScript, id=711)
		self.Bind(wx.EVT_TOOL, self.SaveScriptAs, id=713)
		self.Bind(wx.EVT_TOOL, self.CutSelection, id=715)
		self.Bind(wx.EVT_TOOL, self.CopySelection, id=716)
		self.Bind(wx.EVT_TOOL, self.PasteSelection, id=717)
		self.Bind(wx.EVT_TOOL, self.ShowHelp, id=718)

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
									"Any (*)|*",wx.FD_OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			filename = dlg.GetPath()
			fin = file(filename, "r")
			TextIn = fin.readlines()

			self.scripted.SetText(TextIn)
			fin.close()

	def SaveScriptAs(self, event):
		default = inits.get('savedir')
		dlg = wx.FileDialog(self, "Save Script File", default,"",\
									"Any (*)|*", wx.FD_SAVE)
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
									wx.FD_OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			outputfilename = dlg.GetPath()
			self.LoadPage(outputfilename)
			inits.update({'opendir': dlg.GetDirectory()})

	def SaveHtmlPage(self, event):
		dlg = wx.FileDialog(self, "Save Output","","","*.html|*>*",wx.FD_SAVE)
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
		icon = images.getIconBitmap()
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
		toolNew = toolBar.AddTool(401, "New", wx.Bitmap("icons/IconNew.png"), shortHelp="Create a new data sheet")
		toolOpen = toolBar.AddTool(402, "Open", wx.Bitmap("icons/IconOpen.png"), shortHelp="Open a data file")
		toolSaveAs = toolBar.AddTool(403, "Save As", wx.Bitmap("icons/IconSaveAs.png"), shortHelp="Save these data to a new filename")
		toolPrint = toolBar.AddTool(404, "Print", wx.Bitmap("icons/IconPrint.png"), shortHelp="Print this sheet")
		toolHelp = toolBar.AddTool(405, "Help", wx.Bitmap("icons/IconHelp.png"), shortHelp="See help documentation")
		toolBar.SetToolBitmapSize((24,24))
		# more toolbuttons are needed: New Output, Save, Print, Cut, \
		# Variables, and Wizard creates the toolbar
		self.SetToolBar(toolBar)
		self.CreateStatusBar()
		self.SetStatusText('Salstat statistics - results')
		self.htmlpage = html2lib.WebView.New(self)
		self.htmlpage.SetEditable(False)
		self.Addhtml('')
		self.Bind(wx.EVT_TOOL, self.ClearAll, toolNew)
		self.Bind(wx.EVT_TOOL, self.LoadHtmlPage, toolOpen)
		self.Bind(wx.EVT_TOOL, self.SaveHtmlPage, toolSaveAs)
		self.Bind(wx.EVT_TOOL, self.htmlpage.Print, toolPrint)
		#wx.EVT_TOOL(self, 405, frame.GoHelpTopicsFrame)
		self.Bind(wx.EVT_TOOL, frame.GoHelpTopicsFrame, toolHelp)
		toolBar.Realize()
		#self.printer = wx.Printout()

		self.Bind(wx.EVT_MENU, self.Undo, id=ID_OEDIT_UNDO)
		self.Bind(wx.EVT_MENU, self.Redo, id=ID_OEDIT_REDO)
		self.Bind(wx.EVT_MENU, self.CutHTML, id=ID_OEDIT_CUT)
		self.Bind(wx.EVT_MENU, self.CopyHTML, id=ID_OEDIT_COPY)
		self.Bind(wx.EVT_MENU, self.PasteHTML, id=ID_OEDIT_PASTE)
		self.Bind(wx.EVT_MENU, self.SaveHtmlPage, id=ID_OFILE_SAVEAS)
		self.Bind(wx.EVT_MENU, self.parent.EndApplicationMenu, id=ID_OFILE_QUIT)
		self.Bind(wx.EVT_CLOSE, self.DoNothing)
		self.Bind(wx.EVT_MENU, self.ClearAll, id=ID_OFILE_NEW)
		self.Bind(wx.EVT_MENU, self.PrintOutput, id=ID_OFILE_PRINT)
		self.Bind(wx.EVT_MENU, self.LoadHtmlPage, id=ID_OFILE_OPEN)
		self.Bind(wx.EVT_MENU, frame.GoHelpAboutFrame, id=wx.ID_ABOUT)
		self.Bind(wx.EVT_MENU, frame.GoHelpWizardFrame, id=ID_HELP_WIZARD)
		self.Bind(wx.EVT_MENU, frame.GoHelpTopicsFrame, id=ID_HELP_TOPICS)
		self.Bind(wx.EVT_MENU, frame.GoHelpLicenceFrame, id=ID_HELP_LICENCE)
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
							wx.FD_OPEN)
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
							wx.FD_SAVE)
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
		fout.write(self.WholeOutString+htmlend) #.encode('UTF-8'))
		fout.close()
		file_loc = FileToURL(basedir+os.sep+'tmp/output.html')
		self.htmlpage.LoadURL(file_loc)

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
		print (self.parent.grid.GetSelectedCols())

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
		self.Bind(wx.EVT_BUTTON, self.OnOkayButton, id=1105)
		self.Bind(wx.EVT_BUTTON, self.OnCloseFrame, id=1106)
		self.Bind(wx.EVT_BUTTON, self.squareRootTransform, id=1110)
		self.Bind(wx.EVT_BUTTON, self.logTransform, id=1111)
		self.Bind(wx.EVT_BUTTON, self.reciprocalTransform, id=1112)
		self.Bind(wx.EVT_BUTTON, self.squareTransform, id=1113)

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
		icon = images.getIconBitmap()
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
		# ID_FILE_APPEND
		self.menuAppendData = file_menu.Append(ID_FILE_APPEND, "Append data...")
		file_menu.AppendSeparator()
		self.menuSave = file_menu.Append(ID_FILE_SAVE, '&Save\tCTRL+S')
		self.menuSaveAs = file_menu.Append(ID_FILE_SAVEAS, 'Save &As...\tSHIFT+CTRL+S')
		file_menu.AppendSeparator()
		self.menuPrint = file_menu.Append(ID_FILE_PRINT, '&Print...\tCTRL+P')
		file_menu.AppendSeparator()
		#self.menuExit = file_menu.Append(ID_FILE_EXIT, 'Q&uit\tCTRL+Q')
		self.menuExit = file_menu.Append(wx.ID_EXIT, 'Q&uit\tCTRL+Q')
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
		toolNew = toolBar.AddTool(10, "New", wx.Bitmap("icons/IconNew.png"), shortHelp="Create a new data sheet")
		toolOpen = toolBar.AddTool(20, "Open", wx.Bitmap("icons/IconOpen.png"), shortHelp="Open a data file")
		toolSave = toolBar.AddTool(30, "Save", wx.Bitmap("icons/IconSave.png"), shortHelp="Save these data to file")
		toolSaveAs = toolBar.AddTool(40, "Save As", wx.Bitmap("icons/IconSaveAs.png"), shortHelp="Save these data to a new filename")
		toolPrint = toolBar.AddTool(50, "Print", wx.Bitmap("icons/IconPrint.png"), shortHelp="Print this sheet")
		toolCut = toolBar.AddTool(60, "Cut", wx.Bitmap("icons/IconCut.png"), shortHelp="Cut selection to clipboard")
		toolCopy = toolBar.AddTool(70, "Copy", wx.Bitmap("icons/IconCopy.png"), shortHelp="Copy selection to clipboard")
		toolPaste = toolBar.AddTool(80, "Paste", wx.Bitmap("icons/IconPaste.png"), shortHelp="Paste selection from clipboard")
		toolPreferences = toolBar.AddTool(85, "Preferences", wx.Bitmap("icons/IconPrefs.png"), shortHelp="Set your preferences")
		toolMeta = toolBar.AddTool(87, "Meta", wx.Bitmap("icons/IconHelp.png"), shortHelp="Set variables")
		toolChart = toolBar.AddTool(88, "Chart", wx.Bitmap("icons/IconChart.png"), shortHelp="View the chart window")
		toolHelp = toolBar.AddTool(90, "Help", wx.Bitmap("icons/IconHelp.png"), shortHelp="Get help")
		toolTest = toolBar.AddTool(91, "TEST", wx.Bitmap("icons/IconNew.png"), shortHelp="Testing")
		self.menuData.Enable(False)
		toolBar.SetToolBitmapSize((24,24))
		# more toolbuttons are needed: New Output, Save, Print, Cut, \
		# Variables, and Wizard creates the toolbar
		self.choice = wx.Notebook(self, -1, size=(-1,-1))
		self.grid = gridbase.DataGrid(self.choice, inits)

		toolBar.Bind(wx.EVT_TOOL, self.GoClearData, toolNew)
		#toolBar.Bind(wx.EVT_TOOL, self.ScrapeURL)
		toolBar.Bind(wx.EVT_TOOL, self.SaveData, toolSave)
		toolBar.Bind(wx.EVT_TOOL, self.SaveAsData, toolSaveAs)
		toolBar.Bind(wx.EVT_TOOL, self.OpenFile, toolOpen)
		toolBar.Bind(wx.EVT_TOOL, self.grid.CutData, toolCut)
		toolBar.Bind(wx.EVT_TOOL, self.grid.CopyData, toolCopy)
		toolBar.Bind(wx.EVT_TOOL, self.grid.PasteData, toolPaste)
		#toolBar.Bind(self.GoVariables)
		toolBar.Bind(wx.EVT_TOOL, self.ToggleMetaGrid, toolMeta)
		toolBar.Bind(wx.EVT_TOOL, self.ToggleChartWindow, toolChart)
		toolBar.Bind(wx.EVT_TOOL, self.GoHelpAboutFrame, toolHelp)
		toolBar.Bind(wx.EVT_TOOL, self.Test, toolTest)

		toolBar.Realize()
		self.SetToolBar(toolBar)
		# Set up notebook tabs for data and variables
		# set up the datagrid
		#self.grid.ResizeGrid(10,70)
		self.grid.SetDefaultColSize(60, True)
		self.grid.SetRowLabelSize(40)
		#self.grid.inits = inits
		numcols = self.grid.GetNumberCols()
		self.vargrid = gridbase.VariablesGrid(self.choice, self.grid, numcols)
		# Add both grids to the notebook control
		self.choice.AddPage(self.grid, text="Data")
		self.choice.AddPage(self.vargrid, text="Variables")

		self.Bind(wx.EVT_MENU, self.GoClearData, id=ID_FILE_NEW)
		self.Bind(wx.EVT_MENU, self.SaveData, id=ID_FILE_SAVE)
		self.Bind(wx.EVT_MENU, self.SaveAsData, id=ID_FILE_SAVEAS)
		self.Bind(wx.EVT_MENU, self.OpenFile, id=ID_FILE_OPEN)
		self.Bind(wx.EVT_MENU, self.AppendData, id=ID_FILE_APPEND)
		self.Bind(wx.EVT_MENU, self.EndApplication, self.menuExit)
		self.Bind(wx.EVT_MENU, self.grid.CutData, id=ID_EDIT_CUT)
		self.Bind(wx.EVT_MENU, self.grid.CopyData, id=ID_EDIT_COPY)
		self.Bind(wx.EVT_MENU, self.grid.PasteData, id=ID_EDIT_PASTE)
		self.Bind(wx.EVT_MENU, self.grid.SelectAllCells, id=ID_EDIT_SELECTALL)
		self.Bind(wx.EVT_MENU, self.GoFindDialog, id=ID_EDIT_FIND)
		self.Bind(wx.EVT_MENU, self.grid.InsertCol, id=ID_EDIT_INSERTCOL)
		self.Bind(wx.EVT_MENU, self.grid.InsertRow, id=ID_EDIT_INSERTROW)
		self.Bind(wx.EVT_MENU, self.grid.DeleteCurrentCol, id=ID_EDIT_DELETECOL)
		self.Bind(wx.EVT_MENU, self.grid.DeleteCurrentRow, id=ID_EDIT_DELETEROW)
		self.Bind(wx.EVT_MENU, self.GoVariables, id=ID_PREF_DATA)
		self.Bind(wx.EVT_MENU, self.GoVariables, id=ID_PREF_VARIABLES)
		self.Bind(wx.EVT_MENU, self.NewPrefs, id=ID_PREF_GEN)
		self.Bind(wx.EVT_MENU, self.GoContinuousDescriptives, id=ID_PREPARATION_DESCRIPTIVES)
		self.Bind(wx.EVT_MENU, self.GoTransformData, id=ID_PREPARATION_TRANSFORM)
		self.Bind(wx.EVT_MENU, self.GoCheckOutliers, id=ID_PREPARATION_OUTLIERS)
		self.Bind(wx.EVT_MENU, self.GoOneConditionTest, id=ID_ANALYSE_1COND)
		self.Bind(wx.EVT_MENU, self.GoTwoConditionTest, id=ID_ANALYSE_2COND)
		self.Bind(wx.EVT_MENU, self.GetThreeConditionTest, id=ID_ANALYSE_3COND)
		self.Bind(wx.EVT_MENU, self.GetCorrelationsTest, id=ID_ANALYSE_CORRELATION)
		#wx.EVT_MENU(self, ID_ANALYSE_2FACT, self.GoMFanovaFrame)
		self.Bind(wx.EVT_MENU, self.GoScriptWindow, id=ID_ANALYSE_SCRIPT)
		self.Bind(wx.EVT_MENU, self.ToggleChartWindow, id=ID_CHART_DRAW)
		self.Bind(wx.EVT_MENU, self.GoHelpAboutFrame, id=wx.ID_ABOUT)
		self.Bind(wx.EVT_MENU, self.GoHelpWizardFrame, id=ID_HELP_WIZARD)
		self.Bind(wx.EVT_MENU, self.GoHelpTopicsFrame, id=ID_HELP_TOPICS)
		self.Bind(wx.EVT_MENU, self.GoHelpLicenceFrame, id=ID_HELP_LICENCE)
		#self.Bind(wx.EVT_MENU, self.EndApplicationMenu, id=ID_FILE_EXIT)
		self.Bind(wx.EVT_CLOSE, self.EndApplication)
		self.choice.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.ChangedTab)
		#wx.EVT_FIND(self, ID_FIND_STRING, self.OnFind)
		#wx.EVT_FIND_NEXT(self, ID_FIND_STRING, self.on_find)
		#wx.EVT_FIND_REPLACE(self, ID_FIND_STRING, self.on_find)
		#wx.EVT_FIND_REPLACE_ALL(self, ID_FIND_STRING, self.on_find)
		if filename:
			frameTitle = filename
			self.grid.LoadFile(filename)

	def Test(self, event):
		ColumnList, waste = self.grid.GetUsedCols()
		dlg = TestCorrelations.TestDialog(ColumnList)
		win = dlg.ShowModal()
		if dlg.results:
			DoCorrelations(self.grid, dlg.results)
		"""
		print len(self.grid.meta)
		for item in self.grid.meta:
			print item['name']
		"""
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
			#print (filename, filetype)
			if filetype in ['.salstat']: # native Salstat
				#print "Salstat"
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
									wildcard=wildcard, style=wx.FD_SAVE)
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

	def AppendData(self, event):
		pass

	def OpenFile(self, event):
		startDir = inits.get('opendir')
		FileName = GetFilename(frame, startDir)
		if FileName.fileName == None:
			return None
		filepath = os.path.splitext(FileName.fileName)
		extension = filepath[1].lower()
		inits['opendir'] = os.path.split(FileName.fileName)[0]
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
			col_names = allData.column_names
			numcols = len(col_names)
			numrows = allData.header.properties.row_count
			self.grid.ResizeGrid(numcols, numrows)
			gridData = []
			for line in allData:
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
					if str(colValue).isspace() == False:
						self.grid.SetCellValue(idxRow, idxCol, str(colValue))

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
			dlg = TestOneCondition.TestDialog(ColumnList) 
			win = dlg.ShowModal()
			try:
				if dlg.results:
					print(dlg.results)
					DoOneConditionTests(self.grid, dlg.results)
			except AttributeError:
				pass
			#win = OneConditionTestFrame(frame, -1, ColumnList)
			#win.Show(True)
		else:
			self.SetStatusText('You need to enter 1 data column for this!')

	def GoTwoConditionTest(self,event):
		# shows two conditions test dialog
		ColumnList, waste = self.grid.GetUsedCols()
		if (len(ColumnList) > 1):
			dlg = TestTwoConditions.TestDialog(ColumnList)
			win = dlg.ShowModal()
			try:
				if dlg.results:
					DoTwoConditionTests(self.grid, dlg.results)
			except AttributeError:
				pass
		else:
			self.SetStatusText('You need some data for that!')

	def GetThreeConditionTest(self, event):
		# shows three conditions or more test dialog
		ColumnList, waste = self.grid.GetUsedCols()
		if (len(ColumnList) > 1):
			dlg = TestThreeConditions.TestDialog(ColumnList)
			win = dlg.ShowModal()
			try:
				DoThreeConditionTests(self.grid, dlg.results)
			except AttributeError:
				pass
		else:
			self.SetStatusText('You need some data for that!')

	def GetCorrelationsTest(self, event):
		# Shows the correlations dialog
		ColumnList, waste = self.grid.GetUsedCols()
		if (len(ColumnList) > 1):
			dlg = TestCorrelations.TestDialog(ColumnList)
			win = dlg.ShowModal()
			try:
				if dlg.results:
					DoCorrelations(self.grid, dlg.results)
			except AttributeError:
				pass
		else:
			self.SetStatusText('You need some data for that!')

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

	def EndApplicationMenu(self, evt):
		self.EndApplication(evt)

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
							defaultFile="Untitled", style=wx.FD_SAVE)
					if dlg.ShowModal() == wx.ID_OK:
						path, self.filename = os.path.split(dlg.GetPath())
						self.grid.SaveDataASCII(None)
						self.FinalExit()
					else:
						return
			else:
				return

	def FinalExit(self):
		dims = self.GetSize()
		inits.update({'gridsizex': dims[0]})
		inits.update({'gridsizey': dims[1]})
		dims = self.GetPosition()
		inits.update({'gridposx': dims[0]})
		inits.update({'gridposy': dims[1]})
		dims = output.GetSize()
		inits.update({'outputsizex': dims[0]})
		inits.update({'outputsizey': dims[1]})
		dims = output.GetPosition()
		inits.update({'outputposx': dims[0]})
		inits.update({'outputposy': dims[1]})
		initskeys = list(inits.keys())
		initsvalues = list(inits.values())
		initfilename = ini.initfile
		fout = open(initfilename,'w')
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
		data = ma.array(data)
		if "anovawithin" in result["tests"]:
			res = Inferentials.anovaWithin(data)
			quotevars = (res["DFbet"],res["DFres"],res["F"],res["p"])
			quote = "<h3>Within-subjects ANOVA</h3>(analysis of variance)<br />"
			quote += "<b>Quote:</b> <i>F</i>(%d, %d) = %.3f, <i>p</i> = %1.4f<br />"%(quotevars)
			ln = '<br />'+quote+'<br />'+tabler.tableANOVAWithin(res)
			output.Addhtml(ln)
		if "friedmans" in result["tests"]:
			res = Inferentials.Friedman(data)
			quotevars = (res["df"],res["chi"],res["prob"])
			quote = "<h3>Friedman's Tests</h3>(nonparametric analysis of variance)<br />"
			quote += "<b>Quote:</b> <i>F</i>(%d) = %.3f, <i>p</i> = %1.4f<br />"%(quotevars)
			variables =[['Variable:', " grouped by "],
					['chi',res['chi'] ],
					['df',res['df'] ],
					['p',res['prob'] ]]
			ln = '<br />'+quote+'<br />'+tabler.table(variables)
			output.Addhtml(ln)
		if "cochranes" in result["tests"]:
			pass
	elif result["testType"] == 'between':
		#print "Between subs ",result['tests']
		col1 = int(result["IV"][0])
		col2 = int(result["DV"][0])
		name1 = frame.grid.meta[result["IV"][0]]["name"]
		name2 = frame.grid.meta[result["DV"][0]]["name"]
		vectorIV = grid.GetVariableData(col1, 'str')
		vectorDV = grid.GetVariableData(col2, 'float')
		vals, freqs = AllRoutines.UniqueVals(vectorIV)
		data = ma.zeros((len(freqs), max(freqs)))
		data.mask = True
		indices = [0] * len(freqs)
		for idx in range(len(vectorIV)):
			column = vals.index(vectorIV[idx])
			row = indices[column]
			data[column, row] = vectorDV[idx]
			indices[column] += 1
		if "anovabetween" in result["tests"]:
			res = Inferentials.anovaBetween(data)
			quotevars = (res["DFbet"],res["DFerr"],res["F"],res["p"])
			quote = "<h3>Between-subjects ANOVA</h3>(analysis of variance)<br />"
			quote += "<b>Quote:</b> <i>F</i>(%d, %d) = %.3f, <i>p</i> = %1.4f<br />"%(quotevars)
			ln = '<br />'+quote+'<br />'+tabler.tableANOVABetween(res)
			output.Addhtml(ln)
		if "kruskal" in result["tests"]:
			res = Inferentials.KruskalWallis(data)
			quotevars = (res['df'],res["h"],res["prob"])
			quote = "<h3>Kruskal-Wallis test</h3>(nonparametric analysis of variance)<br />"
			quote += "<b>Quote:</b> <i>H</i> (%d) = %.3f, <i>p</i> = %1.4f<br />"%(quotevars)
			variables =[['Variable:', "%s grouped by %s"%(name2, name1)],
					['h',res['h']],
					['df',res['df']],
					['p',res['prob']]]
			ln = '<br />'+quote+'<br />'+tabler.table(variables)
			output.Addhtml(ln)

def DoTwoConditionTests(grid, result):
	if result["testType"] == "within":
		data = []
		quote = ""
		col1 = result["DV"][0]
		col2 = result["DV"][1]
		name1 = frame.grid.meta[col1]["name"]
		name2 = frame.grid.meta[col2]["name"]
		data.append(grid.GetVariableData(int(col1), 'float'))
		data.append(grid.GetVariableData(int(col2), 'float'))
		if "ttestpaired" in result["tests"]:
			quote += "<h3>T-test</h3>(two paired, dependent, within-subjects or related samples)<br />"
			res = Inferentials.TTestPaired(data[0], data[1])
			quote += res['quote']%(res['df'],res['t'],res['prob'],res['d'])
			variables =[['Variable:', "%s compared against %s"%(name2, name1)],
					['df', res['df']],
					['t',res['t']],
					['p',res['prob']],
					["Cohen's d",res['d']]]
			quote += '<br />' + tabler.table(variables) + '<br />'

		if "wilcoxon" in result["tests"]:
			quote += "<h3>Wilcoxon Signed Ranks test</h3>(two unpaired, independent, between-subjects, or unrelated samples)<br /><br />"
			res = Inferentials.SignedRanks(data[0], data[1])
			quote += res['quote']
			variables =[['Variable:', "%s compared against %s"%(name2, name1)],
					['T', res['t']],
					['p',res['prob']]]
			quote += '<br />' + tabler.table(variables) + '<br />'

		if "pairedsign" in result["tests"]:
			quote += "<h3>Paired Sign test</h3>(two unpaired, independent, between-subjects, or unrelated samples)<br /><br />"
			res = Inferentials.TwoSampleSignTest(data[0], data[1])
			quote += res['quote']
			variables =[['Variable:', "%s compared against %s"%(name2, name1)],
					['Z', res['z']],
					['p',res['prob']],
					['Mean', res['mean']],
					['StdDev', res['sd']]]
			quote += '<br />' + tabler.table(variables) + '<br />'

		ln = "<br />"+quote+"<br />"
		output.Addhtml(ln)
	elif result["testType"] == "between":
		name1 = frame.grid.meta[result["IV"][0]]["name"]
		name2 = frame.grid.meta[result["DV"][0]]["name"]
		quote = ""
		vectorIV = grid.GetVariableData(int(result["IV"][0]), 'str')
		vectorDV = grid.GetVariableData(int(result["DV"][0]), 'float')
		data = Inferentials.GroupData2(vectorIV, vectorDV)
		#print data[1]
		if "ttestunpaired" in result["tests"]:
			quote += "<h3>T-test</h3>(two unpaired, independent, between-subjects, or unrelated samples)<br /><br />"
			res = Inferentials.TTestUnpaired(data[0], data[1])
			quote += res["quote"]%(res['t'],res['df'],res['prob'],res['d'])
			variables =[['Variable:', "%s grouped by %s"%(name2, name1)],
					['df', res['df']],
					['t',res['t']],
					['p',res['prob']],
					["Cohen's d",res['d']]]
			quote += '<br />' + tabler.table(variables) + '<br />'

		if "mannwhitneyu" in result["tests"]:
			quote += "<h3>Mann-Whitney U test</h3>(two unpaired, independent, between-subjects, or unrelated samples)<br /><br />"
			res = Inferentials.MannWhitneyU(data[0], data[1])
			quote += res['quote']
			variables =[['Variable:', "%s grouped by %s"%(name2, name1)],
					['U', res['u']],
					['p',res['prob']]]
			quote += '<br />' + tabler.table(variables) + '<br />'

		if "kolmogorov" in result["tests"]:
			quote += "<h3>Kolmogorov-Smirnov test</h3>(two unpaired, independent, between-subjects, or unrelated samples)<br /><br />"
			res = Inferentials.KolmogorovSmirnov(data[0], data[1])
			quote += res['quote']
			variables =[['Variable:', "%s grouped by %s"%(name2, name1)],
					['d', res['d']],
					['p',res['prob']]]
			quote += '<br />' + tabler.table(variables) + '<br />'

		if "ftest" in result["tests"]:
			pass
		ln = "<br />"+quote+"<br />"
		output.Addhtml(ln)

def DoOneConditionTests(grid, result):
	#name = frame.grid.meta[result["IV"]]["tests"]
	quote = ""
	name1 = frame.grid.meta[result["IV"]]["name"]
	data = grid.GetVariableData(int(result["IV"]), 'float')
	try:
		umean = float(result["umean"])
	except ValueError:
		output.Addhtml('<p class="text-warning">Cannot do test - no user hypothesised mean specified')
		return
	# ['ttestone','signtest','chivariance']
	# One sample t-test
	if 'ttestone' in result['tests']:
		output.Addhtml('<h3>One sample t-test</h3>')
		#df, t, prob, d = Inferentials.OneSampleTTest(data, umean)
		res = Inferentials.OneSampleTTest(data, umean)
		if (res['prob'] == -1.0):
			output.Addhtml('<p class="text-warning">All elements are the same, \
								test not possible</p>')
		else:
			variables = [['Variable', name1],
					['Hypothetic mean', umean],
					['df', res['df']],
					['t',res['t']],
					['p',res['prob']]]
			#quote += '<br />' + tabler.table(variables) + '<br />'
			quote = res['quote']
			ln = '<br />' + tabler.table(variables) + quote + '<p /><br />'
			output.Addhtml(ln)
	# One sample sign test
	if 'signtest' in result['tests']:
		output.Addhtml('<H3>One sample sign test</H3>')
		res = Inferentials.OneSampleSignTest(data, umean)
		if (res['probability'] == -1.0):
			output.Addhtml('<p class="text-warning">All data are the same - no \
								analysis is possible</p>')
		else:
			variables = [['Variable', name1],
					['Hypothetic mean', umean],
					['Positive',res['nplus']],
					['Negative',res['nminus']],
					['Equal',res['nequal']],
					['Z',res['z']],
					['p',res['probability']]]
			ln = '<br />' + tabler.table(variables) + res['quote'] + '<p /><br />'
			output.Addhtml(ln)
	# chi square test for variance
	if 'chivariance' in result['tests']:
		output.Addhtml('<H3>One sample chi square</H3>')
		res = Inferentials.ChiSquareVariance(data, umean)
		if (res['probability'] == -1.0):
			output.Addhtml('<p class="text-warning">All elements are the same, test not possible</p>')
		else:
			variables = [['Variable', name1],
					['Hypothetic mean', umean],
					['df', res['df']],
					['Chi',res['chisquare']],
					['p',res['probability']]]
			ln = '<br />' + tabler.table(variables) + res['quote'] + '<p /><br />'
		output.Addhtml(ln)

def DoCorrelations(grid, result):
	data = []
	quote = ""
	col1 = result["DV"][0]
	col2 = result["DV"][1]
	name1 = frame.grid.meta[col1]["name"]
	name2 = frame.grid.meta[col2]["name"]
	data.append(grid.GetVariableData(int(col1), 'float'))
	data.append(grid.GetVariableData(int(col2), 'float'))
	if "pearsons" in result["tests"]:
		quote += "<h3>Pearson's Correlation</h3>(two samples)<br />"
		res = Inferentials.PearsonR(data[0], data[1])
		quote += res['quote']%(res['df'],res['r'],res['prob'])
		variables =[['Variable:', "%s associated with %s"%(name2, name1)],
				['df', res['df'] ],
				['r',res['r'] ],
				['p',res['prob']] ]
		quote += '<br />' + tabler.table(variables) + '<br />'

	if "spearmans" in result["tests"]:
		quote += "<h3>Spearman's Correlation</h3>(two samples)<br />"
		res = Inferentials.SpearmanR(data[0], data[1])
		quote += res['quote']%(res['df'],res['r'],res['prob'])
		variables =[['Variable:', "%s associated with %s"%(name2, name1)],
				['df', res['df'] ],
				['r',res['r'] ],
				['p',res['prob']] ]
		quote += '<br />' + tabler.table(variables) + '<br />'

	if "kendalls" in result["tests"]:
		quote += "<h3>Kendall's Correlation</h3>(two samples)<br />"
		res = Inferentials.KendallsTau(data[0], data[1])
		quote += res['quote']%(res['df'],res['tau'],res['prob'])
		variables =[['Variable:', "%s associated with %s"%(name2, name1)],
				['df', res['df'] ],
				['tau',res['tau'] ],
				['p',res['prob']] ]
		quote += '<br />' + tabler.table(variables) + '<br />'

	if "pointbr" in result["tests"]:
		quote += "<h3>Point biserial r Correlation</h3>(two samples)<br />"
		res = Inferentials.PointBiserial(data[0], data[1])
		quote += res['quote']%(res['df'],res['r'],res['prob'])
		variables =[['Variable:', "%s associated with %s"%(name2, name1)],
				['df', res['df'] ],
				['r',res['r'] ],
				['p',res['prob']] ]
		quote += '<br />' + tabler.table(variables) + '<br />'

	ln = "<br />"+quote+"<br />"
	output.Addhtml(ln)

#---------------------------------------------------------------------------
# Creating HTML document
def CreateHTMLDoc():
	try:
		fin = open("htmlbase.html",'r')
		page = fin.read()
		fin.close()
	except IOError:
		page = """<!DOCTYPE html>\n<html>\n\t<head>\n\t<script src="jquery/1.8.2/jquery.min.js"></script>\n\t<script src="highcharts/3.0.7/highcharts.js"></script>\n\t<script src="html/highcharts/3.0.7/highcharts-more.js"></script\n\t<script src="highcharts/3.0.7/exporting.js"></script>\n\t<script src="/js/themes/gray.js"></script>\n\t<style>\n\t\tbody { font-family: helvectica, arial, \'lucida sans\'; }\n\t</style>\n</head>\n<body>\n\t<a href="http://www.salstat.com" alt="Go to the Salstat home page"><img src="../icons/PurpleIcon05_32.png" alt="Salstat Statistics" style="float: right;"></a>\n\t<h2>Salstat Statistics</h2>\n\n\n"""
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
