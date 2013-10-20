#!/usr/bin/env python

import wx
import wx.html2 as html2lib
import wx.propgrid as wxpg
import images
import sys

#---------------------------------------------------------------------------
# call instance of DataGrid
# This is main interface of application
class ChartWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self,parent,-1,"CHARTS", size=(1000,600), pos=(50,50))
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
        variables = ""
        self.variables = VarPanel(self, -1, variables)
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
        self.ctrl_title = wx.TextCtrl(self, -1, size=(200,-1),pos=(20,90))
        self.ctrl_subtitle = wx.TextCtrl(self, -1, size=(200,-1),pos=(20,140))
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
    def __init__(self, parent, id, variables):
        wx.Panel.__init__(self, parent, -1, size=(250, -1))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.variables = variables
        heading = wx.StaticText(self, -1, "Variables")
        variables = ['Var 001 (IV)', 'Var 002 (IV)', 'Var 003 (DV)']
        self.varlist = wx.CheckListBox(self, -1, choices=variables, \
                size=(220, -1), pos=(15,45))
        acceptbutton = wx.Button(self, 711, "Draw this graph")
        self.sizer.Add(heading, 0, flag=wx.ALL, border=15)
        self.sizer.Add(self.varlist, 1, wx.ALL, border=15)
        self.sizer.Add(acceptbutton, 0, flag=wx.ALL, border=15)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        self.Layout()
        wx.EVT_BUTTON(acceptbutton, 711, self.ChangeVars)

    def ChangeVars(self, event):
        checked = self.varlist.GetChecked()


class DataObject(object):
    def __init__(self, data):
        self.data = data

class ChartObject(object):
    def __init__(self):
        self.charthtml = """<!DOCTYPE html>\n<html>\n\t<head>\n\t\t<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>\n\t\t<script src="http://code.highcharts.com/highcharts.js"></script>\n\t\t\t<script src="http://code.highcharts.com/modules/exporting.js"></script>\n\t\t\t<script src="/js/themes/gray.js"></script>\n\t\t\t<style>\n\t\t\t\tbody { font-family: helvectica, arial, \'lucida sans\'; }\n        </style>\n\t</head>\n\t<body>\n"""
        self.title_text = "Fruit consumption"
        #self.chart_anim = { animation: false }
        self.chart_type = "area"
        self.subtitle_text = None
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
        self.data = [DataObject([5,7,3]), DataObject([4,2,6])]
        self.data[0].name = "Harry"
        self.data[1].name = "Tom"
        self.ToString()

    def ListToString(self, inList):
        # assumes a single list (i.e., not a list of lists)
        try:
            return '","'.join(inList)
        except TypeError:
            return ','.join([str(item) for item in inList])

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
        if self.xAxis_categories:
            xaxisbit += '\t\tcategories: ["%s"],\n'%(self.ListToString(self.xAxis_categories))
        if self.xAxis_title:
            xaxisbit += '\ttitle: { text: "%s" }\n'%(self.xAxis_title)
        xaxisbit += '\t},\n'
        return xaxisbit

    def title(self):
        titlebit = '\ttitle: {\n'
        if self.title_text:
            titlebit += '\t\ttext: "%s"\n'%(self.title_text)
        titlebit += '\t},\n'
        return titlebit

    def subtitle(self):
        subtitlebit = '\tsubtitle: {\n'
        if self.subtitle_text:
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
        seriesbit = '\tseries: ['
        for datum in self.data:
            datastr = self.ListToString(datum.data)
            namestr = datum.name
            seriesbit += '{\n'
            if namestr:
                seriesbit += '\t\tname: "%s",\n'%(namestr)
            if datastr:
                seriesbit += '\t\tdata: [%s]\n\t},'%(datastr)
        seriesbit += '\t]\n'
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

act = """$(function () { 

        series: [{
            name: "John",
            data: [5, 7, 3]
        }, {
            name: "Jane",
            data: [1, 0, 6]
        }]
    });
});"""


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

