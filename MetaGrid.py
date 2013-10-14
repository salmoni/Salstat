import wx
import wx.grid as gridlib

class MetaFrame(wx.Frame):
    def __init__(self, parent):
        # size the frame to 600x400 - will fit in any VGA screen
        wx.Frame.__init__(self,parent,-1,"Meta Grid", size=(600,\
                                    400))
        self.metaGrid = metaGrid(self, parent.grid)


class metaGrid(gridlib.Grid):
    def __init__(self, parent, grid):
        self.parent = parent
        ncols = grid.GetNumberCols()
        gridlib.Grid.__init__(self, parent)
        self.CreateGrid(22, ncols)
        #self.SetNumberCols() # 6 rows of meta, 1 gap, 15 rows
        rowLabels = ['Name','IV/DV','Alignment','Measure','Missing values','Labels',' ']
        for colidx in range(ncols):
            self.SetCellBackgroundColour(6, colidx, wx.LIGHT_GREY)
            for rowidx in range(7):
                self.SetRowLabelValue(rowidx, rowLabels[rowidx])
            for rowidx in range(15):
                self.SetRowLabelValue(rowidx+7, "Data %d"%(rowidx+1))
                val = grid.GetCellValue(rowidx, colidx)
                self.SetCellValue(rowidx+7, colidx, val)


