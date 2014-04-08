#!/usr/bin/env python

import time
import wx
import wx.html2 as html2lib
import wx.propgrid as wxpg
import images
import sys, numpy
import AllRoutines


#---------------------------------------------------------------------------
# Ancilliary functions
def GetGroups(groupingvars):
    """
    Receives a list of vectors and calculates the permuations
    """
    groups = []
    k = len(groupingvars)
    N = len(groupingvars[0])
    for idx in range(N):
        row = [var[idx] for var in groupingvars]
        if row not in groups:
            groups.append(row)
    return groups

def ExtractGroupsData(group, groupingvars, variable):
    N = len(variable)
    data = []
    for idx in range(N):
        row = [element[idx] for element in groupingvars]
        if group == row:
            data.append(variable[idx])
    return data

#---------------------------------------------------------------------------
# call instance of DataGrid
# This is main interface of application
class ChartWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1,"CHARTS", size=(1000,600), pos=(50,50))
        self.parent = parent
        self.embed = False
        self.grid = parent.grid
        self.CreateStatusBar()
        #self.SetStatusText('SalStat Statistics')
        self.chartObject = ChartObject()
        NewIcon = images.getNewBitmap()
        OpenIcon = images.getOpenBitmap()
        SaveIcon = images.getSaveBitmap()
        PrintIcon = images.getPrintBitmap()
        EmbedIcon = images.getPrintBitmap()
        toolBar = self.CreateToolBar(wx.TB_HORIZONTAL|wx.NO_BORDER| \
                                    wx.TB_3DBUTTONS | wx.TB_TEXT)
        #ToolNew = wx.ToolBarToolBase(toolBar)
        #toolBar.AddTool(10, NewIcon,"New")
        toolBar.AddSimpleTool(10, NewIcon,"New")
        toolBar.AddSimpleTool(20, OpenIcon,"Open")
        toolBar.AddSimpleTool(30, SaveIcon,"Save")
        toolBar.AddSimpleTool(50, PrintIcon,"Print")
        toolBar.AddSimpleTool(70, EmbedIcon, "Embed")
        toolBar.SetToolBitmapSize((24,24))
        toolBar.Realize()
        self.SetToolBar(toolBar)
        self.charthtml = """<!DOCTYPE html>\n<html>\n    <head>\n        <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>\n        <script src="http://code.highcharts.com/highcharts.js"></script>\n        <script src="http://code.highcharts.com/modules/exporting.js"></script>\n        <script src="/js/themes/gray.js"></script>\n        <style>\n            body { font-family: helvectica, arial, \'lucida sans\'; }\n        </style>\n    </head>\n    <body>\n"""
        self.webview = html2lib.WebView
        self.preview = self.webview.New(self) #, size=(100,100))
        self.preview.SetSize
        self.control = ControlPanel(self, -1, self.chartObject, self.preview)
        if self.grid:
            self.variables = VarPanel(self, -1, self.grid, self.chartObject)
        else:
            self.variables = VarPanel(self, -1, None, self.chartObject)
        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.box.Add(self.variables, 0, wx.EXPAND)
        self.box.Add(self.preview, 1, wx.EXPAND)
        self.box.Add(self.control, 0, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(self.box)
        self.Layout()
        wx.EVT_TOOL(self, 70, self.EmbedChart)

    def EmbedChart(self, event):
        #self.embed = True
        chart = self.chartObject.FinalToString()
        self.parent.ReceiveChart(chart)

class ControlPanel(wx.Panel):
    def __init__(self, parent, id, chartObject, webview):
        wx.Panel.__init__(self, parent, -1, size=(250,-1))
        self.chartObject = chartObject
        self.WebView = webview
        self.types = ['line', 'spline', 'area', 'areaspline', 'column', \
                'bar', 'pie', 'scatter']
        self.align =  ["left", "center", "right", "do not show"]
        self.valign = ["top","middle","bottom"]
        self.aligned = ["Do not display legend","Top left","Top middle","Top right", \
                "Centre left","Centre middle","Centre right", \
                "Bottom left","Bottom middle","Bottom right"]

        wx.StaticText(self, -1, "Chart type", (20,20))
        wx.StaticText(self, -1, "Chart title", (20,70))
        wx.StaticText(self, -1, "Chart subtitle", (20,120))
        wx.StaticText(self, -1, "Legend", (20,170))

        self.ctrl_type = wx.ComboBox(self, -1, size=(200,-1),pos=(20,40), choices = self.types, value=self.chartObject.chart_type)
        self.ctrl_title = wx.TextCtrl(self, -1, size=(200,-1),pos=(20,90), \
                value=self.chartObject.title_text)
        self.ctrl_subtitle = wx.TextCtrl(self, -1, size=(200,-1),pos=(20,140), \
                value=self.chartObject.subtitle_text)
        self.ctrl_align = wx.ComboBox(self, -1, size=(200,-1),pos=(20,190), choices = self.align, value=self.chartObject.legend_align)
        self.ctrl_valign = wx.ComboBox(self, -1, size=(200,-1),pos=(20,220), choices = self.valign, value=self.chartObject.legend_verticalAlign)

        changebutton = wx.Button(self, 710, "Change settings", pos=(15,280))
        wx.EVT_BUTTON(changebutton, 710, self.ChangeSettings)

    def ChangeSettings(self, event):
        type_idx = self.ctrl_type.GetSelection()
        if type_idx > -1:
            self.chartObject.chart_type = self.types[type_idx]
        self.chartObject.title_text = self.ctrl_title.GetValue()
        self.chartObject.subtitle_text = self.ctrl_subtitle.GetValue()
        align_idx  = self.ctrl_align.GetSelection()
        valign_idx = self.ctrl_valign.GetSelection()
        self.chartObject.legend_align = self.align[align_idx]
        self.chartObject.legend_verticalAlign = self.valign[valign_idx]
        #y_title = self.ctrl_yaxistitle.GetValue()
        #x_title = self.ctrl_xaxistitle.GetValue()
        #legend = self.ctrl_legendpos.GetValue()
        #x_max = self.ctrl_xaxismax.GetValue()
        self.chartObject.ToString()
        self.WebView.SetPage(self.chartObject.page, "")

    def ConstructGraphCode(self, codes):
        pass

class VarPanel(wx.Panel):
    def __init__(self, parent, id, grid, chartObject):
        wx.Panel.__init__(self, parent, -1, size=(250, -1))
        self.grid = grid
        self.parent = parent
        self.chartObject = chartObject
        self.stats=["Frequencies","Sum","Mean","Median","Minimum","Maximum",\
                "Range","Variance","Standard deviation","Standard error"]
        if not grid:
            variables = ['Var 001 (IV)', 'Var 002 (IV)', 'Var 003 (DV)']
        else:
            ColsUsed, self.ColNums = self.grid.GetUsedCols()
            variables = ['None'] + ColsUsed
        wx.StaticText(self, -1, "Variables", pos=(20,20))
        wx.StaticText(self, -1, "Chart this variable:", pos=(20,50))
        self.DV = wx.ComboBox(self, -1, size=(190,-1),pos=(20,70), choices = variables)
        wx.StaticText(self, -1, "by:", pos=(20,110))
        self.stat = wx.ComboBox(self, -1, size=(190,-1), pos=(20,130),choices=self.stats)
        wx.StaticText(self, -1, "Organised by:",pos=(20,170))
        self.IV = wx.ComboBox(self, -1, size=(190,-1), pos=(20,190),choices=variables)

        acceptbutton = wx.Button(self, 711, "Draw this graph", pos=(15,250))
        self.SetAutoLayout(True)
        self.Layout()
        wx.EVT_BUTTON(acceptbutton, 711, self.ChangeVars)
        self.ChangeVars(None)

    def GetSetDV(self, col_DV, col_IV):
        if col_DV == 0:
            self.valid_content = False
        else:
            self.valid_content = True
            name_DV = self.grid.GetColLabelValue(col_DV-1)
            self.chartObject.yAxis_title = name_DV
            test = self.stat.GetStringSelection()
            if col_IV == 0: # no grouping
                data = self.grid.GetColumnData(col_DV-1)
                values, freqs = AllRoutines.UniqueVals(data)
            else: # is grouping
                data_IV = self.grid.GetColumnRawData(col_IV-1)
                data_DV = self.grid.GetColumnData(col_DV-1)
                groups = GetGroups([data_IV])
                data = []
                for group in groups:
                    data_section = numpy.array(ExtractGroupsData(group, [data_IV], data_DV))
                    if test == "":
                        pass
                    elif test == "Frequencies":
                        data.append(AllRoutines.Count(data_section))
                    elif test == "Sum":
                        data.append(AllRoutines.Sum(data_section))
                    elif test == "Mean":
                        data.append(AllRoutines.Mean(data_section))
                    elif test == "Median":
                        data.append(AllRoutines.Median(data_section))
                    elif test == "Minimum":
                        data.append(AllRoutines.Minimum(data_section))
                    elif test == "Maximum":
                        data.append(AllRoutines.Maximum(data_section))
                    elif test == "Range":
                        data.append(AllRoutines.Range(data_section))
                    elif test == "Variance":
                        data.append(AllRoutines.SampVar(data_section))
                    elif test == "Standard deviation":
                        data.append(AllRoutines.SampStdDev(data_section))
                    elif test == "Standard error":
                        data.append(AllRoutines.StdErr(data_section))
            self.chartObject.data = [data]
            yAxisText = '%s of %s'%(test, name_DV)
            self.chartObject.yAxis_title = yAxisText

    def GetSetIV(self, col_IV):
        if col_IV == 0:
            # remove x-axis details or specify no x-axis details
            self.chartObject.xAxis_categories = None
            self.chartObject.xAxis_min = None
            self.chartObject.xAxis_max = None
            self.chartObject.xAxis_minTickInterval = None
            self.chartObject.zAxis_TickInterval = None
            test = self.stat.GetStringSelection()
            yAxisText = '%s'%(test)
            self.chartObject.yAxis_title = yAxisText
        else:
            name_IV = self.grid.GetColLabelValue(col_IV - 1)
            data_IV = self.grid.GetColumnRawData(col_IV - 1)
            values, freqs = AllRoutines.UniqueVals(data_IV)
            self.chartObject.xAxis_title = name_IV
            self.chartObject.xAxis_categories = values
            self.chartObject.xAxis_min = None
            self.chartObject.xAxis_max = None
            self.chartObject.xAxis_minTickInterval = None
            self.chartObject.zAxis_TickInterval = None
            test = self.stat.GetStringSelection()
            yAxisText = '%s'%(test)
            self.chartObject.yAxis_title = yAxisText

    def ChangeVars(self, event):
        col_IV = self.IV.GetSelection()
        self.GetSetIV(col_IV)
        col_DV = self.DV.GetSelection()
        self.GetSetDV(col_DV, col_IV)
        if self.valid_content:
            self.chartObject.ToString()
            self.parent.preview.SetPage(self.chartObject.page,"")
        else:
            help_prompt = "<br /><br /><br /><p>To create a chart, simply select which variable you want to display (to the left of this message)"
            self.parent.preview.SetPage(help_prompt, "")
        #print self.chartObject.page

    def ToString(self, inData):
        try:
            outString = '","'.join([str(idx) for idx in inData])
            return outString
        except:
            return inData

class DataObject(object):
    def __init__(self, data):
        self.data = data

class ChartObject(object):
    def __init__(self):
        self.charthtml = """<!DOCTYPE html>\n<html>\n\t<head>\n\t\t<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>\n\t\t<script src="http://code.highcharts.com/highcharts.js"></script>\n\t\t\t<script src="http://code.highcharts.com/modules/exporting.js"></script>\n\t\t\t<script src="/js/themes/gray.js"></script>\n\t\t\t<style>\n\t\t\t\tbody { font-family: helvectica, arial, \'lucida sans\'; }\n        </style>\n\t</head>\n\t<body>\n"""
        self.title_text = ""
        #self.chart_anim = { animation: false }
        self.chart_type = "area"
        self.subtitle_text = ""
        self.xAxis_title = None
        self.xAxis_categories = []
        self.xAxis_min = None
        self.xAxis_max = None
        self.xAxis_minTickInterval = None
        self.xAxis_tickInterval = None
        self.yAxis_title = "y axis"
        self.yAxis_categories = None
        self.yAxis_min = None
        self.yAxis_max = None
        self.yAxis_minTickInterval = None
        self.yAxis_tickInterval = None
        self.legend_align = "do not show"
        self.legend_verticalAlign = "bottom"
        self.chart_series = None
        self.data = None
        self.ToString()

    def FloatsToString(self, inList):
        try:
            return '","'.join(inList)
        except TypeError:
            newList = ','.join([str(item) for item in inList])
            return newList

    def ListToString(self, inList):
        # assumes a single list (i.e., not a list of lists)
        try:
            return '","'.join(inList)
        except TypeError:
            newList = '","'.join([str(item) for item in inList])
            return newList

    def chart(self):
        chartsbit = '\tchart: {\n'
        if self.chart_type:
            chartsbit += '\t\ttype: "%s"'%(self.chart_type)
        if self.subtitle_text:
            pass
        chartsbit += '\t},\n'
        chartsbit += '\tcredits: {\n\t\ttext: "Analysed with Salstat",\n\t\thref: "http://www.salstat.com"\n\t},\n'
        return chartsbit

    def yAxis(self):
        yaxisbit = '\tyAxis: {\n'
        if self.yAxis_min:
            yaxisbit += '\t\tmin: "%s",\n'%(self.yAxis_min)
        if self.yAxis_max:
            yaxisbit += '\t\tmax: "%s",\n'%(self.yAxis_max)
        if self.yAxis_minTickInterval:
            yaxisbit += '\t\tminTickInterval: %s,\n'%(self.yAxis_minTickInterval)
        if self.yAxis_tickInterval:
            yaxisbit += '\t\ttickInterval: %s,\n'%(self.yAxis_tickInterval)
        if self.yAxis_title:
            yaxisbit += '\t\ttitle: { text: "%s" }\n'%(self.yAxis_title)
        yaxisbit += '\t},\n'
        return yaxisbit

    def xAxis(self):
        xaxisbit = '\txAxis: {\n'
        if self.xAxis_min:
            xaxisbit += '\t\tmin: "%s",\n'%(self.xAxis_min)
        if self.xAxis_max:
            xaxisbit += '\t\tmax: "%s",\n'%(self.xAxis_max)
        if self.xAxis_minTickInterval:
            xaxisbit += '\t\tminTickInterval: %s,\n'%(self.xAxis_minTickInterval)
        if self.xAxis_tickInterval:
            xaxisbit += '\t\ttickInterval: %s,\n'%(self.xAxis_tickInterval)
        if self.xAxis_categories != None:
            xaxisbit += '\t\tcategories: ["%s"],\n'%(self.ListToString(self.xAxis_categories))
        if self.xAxis_title:
            xaxisbit += '\t\ttitle: { text: "%s" }\n'%(self.xAxis_title)
        xaxisbit += '\t},\n'
        return xaxisbit

    def title(self):
        titlebit = '\ttitle: {\n'
        if self.title_text != "":
            titlebit += '\t\ttext: "%s"\n'%(self.title_text)
        titlebit += '\t},\n'
        return titlebit

    def subtitle(self):
        subtitlebit = '\tsubtitle: {\n'
        if self.subtitle_text != "":
            subtitlebit += '\t\ttext: "%s,"\n'%(self.subtitle_text)
        subtitlebit += '\t},\n'
        return subtitlebit

    def legend(self):
        legendbit = '\tlegend: {\n'
        if self.legend_align:
            legendbit += '\t\talign: "%s",\n'%(self.legend_align)
        if self.legend_verticalAlign:
            legendbit += '\t\tverticalAlign: "%s",\n'%(self.legend_verticalAlign)
        if self.legend_align == "do not show":
            legendbit += '\t\tenabled: false,\n'
        legendbit += '\t},\n'
        return legendbit

    def series(self):
        if self.data:
            seriesbit = '\tseries: ['
            for data_set in self.data:
                datastr = self.FloatsToString(data_set)
                seriesbit += '{\n'
                if datastr:
                    seriesbit += '\t\tdata: [%s]\n\t},'%(datastr)
            seriesbit += '\t]\n'
        else:
            seriesbit = ''
        return seriesbit

    def ToString(self):
        # converts all attributes to a HighCharts string
        # head and tail
        self.chartLine = """\t$(function () {\n\t$("#chart0001").highcharts({\n""" + \
                self.chart() + self.title() + self.subtitle() + \
                self.xAxis() + self.yAxis() + self.legend() + \
                self.series() + \
                """\t});\n});\n"""
        #print self.chartLine
        self.page = '%s<div id="chart0001" style="width:100&amp; height: auto;">\n<script type="text/javascript">\n%s</script>\n</div>\n</body>\n</html>'%(self.charthtml, self.chartLine)

    def FinalToString(self):
        # converts all attributes to a HighCharts string ready for the output screen
        # uses timestamp as DIV id
        t = str(time.time()).translate(None, '.')
        self.chartLine = """\t$(function () {\n\t$("#Chart_%s").highcharts({\n"""%t + \
                self.chart() + self.title() + self.subtitle() + \
                self.xAxis() + self.yAxis() + self.legend() + \
                self.series() + \
                """\t});\n});\n"""
        #print self.chartLine
        return '<div id="Chart_%s" style="width:100&amp; height: auto;">\n<script type="text/javascript">\n%s</script>\n</div>\n'%(t, self.chartLine)

#---------------------------------------------------------------------------
# main loop
if __name__ == '__main__':
    app = wx.App()
    frame = ChartWindow(None)
    frame.Show(True)
    frame.preview.SetPage(frame.chartObject.page,"")
    #print frame.chartObject.page
    #frame.preview.SetPage(frame.chartObject.chartLine,"")
    app.MainLoop()

