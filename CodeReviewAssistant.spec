# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Code Review Assistant
Builds a single-file Windows executable with all resources bundled.
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os

block_cipher = None

# Collect all resource files
templates_dir = os.path.join('resources', 'templates')
languages_dir = os.path.join('resources', 'languages')

added_files = [
    (templates_dir, 'resources/templates'),
    (languages_dir, 'resources/languages'),
]

# Collect PySide6 data files
pyside6_data = collect_data_files('PySide6')

# Collect tiktoken data files (encoding data)
tiktoken_data = collect_data_files('tiktoken_ext')

# Hidden imports for PySide6 and other dependencies
hidden_imports = collect_submodules('PySide6')
hidden_imports.extend([
    # Markdown & Syntax highlighting
    'markdown',
    'markdown.extensions.fenced_code',
    'markdown.extensions.codehilite',
    'markdown.extensions.tables',
    'Pygments',
    'Pygments.lexers.dotnet',  # C#
    'Pygments.lexers.jvm',     # Java
    'Pygments.lexers.python',  # Python
    'Pygments.lexers.javascript',  # Vue.js
    'Pygments.formatters.html',
    # LLM APIs
    'openai',
    'anthropic',
    'tiktoken',
    'tiktoken_ext',
    'tiktoken_ext.openai_public',
    # Config
    'dotenv',
    'yaml',
])

a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=added_files + pyside6_data + tiktoken_data,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'matplotlib.tests',
        'numpy',
        'numpy.tests',
        'PIL',
        'scipy',
        'pandas',
        'IPython',
        'jupyter',
        'notebook',
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
    name='CodeReviewAssistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # UPX compression for smaller EXE
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Hide console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # TODO: Add icon file when available
)
