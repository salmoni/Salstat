"""
tabler.py
Creates tables in HTML for Salstat
Submit a list of [heading: value] pairs in the desired order
p-values are automatically formatted as %1.6f (all other floats as %5.3f?)

The first two routines are generic and for single answer results.

Following are a handful of tabler functions for particular tests

(c) 2013, Alan James Salmoni

"""

def table(ListofLists):
    ln1 = '<table class="table table-striped"><tr>'
    ln2 = '<tr>'
    for List in ListofLists:
        key = List[0]
        val = List[1]
        headhtml = '<th>%s</th>'%key
        if key == 'p':
            try:
                foothtml = '<td>%1.6f</td>'%val
            except TypeError:
                foothtml = '<td>n/a</td>'
        elif type(val) is int:
            foothtml = '<td>%d</td>'%val
        elif (type(val) is str) or (type(val) is unicode):
            foothtml = '<td>%s</td>'%val
        #elif type(val) is float:
        else:
            fltstr = str(val)
            foothtml = '<td>%s</td>'%fltstr
            # really need to figure out what parameters make a good display for each number
        ln1 = ln1 + headhtml
        ln2 = ln2 + foothtml
    ln1 = ln1 + '</tr>' + ln2 + '</tr>\n</table>\n'
    return ln1

def vtable(List):
    key = List[0]
    vals = List[1:]
    btn_id = ' id="%s"'%key
    chartbutton = '<a class="btn btn-mini dropdown-toggle"%s data-toggle="dropdown" \
            href="#">Chart</a>\n'%btn_id
    linehtml = '<tr><td>%s</td>'%(key)
    for val in vals:
        if key == 'p':
            try:
                linehtml = '<td>%1.6f</td>'%val
            except TypeError:
                linehtml = '<td>n/a</td>'
        elif type(val) is int:
            linehtml = linehtml + '<td>%d</td>'%val
        elif (type(val) is str) or (type(val) is unicode):
            linehtml = linehtml + '<td>%s</td>'%val
        elif type(val) is float:
            linehtml = linehtml + '<td>%s</td>'%str(val)
        elif type(val) is tuple:
            print "TUPLE!", val
        else:
            try:
                linehtml = linehtml + '<td>%s</td>'%str(val)
            except:
                pass
    linehtml = linehtml + '</tr>\n'
    return linehtml

def tableHinges(List):
    key = List[0]
    vals = List[1:]
    linehtml = '<tr><td>%s</td>'%(key)
    for val in vals:
        linehtml += '<td>%s, %s</td>'%(str(val[0]), str(val[1]))
    linehtml += '</tr>\n'
    return linehtml

def tableMultiples(vals, varName):
    table = '<h3>%s</h3><table class="table table-striped">\n'%varName
    table += '\t<tr><th>Value</th>'
    try:
        if vals['freqs']:
            table += '<th>Frequencies</th>'
    except ValueError:
        table += '<th>Frequencies</th>'
    try:
        if vals['props']:
            table += '<th>Proportions</th>'
    except ValueError:
        table += '<th>Proportions</th>'
    try:
        if vals['percs']:
            table += '<th>Percentages</th>'
    except ValueError:
        table += '<th>Percentages</th>'
    table += '</tr>\n'
    N = len(vals['values'])
    for idx in range(N):
        table += '\t<tr><td>%s</td>'%vals['values'][idx]
        try:
            if vals['freqs']:
                table += '<td>%s</td>'%vals['freqs'][idx]
        except ValueError:
            table += '<td>%s</td>'%vals['freqs'][idx]
        try:
            if vals['props']:
                table += '<td>%s</td>'%vals['props'][idx]
        except ValueError:
            table += '<td>%s</td>'%vals['props'][idx]
        try:
            if vals['percs']:
                table += '<td>%s %%</td>'%vals['percs'][idx]
        except ValueError:
            table += '<td>%s %%</td>'%vals['percs'][idx]
        table += '</tr>\n'
    table += '</table>\n'
    return table

def tableFrequencies(List):
    table = '<table class="table table-striped">\n'
    table += '\t<tr><th>Value</th><th>Frequency</th></tr>\n'
    for var in List:
        values = var[0]
        freqs  = var[1]
        table += '<table class="table table-striped">\n'
        table += '\t<tr><th>Value</th><th>Frequency</th></tr>\n'
        for idx, row in enumerate(values):
            table += '\t<tr><td>%s</td><td>%s</td></tr>\n'%(str(row),str(freqs[idx]))
        table += '</table>\n'
    return table
        
def tableProportions(List):
    """
    Passes two arrays in a list:
    array 1 = value
    array 2 = corresponding proportions
    """
    table = ''
    for turn in List:
        vals = turn[0]
        props = turn[1]
        table += '<table class="table table-striped">\n'
        table += '\t<tr><th>Value</th><th>Proportion</th></tr>\n'
        for idx, val in enumerate(vals):
            table += '\t<tr><td>%s</td><td>%s</td></tr>\n'%(str(val),str(props[idx]))
        table += '</table>\n'
    return table

def tableMode(List):
    """
    Produces a table to display modes.
    Passed are two arrays:
    1 = frequency
    2 = modal values
    """
    table = '<h3>Mode</h3>\n<table class="table table-striped">\n'
    table += '\t<tr><th>Frequency</th><th>Modal values</th></tr>\n'
    for turn in List:
        freq = turn[0]
        vals = turn[1]
        table += '\t<tr><td>%s</td><td>%s<br />'%(str(freq), str(vals[0]))
        for idx in range(1, len(vals)):
            table += '\t%s<br />\n'%(str(vals[idx]))
        table += '</td></tr>\n\t<tr><td></td><td></td></tr>\n'
    table += '</table>\n'
    return table


if __name__ == '__main__':
    a1 = ['Variable 1','Var001']
    a2 = ['Variable 2','Var002']
    a3 = ['df',99]
    a4 = ['t',30.0001]
    a5 = ['p',0.003]
    a = [a1,a2,a3,a4,a5]
    print table(a)


