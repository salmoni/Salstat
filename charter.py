#!/usr/bin/env python

"""
charter.py

A chart drawing module for Salstat
(c) 2013, Alan James Salmoni

This is a wx frame with a html2.WebView. The operation is done all in Javascript.
"""

import wx
import wx.html2 as html2lib
import wx.propgrid as wxpg
import images
import sys
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

#---------------------------------------------------------------------------
# This is main interface of application
class ChartWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self,parent,-1,"CHARTS", size=(1000,600), pos=(50,50))
        self.CreateStatusBar()
        #self.SetStatusText('SalStat Statistics')
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
        fin = open('ChartCreate.html','r')
        self.page = fin.read()
        fin.close()
        self.webview = html2lib.WebView
        self.preview = self.webview.New(self, size=(100,100))
        self.preview.SetPage(self.page,"")

def SetServer():
    HandlerClass = SimpleHTTPRequestHandler
    ServerClass  = BaseHTTPServer.HTTPServer
    Protocol     = "HTTP/1.0"
    port = 8008
    server_address = ('127.0.0.1', port)

    HandlerClass.protocol_version = Protocol
    httpd = ServerClass(server_address, HandlerClass)

    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."
    #httpd.serve_forever()
    httpd.server_activate()


#---------------------------------------------------------------------------
# main loop
if __name__ == '__main__':
    SetServer()
    app = wx.App()
    chartFrame = ChartWindow(None)
    chartFrame.Show(True)
    app.MainLoop()

