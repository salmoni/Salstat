"""
exportsSQLite.py
A module to save Salstat files to an SQLite database
There are two tables:
1. Data (including meta data)
2. Output

We're thinking of including the history too so that each analysis session is completely
auditable.
"""


import sqlite3, os.path

def exporttoSQLiteTEST(datagrid, output):
    print output.WholeOutString
    filename = "/Users/alan/Projects/SQLitefile.sqlite"
    exporttoSQLite(filename, datagrid, output)

def importfromSQLite(filename, datagrid, output):
    # First open the database (filename should include the full path)
    # Tests if file exists so it's not created if not there
    if os.path.exists(filename):
        conn = sqlite3.connect(filename)
        c = conn.cursor()
        # clear the grid
        datagrid.ClearGrid()
        # size the incoming data
        numcols = 0
        numrows = 0
        for item in c.execute("SELECT * FROM data"):
            numcols += 1
            rowlen = len(item[7].split(','))
            if rowlen > numrows:
                numrows = rowlen
        datagrid.ResizeGrid(numcols, numrows, spare=10)
        # populate the grid with data & meta data
        datagrid.meta = {}
        for index, v in enumerate(c.execute("SELECT * FROM data")):
            obj= {'name': v[0], 'align':v[1], 'label':v[2], 'measure':v[3], 'ivdv': v[4],
                    'decplaces':v[5],'missingvalues':v[6]}
            datagrid.AddNewMeta(v[0],obj)
            datagrid.SetColLabelValue(index, v[0])
            if len(v[7]) > 0:
                data = v[7].split(',') # won't work if commas are in the cells
                for idx in range(len(data)):
                    datum = data[idx]
                    datagrid.SetCellValue(idx, index, datum)
        # read & show output
        # wrap up
        conn.close()
    else:
        # file does not exist
        pass

def exporttoSQLite(filename, datagrid, output=None):
    # first, open the SQLite file (filename should include the full path)
    # open connection to database
    try:
        conn = sqlite3.connect(filename)
        c = conn.cursor()
    except:
        print "Could not open database"
        return
    # then save data and meta-data to a table
    # First drop the original table
    ln = "DROP TABLE data"
    try:
        c.execute(ln)
    except sqlite3.OperationalError:
        pass
    # write variables table
    try:
        c.execute('''CREATE TABLE data
                    (name text, align text, label text, measure text, ivdv text, 
                    decplaces text, missingvalues text, data text)''')
    except sqlite3.OperationalError:
       pass
    # now save each variable's meta data in turn
    # needs changing because the order (which is important) isn't saved
    numcols = datagrid.GetNumberCols()
    for item in range(numcols):
        label = datagrid.GetColLabelValue(item)
        v = datagrid.meta[label]
        vars = datagrid.GetVariableData(item)
        if type(vars) == list:
            data = ', '.join(vars)
        else:
            data = ''
        c.execute("INSERT INTO data VALUES (?,?,?,?,?,?,?,?)",(v['name'], v['align'], v['label'], v['measure'], v['ivdv'], "","",data))
        #print ln
        #c.execute(ln)
    # then commit
    conn.commit()
    # then save the output
    if output:
        try:
            ln = "DROP TABLE output"
            c.execute(ln)
        except sqlite3.OperationalError:
            pass
        ln = "CREATE TABLE output (html text)"
        c.execute(ln)
        #print output.WholeOutString
        c.execute("INSERT INTO output VALUES (?)",(output.WholeOutString,))
        conn.commit()
    # wrap up
    conn.close()




