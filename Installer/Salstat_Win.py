"""
Pyinstaller script

This takes source and builds a Windows package.
"""

import os

base = '..\\..\\'
ln = "pyinstaller -w --distpath=%sSalstat-Dist --workpath=%sSalstat-Build %sSalstat\\salstat.py"%(base, base ,base)
print
print ln
print
os.popen(ln)
