import wx
from wx.stc import *
import wx.grid as gridlib
import numpy
import numpy.ma as ma
import string, os

#---------------------------------------------------------------------------
# class for variables grid

class VariablesGrid(gridlib.Grid):
    def __init__(self, parent, grid, cols=None):
        gridlib.Grid.__init__(self, parent)
        self.grid = grid
        self.backgroundColour = wx.Colour(216,122,50,127)
        self.parent = parent
        self.SetGridLineColour(wx.LIGHT_GREY)
        self.CreateGrid(12, cols)
        self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_BOTTOM)
        self.SetRowLabelSize(125)
        self.SetRowLabelAlignment(0, 0)
        self.SetRowLabelValue(0, "Variable name")
        self.SetRowLabelValue(1, "Alignment")
        self.SetRowLabelValue(2, "Label")
        self.SetRowLabelValue(3, "Measure")
        self.SetRowLabelValue(4, "Variable type")
        self.SetRowLabelValue(5, "Decimal places")
        self.SetRowLabelValue(6, "Missing values")
        self.SetRowLabelValue(7, " ")
        self.SetRowLabelValue(8, "Your data row 1")
        self.SetRowLabelValue(9, "Your data row 2")
        self.SetRowLabelValue(10, "Your data row 3")
        self.SetRowLabelValue(11, "Your data row 4")
        self.choices_align = ['Left','Centre','Right']
        self.choice_align = gridlib.GridCellChoiceEditor(self.choices_align, False)
        self.choices_measure = ['Nominal','Ordinal','Interval','Ratio']
        self.choice_measure = gridlib.GridCellChoiceEditor(self.choices_measure, False)
        self.choices_ivdv = ['None','IV','DV']
        self.choice_ivdv  = gridlib.GridCellChoiceEditor(self.choices_ivdv, False)
        self.ResetGrid()
        gridlib.EVT_GRID_CELL_CHANGE(self, self.CellChanged)

    def BackToData(self):
        # Called when the user moves back to the data grid
        numcols = self.GetNumberCols()
        for col in range(numcols):
            label = self.GetCellValue(0, col)
            self.grid.SetColLabelValue(col, label)

    def CellChanged(self, event):
        row = event.GetRow()
        col = event.GetCol()
        val = self.GetCellValue(row, col).lower()
        oldname = event.GetString()
        label = self.grid.GetColLabelValue(col)
        if row == 0: # change variable name
            newname = self.GetCellValue(0, col)
            if newname not in self.grid.meta.keys(): # unused name
                obj = self.grid.meta[oldname]
                self.grid.AddNewMeta(newname, obj)
                del self.grid.meta[oldname]
            else:
                self.SetCellValue(0, col, oldname)
        elif row == 1: # changed column text alignment
            if val[0].lower() == 'l':
                self.SetCellValue(1, col, "Left")
                cellattr = gridlib.GridCellAttr()
                cellattr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
                self.grid.SetColAttr(col, cellattr)
                self.grid.meta[label]['align'] = "Left"
            elif val[0].lower() == 'r':
                self.SetCellValue(1, col, "Right")
                cellattr = gridlib.GridCellAttr()
                cellattr.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
                self.grid.SetColAttr(col, cellattr)
                self.grid.meta[label]['align'] = "Right"
            elif val[0].lower() == 'c':
                self.SetCellValue(1, col, "Centre")
                cellattr = gridlib.GridCellAttr()
                cellattr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                self.grid.SetColAttr(col, cellattr)
                self.grid.meta[label]['align'] = "Centre"
            else:
                self.SetCellValue(row, col, oldname)
        elif row == 5: # decimal places
            pass

    def ResetGrid(self):
        # called when the user clicks to view the tab. This updates the view
        numcols = self.grid.GetNumberCols()
        self.ResizeGrid()
        for i in range(numcols):
            #attr = gridlib.GridCellAttr()
            #attr.SetEditor(self.choice_align)
            self.SetColLabelValue(i, str(i + 1))
            colLabel = self.grid.GetColLabelValue(i)
            meta = self.grid.meta[colLabel]
            self.SetCellValue(0, i, meta["name"])
            #self.SetCellEditor(1, i, self.choice_align)
            self.SetCellValue(1, i, meta["align"])
            self.SetCellValue(2, i, meta["label"])
            #self.SetCellEditor(3, i, choice_measure)
            self.SetCellValue(3, i, meta["measure"])
            #self.SetCellEditor(4, i, choice_ivdv)
            self.SetCellValue(4, i, meta["ivdv"])
            self.SetCellValue(5, i, str(meta["decplaces"]))
            self.SetCellValue(6, i, meta["missingvalues"])
            for j in range(4):
                cellValue = self.grid.GetCellValue(j, i)
                self.SetCellValue(j+8, i, cellValue)
        #self.SetRowAttr(1, attr)

    def ResizeGrid(self):
        self.ClearGrid()
        self.DeleteCols(0, self.GetNumberCols(), False)
        self.InsertCols(0, self.grid.GetNumberCols(), False)        

#---------------------------------------------------------------------------
# class for grid - used as datagrid.
class DataGrid(gridlib.Grid):
    def __init__(self, parent, inits=None):
        gridlib.Grid.__init__(self, parent)
        self.backgroundColour = wx.Colour(216,122,50,127)
        self.parent = parent
        self.named = False
        self.Saved = True
        self.filename = "Untitled"
        self.moveTo = None
        self.SetGridLineColour(wx.LIGHT_GREY)
        self.inits = inits
        self.CreateGrid(int(self.inits.get("gridcellsy")), \
                                    int(self.inits.get("gridcellsx")))
        self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_BOTTOM)
        #for i in range(20):
            #self.SetColFormatFloat(i, 8, 4)
        gridlib.EVT_GRID_CELL_CHANGE(self, self.AlterSaveStatus)
        gridlib.EVT_GRID_RANGE_SELECT(self, self.RangeSelected)
        self.wildcard = "Any File (*.*)|*.*|" \
                        "ASCII data format (*.dat)|*.dat|" \
                        "SalStat Format (*.xml)|*.xml"
        self.colnames = 21
        self.BeginMeta()

    def AddNewMeta(self, colname, obj=None):
		varObj = {'name': colname}
		if obj:
		    varObj['label'] = obj['label']
		    varObj['align'] = obj['align']
		    varObj['measure'] = obj['measure']
		    varObj['ivdv'] = obj['ivdv']
		    varObj['decplaces'] = obj['decplaces']
		    varObj['missingvalues'] = obj['missingvalues']
		else:
		    varObj['label'] = colname
		    varObj['align'] = 'Left'
		    varObj['measure'] = 'None set'
		    varObj['ivdv'] = 'None set'
		    varObj['decplaces'] = ''
		    varObj['missingvalues'] = ''
		self.meta[colname] = varObj

    def BeginMeta(self):
        self.meta = {}
        ncols = self.GetNumberCols()
        for colidx in range(ncols):
            labelObj = {}
            colname = self.GetColLabelValue(colidx)
            varObj = {'name': colname}
            varObj['align'] = 'Left'
            varObj['label'] =colname
            varObj['measure'] = 'None set'
            varObj['ivdv'] = 'None set'
            varObj['decplaces'] = ''
            varObj['missingvalues'] = ''
            self.meta[colname] = varObj

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
        try:
            v = float(value)
            self.SetCellBackgroundColour(row, col, wx.WHITE)
        except ValueError:
            self.SetCellBackgroundColour(row, col, self.backgroundColour)
        xmlevt = '<data row="'+str(row)+'" col="'+str(col)+'">'+str(value)+'</data>\n'
        #hist.AppendEvent(xmlevt)
        #print hist.history
        # check if missing data and mark background if it is

    def CutData(self, event):
        buffer = wx.TextDataObject()
        Cells = self.GetSelectedCells()
        Cols  = self.GetSelectedCols()
        Rows  = self.GetSelectedRows()
        TopLt = self.GetSelectionBlockTopLeft()
        BotRt = self.GetSelectionBlockBottomRight()
        if len(TopLt) > 0:
            top = TopLt[0][0]
            left = TopLt[0][1]
            bot = BotRt[0][0] + 1
            right = BotRt[0][1] + 1
            data = []
            for row in range(top, bot):
                line = []
                for col in range(left, right):
                    val = self.GetCellValue(row, col)
                    line.append(val)
                data.append('\t'.join(line))
            data = '\r'.join(data)
        elif len(Cols) > 0:
            data = []
            for row in range(self.GetNumberRows()):
                line = []
                for col in Cols:
                    line.append(self.GetCellValue(row, col))
                data.append('\t'.join(line))
            data = '\r'.join(data)
        elif len(Rows) > 0:
            data = []
            for row in Rows:
                line = []
                for col in range(self.GetNumberCols()):
                    line.append(self.GetCellValue(row, col))
                data.append('\t'.join(line))
            data = '\r'.join(data)
        elif len(Cells) > 0:
            print "CELLS!"
        else:
            currentcol = self.GetGridCursorCol()
            currentrow = self.GetGridCursorRow()
            data = self.GetCellValue(currentrow, currentcol)
        if (wx.TheClipboard.Open()):
            buffer.SetText(data)
            wx.TheClipboard.SetData(buffer)
            wx.TheClipboard.Close()
            if len(TopLt) > 0:
                for row in range(top, bot):
                    for col in range(left, right):
                        self.SetCellValue(row, col, '')
            elif len(Cols) > 0:
                for row in range(0, self.GetNumberRows()):
                    for col in Cols:
                        self.SetCellValue(row, col, '')
            elif len(Rows) > 0:
                for row in Rows:
                    for col in range(0, self.GetNumberCols()):
                        self.SetCellValue(row, col, '')
            #self.SetCellValue(currentrow, currentcol, '')
            self.Saved = False

    def CopyData(self, event):
        buffer = wx.TextDataObject()
        Cells = self.GetSelectedCells()
        Cols  = self.GetSelectedCols()
        Rows  = self.GetSelectedRows()
        TopLt = self.GetSelectionBlockTopLeft()
        BotRt = self.GetSelectionBlockBottomRight()
        if len(TopLt) > 0:
            top = TopLt[0][0]
            left = TopLt[0][1]
            bot = BotRt[0][0] + 1
            right = BotRt[0][1] + 1
            data = []
            for row in range(top, bot):
                line = []
                for col in range(left, right):
                    val = self.GetCellValue(row, col)
                    line.append(val)
                data.append('\t'.join(line))
            data = '\r'.join(data)
        elif len(Cols) > 0:
            data = []
            for row in range(self.GetNumberRows()):
                line = []
                for col in Cols:
                    line.append(self.GetCellValue(row, col))
                data.append('\t'.join(line))
            data = '\r'.join(data)
        elif len(Rows) > 0:
            data = []
            for row in Rows:
                line = []
                for col in range(self.GetNumberCols()):
                    line.append(self.GetCellValue(row, col))
                data.append('\t'.join(line))
            data = '\r'.join(data)
        elif len(Cells) > 0:
            print "CELLS!"
        else:
            currentcol = self.GetGridCursorCol()
            currentrow = self.GetGridCursorRow()
            data = self.GetCellValue(currentrow, currentcol)
        if (wx.TheClipboard.Open()):
            buffer.SetText(data)
            wx.TheClipboard.SetData(buffer)
            wx.TheClipboard.Close()

    def PasteData(self, event):
        buffer = wx.TextDataObject()
        Cols = self.GetSelectedCols()
        Rows = self.GetSelectedRows()
        maxCols = self.GetNumberCols()
        maxRows = self.GetNumberRows()
        if len(Cols) > 0:
            currentcol = Cols[0]
            currentrow = 0
        elif len(Rows) > 0:
            currentcol = 0
            currentrow = Rows[0]
        else:
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
                maxWidth = 0
                for row in rows:
                    width = len(row.split('\t'))
                    if width > maxWidth:
                        maxWidth = width
                diffCols = (currentcol + maxWidth + 10) - maxCols
                diffRows = (currentrow + len(rows) + 10) - maxRows
                if diffCols > 0:
                    self.AppendCols(diffCols)
                if diffRows > 0:
                    self.AppendRows(diffRows)
                for row in range(len(rows)):
                    cells = rows[row].split('\t')
                    for col in range(len(cells)):
                        val = cells[col]
                        self.SetCellValue(currentrow+row, currentcol+col, val)
            self.Saved = False

    def EditGrid(self, event, numrows):
        insert = self.AppendRows(numrows)

    def DeleteCurrentCol(self, event):
        Cols  = self.GetSelectedCols()
        TopLt = self.GetSelectionBlockTopLeft()
        BotRt = self.GetSelectionBlockBottomRight()
        if len(Cols) > 0:
            Cols.reverse()
            for col in Cols:
                colname = self.GetColLabelValue(col)
                self.DeleteCols(col, 1)
                del self.meta[colname]
        elif len(TopLt) < 1 and len(BotRt) < 1:
            currentcol = self.GetGridCursorCol()
            colname = self.GetColLabelValue(currentcol)
            self.DeleteCols(currentcol, 1)
            del self.meta[colname]
        else:
            tl = TopLt[0][1]
            br = BotRt[0][1] + 1
            #self.DeleteCols(tl, br-tl)
            #del self.meta[col]
            for i in range(br-tl):
                colname = self.GetColLabelValue(tl)
                self.DeleteCols(tl, 1)
                del self.meta[colname]
        self.AdjustScrollbars()
        self.Saved = False

    def DeleteCurrentRow(self, event):
        Rows  = self.GetSelectedRows()
        TopLt = self.GetSelectionBlockTopLeft()
        BotRt = self.GetSelectionBlockBottomRight()
        if len(Rows) > 0:
            Rows.reverse()
            for row in Rows:
                self.DeleteRows(row, 1)
        elif len(TopLt) < 1 and len(BotRt) < 1:
            currentrow = self.GetGridCursorRow()
            self.DeleteRows(currentrow, 1)
        else:
            tl = TopLt[0][0]
            br = BotRt[0][0] + 1
            self.DeleteRows(tl, br-tl)
        self.AdjustScrollbars()
        self.Saved = False

    def InsertCol(self, event):
        Cols  = self.GetSelectedCols()
        TopLt = self.GetSelectionBlockTopLeft()
        BotRt = self.GetSelectionBlockBottomRight()
        if len(Cols) > 0: # column headers selected
            #Cols.reverse()
            for col in Cols:
                self.InsertCols(col, 1)
                label = "Var %03d"%(self.colnames)
                self.SetColLabelValue(col, label)
                self.colnames += 1
                self.AddNewMeta(label)
        elif len(TopLt) < 1 and len(BotRt) < 1: # single cell selected
            currentcol = self.GetGridCursorCol()
            self.InsertCols(currentcol, 1)
            label = "Var %03d"%(self.colnames)
            self.SetColLabelValue(currentcol, label)
            self.colnames += 1
            self.AddNewMeta(label)
        else: # block of cells selected
            tl = TopLt[0][1]
            br = BotRt[0][1] + 1
            for i in range(br-tl):
	            self.InsertCols(tl+i, 1)
	            label = "Var %03d"%(self.colnames)
	            self.SetColLabelValue(tl+i, label)
	            self.colnames += 1
	            self.AddNewMeta(label)
        self.AdjustScrollbars()
        self.Saved = False

    def InsertRow(self, event):
        Rows  = self.GetSelectedRows()
        TopLt = self.GetSelectionBlockTopLeft()
        BotRt = self.GetSelectionBlockBottomRight()
        if len(Rows) > 0:
            Rows.reverse()
            for row in Rows:
                self.InsertRows(row, 1)
        elif len(TopLt) < 1 and len(BotRt) < 1:
            currentrow = self.GetGridCursorRow()
            self.InsertRows(currentrow, 1)
        else:
            tl = TopLt[0][0]
            br = BotRt[0][0] + 1
            self.InsertRows(tl, br-tl)
        self.AdjustScrollbars()
        self.Saved = False

    def SelectAllCells(self, event):
        self.SelectAll()

    def ResizeGrid(self, nCols, nRows, spare=10):
        # check that data is saved before clearing!
        self.ClearGrid()
        # resize grid to accommodate data
        actual_cols = self.GetNumberCols()
        num_cols_to_append = nCols + spare
        self.DeleteCols(pos=0, numCols=actual_cols)
        self.AppendCols(numCols=num_cols_to_append)
        actual_rows = self.GetNumberRows()
        num_rows_to_append = nRows + spare
        self.DeleteRows(pos=0, numRows=actual_rows)
        self.AppendRows(numRows=num_rows_to_append)
        for i in range(self.GetNumberCols()):
        	label = "Var %03d"%(i+1)
        	self.SetColLabelValue(i, label)
        self.BeginMeta()

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
        ColsUsed
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

    def SaveAsDataASCII(self, filename):
        """
        default = self.inits.get('savedir')
        dlg = wx.FileDialog(self, "Save Data File", default,"",\
                                    "CSV text (*.csv)|*.csv|Plain text (*.txt)|*.txt", wx.SAVE)
        ico = wx.Icon('icons/PurpleIcon05_32.png',wx.BITMAP_TYPE_PNG)
        dlg.SetIcon(ico)
        if dlg.ShowModal() == wx.ID_OK:
        """
        self.inits.update({'savedir': filename})
        #filename = dlg.GetPath()
        fout = open(filename, "w")
        cols,waste = self.GetUsedCols()
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
                line = ",".join(datapoint)
            fout.write(line)
            fout.write('\n')
        fout.close
        self.Saved = True
        self.named = True
        path, self.filename = os.path.split(filename)
        #self.parent.SetTitle(self.filename)

    def SaveDataASCII(self, event):
        if self.named:
            defaultDir = self.inits.get('savedir')
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
                line = ",".join(datapoint)
                fout.write(line)
                fout.write('\n')
            fout.close
            self.Saved = True
        else:
            self.SaveAsDataASCII(None)

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
        default = self.inits.get('opendir')
        dlg = wx.FileDialog(self, "Load Data File", default,"","*.\
                                    dat|*.*", wx.OPEN)
        dlg.SetIcon(ico)
        if dlg.ShowModal() == wx.ID_OK:
            self.inits.update({'opendir': dlg.GetDirectory()})
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

    #########################################
    # New routines to retrieve data from grid
    def CheckBlank(self, cell):
        if len(cell) > 0:
            val = cell.isspace()
            return val
        else:
            return True

    def GetVariableData(self, col, vtype = None):
        """
        This is an important method. It returns the data for a single variable.
        Empty variable returns None
        Blanks after data are not returned
        Variable type can be specified as string (or None), int or float
        For string or None, all raw values are returned.
        For int, all figures are rounded to nearest decimal place and values that 
        cannot be converted are masked.
        For float, all values that cannot be converted to float are masked.
        All values matching the variable's 'missingvalue' are masked.
        It's inefficient and requires 2 passes but it should be reliable.
        """
        maxRow = self.GetNumberRows()
        meta = self.meta[self.GetColLabelValue(col)]
        missing = meta["missingvalues"]
        if col > self.GetNumberCols():
            return None
        maxIdx = -1
        for idx in range(maxRow):
            if not self.CheckBlank(self.GetCellValue(idx, col)):
                maxIdx = idx
        if maxIdx < 0:
            return None
        maxIdx = maxIdx + 1
        data = []
        if (vtype == None) or (vtype.lower() == "str"):
            for row in range(maxIdx):
                val = self.GetCellValue(row, col)
                if self.CheckBlank(val):
                    val = ""
                data.append(val)
        elif vtype.lower() == "int":
            data = ma.zeros(maxIdx,dtype='int')
            for row in range(maxIdx):
                val = self.GetCellValue(row, col)
                if (val == missing) or (self.CheckBlank(val)):
                    data[row] = ma.masked
                else:
                    try:
                        data[row] = int(round(float(val)))
                    except ValueError:
                        data[row] = ma.masked
        elif vtype.lower() == "float":
            data = ma.zeros(maxIdx,dtype='float')
            for row in range(maxIdx):
                val = self.GetCellValue(row, col)
                if (val == missing) or (self.CheckBlank(val)):
                    data[row] = ma.masked
                else:
                    try:
                        data[row] = float(val)
                    except ValueError:
                        data[row] = ma.masked
        return data

    # Routine to return a "clean" list of data from one column
    def GetColumnData(self, col):
        indata = []
        self.missing = 0
        label = self.GetColLabelValue(col)
        missingvalues = self.meta[label]['missingvalues']
        for i in range(self.GetNumberRows()):
            datapoint = self.GetCellValue(i, col)
            if (datapoint != '') and (datapoint != '.'):
                try:
                    value = float(datapoint)
                    if (str(value) in missingvalues):
                        self.missing = self.missing + 1
                    else:
                        indata.append(value)
                except ValueError:
                    pass
        return indata

    def GetColumnRawData(self, col):
        indata = []
        self.missing = 0
        for i in range(self.GetNumberRows()):
            datapoint = self.GetCellValue(i, col)
            if datapoint != '':
                label = self.GetColLabelValue(col)
                if datapoint != self.meta[label]['missingvalues']:
                    if datapoint.isspace() == False:
                        indata.append(datapoint)
                else:
                    self.missing += 1
        return indata

    def CleanData(self, col):
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
            smalllist = frame.grid.GetVariableData(numcols[i])
            biglist.append(smalllist)
        return numpy.array((biglist), numpy.Float)

