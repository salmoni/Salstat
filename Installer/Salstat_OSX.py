"""
Pyinstaller script

This takes source and builds an OS X package.
"""

import os

base = '../../'
ln = "pyinstaller -w --distpath=%sSalstat-Dist/ --workpath=%sSalstat-Build %sSalstat/salstat.py"%(base, base ,base)

os.popen(ln)

