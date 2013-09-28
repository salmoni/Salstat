# -*- mode: python -*-
a = Analysis(['../../Salstat/salstat.py'],
             pathex=['/Users/alansalmoni/Projects/Salstat/Installer'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='salstat',
          debug=False,
          strip=None,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='salstat')
app = BUNDLE(coll,
             name='salstat.app',
             icon=None)
