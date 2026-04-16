# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['c:\\Users\\Joshu\\OneDrive\\Desktop\\game stuff\\GameOptimizer\\app.py'],
    pathex=[],
    binaries=[],
    datas=[('c:\\Users\\Joshu\\OneDrive\\Desktop\\game stuff\\GameOptimizer\\step1_process_manager.py', '.'), ('c:\\Users\\Joshu\\OneDrive\\Desktop\\game stuff\\GameOptimizer\\step2_server.py', '.'), ('c:\\Users\\Joshu\\OneDrive\\Desktop\\game stuff\\GameOptimizer\\step4_optimizations.py', '.'), ('c:\\Users\\Joshu\\OneDrive\\Desktop\\game stuff\\GameOptimizer\\step5_hardware_setup.py', '.'), ('c:\\Users\\Joshu\\OneDrive\\Desktop\\game stuff\\GameOptimizer\\frontend', 'frontend')],
    hiddenimports=['psutil', 'flask', 'flask_cors', 'webview'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='GameOptimizer',
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
)
