# -*- mode: python ; coding: utf-8 -*-
# Fichier de build PyInstaller. Usage : uv run pyinstaller MusicPlayer.spec
#
# VLC reste une dépendance externe (non embarquée) : l'utilisateur doit avoir
# VLC installé sur sa machine. Les données internes de CustomTkinter sont
# collectées automatiquement par le hook fourni par pyinstaller-hooks-contrib.

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MusicPlayer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon/zkz_icon.ico',
)
