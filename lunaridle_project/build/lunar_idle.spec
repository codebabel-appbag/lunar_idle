# -*- mode: python ; coding: utf-8 -*-

import sys
import os

# Caminho base do projeto considerando que o spec está em lunaridle_project/build/
PROJECT_ROOT = os.path.abspath(os.path.join(SPECPATH, '..'))

# Configuração de ícones baseada no sistema operacional atual do build
icon_path = None
version_file_path = None

if sys.platform == 'win32':
    icon_path = os.path.join(PROJECT_ROOT, 'assets', 'windows', 'icon.ico')
    version_file_path = os.path.join(PROJECT_ROOT, 'build', 'version.txt')
elif sys.platform == 'darwin':
    icon_path = os.path.join(PROJECT_ROOT, 'assets', 'macos', 'icon.icns')

a = Analysis(
    [os.path.join(PROJECT_ROOT, 'source', 'code', 'python', 'main.py')],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='lunar_idle',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
    version=version_file_path if sys.platform == 'win32' else None,
)

if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='lunar_idle.app',
        icon=icon_path,
        bundle_identifier='com.minguantecossys.lunaride',
    )