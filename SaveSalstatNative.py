"""
SaveSalstatNative

A module to save in a native XML format for Salstat
(c) 2013, Alan James Salmoni
"""

import numpy
import datetime, pickle
from BeautifulSoup import BeautifulStoneSoup


def MakeString(vector):
    # returns a string representation of a numpy vector
    return ','.join([str(scal) for scal in vector])

def MakeVector(string):
    return numpy.array([float(scal) for scal in string.split(',')])

def Label(key_value_pairs):
    num_labels = len(key_value_pairs)
    label_xml = ''
    for label in key_value_pairs:
        ln = '\t\t\t<label>\n\t\t\t\t<labelvalue>%s</labelvalue>\n\t\t\t\t<labeltext>%s</labeltext>\n\t\t\t</label>\n'%(label, key_value_pairs[label])
        label_xml = label_xml + ln
    return label_xml

def Data(data):
    data_str = pickle.dumps(data)
    ln = '\t\t\t<data>%s\n\t\t\t</data>\n'%(data_str)
    return ln

def Variable(name, ivdv, labels, missingvalues, align, measure, data):
    labels_xml = Label(labels)
    data_xml = Data(data)
    var_xml = '\t\t<variable>\n\t\t\t<name>%s</name>\n'%(name)
    var_xml = var_xml + '\t\t\t<ivdv>%s</ivdv>\n'%(ivdv)
    var_xml = var_xml + labels_xml
    var_xml = var_xml + '\t\t\t<missingvalues>%s</missingvalues>\n'%(missingvalues)
    var_xml = var_xml + '\t\t\t<align>%s</align>\n'%(align)
    var_xml = var_xml + '\t\t\t<measure>%s</measure>\n'%(measure)
    var_xml = var_xml + data_xml + '\t\t</variable>\n'
    return var_xml

def Variables(variables):
    vars_xml = '\t<variables>\n'
    for var in variables:
        var_xml = Variable(var.name, var.ivdv, var.labels, var.missingvalues, \
                var.align, var.measure, var.data)
        vars_xml = vars_xml + var_xml
    vars_xml = vars_xml + '\t</variables>\n'
    return vars_xml

def NativeDoc(version, fname, variables):
    now = datetime.date.today()
    date_str = now.strftime("%Y-%m-%d")
    # convert to human-readable format
    variables = Variables(variables)
    initial_xml = '<SalstatDoc>\n\t<version>%s</version>\n\t<filename>%s</filename>\
            \n\t<date_created>%s</date_created>\n'%(version, fname, date_str)
    ending_xml  = '%s</SalstatDoc>'%variables
    return initial_xml + ending_xml

class variableobj(object):
    def __init__(self, name):
        self.name = name

def SaveNativeDoc(grid, filename):
    # default suffix is .xml
    ColsUsed, colnums = grid.GetUsedCols()
    vars = []
    for col in colnums:
        var_name = grid.GetColLabelValue(col)
        var = variableobj(var_name)
        var.labels = {}
        var.data = grid.CleanData(col)
        var.ivdv = "Not set"
        var.missingvalues = "Not set"
        var.measure = "Not set"
        var.align = "Not set"
    n = NativeDoc("20131022", filename, vars)
    try:
        fout = open(filename, 'w')
        fout.write(n)
        fout.close()
    except:
        pass

def LoadNativeDoc(grid, filename):
    try:
        fin = open(filename, 'r')
        data = fin.read()
        fin.close()
        soup = BeautifulStoneSoup(data)
        vars = soup.findAll('variable')
        for idx, var in enumerate(vars):
            var_name = var('name')[0].text
            var_ivdv = var('ivdv')[0].text
            var_align = var('align')[0].text
            var_missingvalues = var('missingvalues')[0].text
            var_data = var('data')[0].text
            grid.SetColLabelValue(idx, var_name)
            vector = pickle.loads(var_data)
            for row in range(len(vector)):
                grid.SetCellValue(row, idx, vector[row])
            # cannot do any others just yet! 
            # Need to have meta data in the grid
    except: # specific exception?
        data = ""


if __name__ == '__main__':
    var1 = variableobj('Var001')
    var2 = variableobj('Var002')
    var3 = variableobj('Var003')
    var1.labels = {1: 'Label 1', 2: 'Label 2','a':'Label a'}
    var2.labels = {1: 'Label a', 2: 'Label b','a':'Label 123'}
    var3.labels = {1: 'Label 1', 2: 'Label 2','a':'Label 456'}
    #print Label(labels)
    var1.data = numpy.array(([2,3.4,4,3.565,7]))
    var2.data = numpy.array(([2,3.4,4,3.565,7]))
    var3.data = numpy.array(([2,3.4,4,3.565,7]))
    var1.ivdv = 'Not yet'
    var2.ivdv = 'IV'
    var3.ivdv = 'DV'
    var1.missingvalues = 'None yet'
    var2.missingvalues = '-99'
    var3.missingvalues = 'Missing'
    var1.align = 'left'
    var2.align = "CENTRE"
    var3.align = "Right"
    var1.measure = "Ordinal"
    var2.measure = "INTERVAL"
    var3.measure = "nominal"
    vars = [var1, var2, var3]
    """
    n = NativeDoc("20131022",'filename001',vars)
    fout = open('/Users/alansalmoni/sal.xml','w')
    fout.write(n)
    fout.close()
    """
    vec = numpy.random.rand(400)
    vecstr = MakeString(vec)
    strvec = MakeVector(vecstr)

