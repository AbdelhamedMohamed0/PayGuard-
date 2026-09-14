# -*- mode: python ; coding: utf-8 -*-

import os
import sys

base_dir = os.path.abspath(os.path.dirname(SPEC)) if 'SPEC' in locals() else os.path.abspath('.')
win_icon = os.path.join(base_dir, 'assets', 'icons', 'icon.ico')
mac_icon = os.path.join(base_dir, 'assets', 'icons', 'icon.icns')

datas = [('templates', 'templates')]
assets_dir = os.path.join(base_dir, 'assets')
if os.path.exists(assets_dir):
    datas.append(('assets', 'assets'))

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['jinja2', 'openpyxl'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

try:
    print(f"[ICON DEBUG] Resolved Windows icon path: {win_icon}".encode('ascii', errors='backslashreplace').decode('ascii'))
    print(f"[ICON DEBUG] Path exists: {os.path.exists(win_icon)}")
except Exception:
    pass

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PayGuard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True if sys.platform == 'win32' else False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=win_icon if os.path.exists(win_icon) else 'assets/icons/icon.ico',
)

if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='PayGuard.app',
        icon=mac_icon if os.path.exists(mac_icon) else 'assets/icons/icon.icns',
        bundle_identifier='com.payguard.payroll',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'CFBundleShortVersionString': '2.0.0',
            'CFBundleVersion': '2.0.0',
            'NSRequiresAquaSystemAppearance': 'False'
        }
    )

