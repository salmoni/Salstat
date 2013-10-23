"""
DescriptivesFrame.py

A wxPython dialog to allow users to select a range of descriptive
statistics and variables for analysis.

"""

import wx






if __name__ == '__main__':
    app = wx.App()
    frame = DFrame(None)
    frame.Show(True)
    app.MainLoop()

