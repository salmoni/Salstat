#!/usr/bin/env python

import wx
import wx.html2 as html2lib
import wx.propgrid as wxpg
import images
import sys, numpy
import AllRoutines

#---------------------------------------------------------------------------
# call instance of DataGrid
# This is main interface of application
class ChartWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self,parent,-1,"CHARTS", size=(1000,600), pos=(50,50))
        self.grid = parent
        self.CreateStatusBar()
        #self.SetStatusText('SalStat Statistics')
        self.chartObject = ChartObject()
        NewIcon = images.getNewBitmap()
        OpenIcon = images.getOpenBitmap()
        SaveIcon = images.getSaveBitmap()
        PrintIcon = images.getPrintBitmap()
        toolBar = self.CreateToolBar(wx.TB_HORIZONTAL|wx.NO_BORDER| \
                                    wx.TB_3DBUTTONS | wx.TB_TEXT)
        #ToolNew = wx.ToolBarToolBase(toolBar)
        #toolBar.AddTool(10, NewIcon,"New")
        toolBar.AddSimpleTool(10, NewIcon,"New")
        toolBar.AddSimpleTool(20, OpenIcon,"Open")
        toolBar.AddSimpleTool(30, SaveIcon,"Save")
        toolBar.AddSimpleTool(50, PrintIcon,"Print")
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

class ControlPanel(wx.Panel):
    def __init__(self, parent, id, chartObject, webview):
        wx.Panel.__init__(self, parent, -1, size=(250,-1))
        self.chartObject = chartObject
        self.WebView = webview
        self.types = ['line', 'spline', 'area', 'areaspline', 'column', \
                'bar', 'pie', 'scatter']
        self.align =  ["left", "center", "right", "do not show"]
        self.valign = ["top","middle","bottom"]

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

        changebutton = wx.Button(self, 710, "Change settings")
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
            variables = ColsUsed
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

    def ChangeVars(self, event):
        sel_IV = self.IV.GetSelection()
        sel_DV = self.DV.GetSelection()
        idx_IV = self.ColNums[sel_IV]
        idx_DV = self.ColNums[sel_DV]
        name_IV = self.grid.GetColLabelValue(idx_IV)
        name_DV = self.grid.GetColLabelValue(idx_DV)
        IV = self.grid.GetColumnData(idx_IV)
        DV = self.grid.GetColumnData(idx_DV)
        stat = self.stats[self.stat.GetSelection()]
        values, freqs = AllRoutines.UniqueVals(IV)
        if stat == "Frequencies":
            # we have all we need already
            data = freqs
        else:
            data = []
            for val in values:
                idcs = numpy.equal(IV, val)
                try:
                    subset = DV[idcs]
                except IndexError:
                    subset = []
                    for idx, cell in enumerate(IV):
                        if cell == val:
                            subset.append(DV[idx])
                    subset = numpy.array(subset)
                if stat == "Sum":
                    v = AllRoutines.Sum(subset)
                elif stat == "Mean":
                    v = AllRoutines.Mean(subset)
                elif stat == "Median":
                    v = AllRoutines.Median(subset)
                elif stat == "Minimum":
                    v = AllRoutines.Minimum(subset)
                elif stat == "Maximum":
                    v = AllRoutines.Maximum(subset)
                elif stat == "Range":
                    v = AllRoutines.Range(subset)
                elif stat == "Variance":
                    v = AllRoutines.SampVar(subset)
                elif stat == "Standard deviation":
                    v = AllRoutines.SampStdDev(subset)
                elif stat == "Standard Error":
                    v = AllRoutines.StdErr(subset)
                else:
                    v = None
                data.append(v)
        self.chartObject.data = [DataObject(data)]
        self.chartObject.data[0].name = name_DV
        self.chartObject.xAxis_categories = values
        self.chartObject.ToString()
        self.parent.preview.SetPage(self.chartObject.page,"")

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
        self.xAxis_categories = ["Apples", "Bananas", "Oranges"]
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
            xaxisbit += '\ttitle: { text: "%s" }\n'%(self.xAxis_title)
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
            for datum in self.data:
                datastr = self.FloatsToString(datum.data)
                namestr = datum.name
                seriesbit += '{\n'
                if namestr:
                    seriesbit += '\t\tname: "%s",\n'%(namestr)
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

