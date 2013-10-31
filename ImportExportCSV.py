"""
ImportExportCSV
A module for importing and exporting CSV to and from Salstat
Includes dialogs for wxPython

(c) 2013, Alan James Salmoni

"""

import csv
import wx



def FinalImport(fin, delimiter, qualifier, header_line):
    if type(delimiter) is not list:
        delimiter = [delimiter]
    if type(qualifier) is not list:
        qualifier = [qualifier]
    fin.seek(0) # reset file pointer to start of file
    #for line in fin.readlines():

def ParseLine(line, delimiter, qualifier):
    if type(delimiter) is not list:
        delimiter = [delimiter]
    if type(qualifier) is not list:
        qualifier = [qualifier]
    withinflag = False
    words = []
    length = len(line)
    thisword = ''
    for idx in range(length):
        char = line[idx]
        if char in qualifier:
            if withinflag:
                withinflag = False
            else:
                withinflag = True
        if char in delimiter:
            if not withinflag:
                print "Not ",char
                words.append(thisword)
                thisword = ''
        else:
            thisword += char
    return words

if __name__ == '__main__':
    ln = 'this is a, line'
    delimiter = ','
    qualifier = '"'
    print ParseLine(ln, delimiter, qualifier)


