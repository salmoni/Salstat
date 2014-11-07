"""
exportsSQLite.py
A module to save Salstat files to an SQLite database
There are three tables:
1. Data
2. Variables' meta data
3. Output

We're thinking of including the history too so that each analysis session is completely
auditable.
"""


import sqlite3

def exporttoSQLiteTEST(datagrid):
    filename = "/Users/alan/Projects/SQLitefile.sqlite"
    exporttoSQLite(filename, datagrid)

def exporttoSQLite(filename, datagrid):
    # first, open the SQLite file (filename should include the path)
    
    # open connection to database
    try:
        conn = sqlite3.connect(filename)
        c = conn.cursor()
    except:
        print "Could not open database"
        return
    # then save meta-data to a table
    # write variables table
    try:
        c.execute('''CREATE TABLE variables
                    (name text, align text, label text, measure text, ivdv text, 
                    decplaces text, missingvalues text)''')
    except sqlite3.OperationalError:
       pass
    # now save each variable's meta data in turn
    for item in datagrid.meta.keys():
        v = datagrid.meta[item]
        ln = '''INSERT INTO variables VALUES
                    ("%s", "%s", "%s", "%s", "%s", " ", " ")'''%(
                    v['name'], v['align'], v['label'], v['measure'], v['ivdv'])
        #print ln
        c.execute(ln)
    # then commit
    conn.commit()
    # then save data to a table
    # then save the output
    # wrap up
    conn.close()
    