# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for TopEleven Bot (Windows + Mac shared spec)."""

import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[str(Path('.').resolve())],
    binaries=[],
    datas=[
        ('Assets',      'Assets'),
        ('config.json', '.'),
        ('Modules',     'Modules'),
    ],
    hiddenimports=[
        'customtkinter',
        'PIL._tkinter_finder',
        'pyscreeze',
        'pyautogui',
        'keyboard',
        'sqlite3',
        'queue',
        'threading',
        'app.ui.main_window',
        'app.ui.components.sidebar',
        'app.ui.components.dashboard',
        'app.ui.components.farming_panel',
        'app.ui.components.settings_panel',
        'app.ui.components.overlay',
        'app.ui.components.debug_panel',
        'app.bot.controller',
        'app.bot.actions.farm_greens',
        'app.bot.actions.farm_rest',
        'app.bot.actions.claim_daily',
        'app.bot.detection.composite_detector',
        'app.bot.detection.template_detector',
        'app.bot.detection.yolo_detector',
        'app.bot.platform.windows_adapter',
        'app.bot.platform.mac_adapter',
        'app.data.session_store',
        'app.data.debug_store',
    ],
    excludes=[
        'torch', 'torchvision', 'torchaudio',
        'ultralytics', 'supervision',
        'matplotlib', 'scipy', 'pandas', 'numpy',
        'IPython', 'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TopElevenBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Assets/icon.ico' if sys.platform == 'win32' else 'Assets/icon.icns',
)

# macOS: also build an .app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='TopElevenBot.app',
        icon='Assets/icon.icns',
        bundle_identifier='com.topeleven.bot',
        info_plist={
            'NSHighResolutionCapable': True,
            'LSUIElement': False,
        },
    )
