# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File for Certify Intel Backend

This specification file defines how PyInstaller should bundle the
Certify Intel backend into a standalone executable.

Build commands:
    Windows: pyinstaller certify_backend.spec --clean --noconfirm
    macOS:   pyinstaller certify_backend.spec --clean --noconfirm

Output:
    dist/certify_backend.exe (Windows)
    dist/certify_backend (macOS/Linux)
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect data files from packages that need them
datas = [
    # Include the database file (will be copied, user should have their own)
    ('certify_intel.db', '.'),
    # Include .env.example as template
    ('.env.example', '.'),
]

# Check if templates directory exists
if os.path.exists('templates'):
    datas.append(('templates', 'templates'))

# Hidden imports - packages that PyInstaller can't detect automatically
hiddenimports = [
    # Uvicorn and ASGI
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.loops.asyncio',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.http.httptools_impl',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.protocols.websockets.websockets_impl',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.lifespan.off',

    # FastAPI and Starlette
    'fastapi',
    'starlette',
    'starlette.responses',
    'starlette.routing',
    'starlette.middleware',
    'starlette.middleware.cors',

    # SQLAlchemy
    'sqlalchemy',
    'sqlalchemy.sql.default_comparator',
    'sqlalchemy.ext.declarative',
    'sqlalchemy.orm',
    'sqlalchemy.engine',
    'sqlalchemy.dialects.sqlite',

    # Authentication
    'passlib',
    'passlib.handlers',
    'passlib.handlers.bcrypt',
    'jose',
    'jose.jwt',

    # AI/ML Libraries
    'openai',
    'tiktoken',
    'tiktoken_ext',
    'tiktoken_ext.openai_public',
    'langchain',

    # Data processing
    'pandas',
    'numpy',
    'openpyxl',
    'reportlab',

    # Web scraping
    'playwright',
    'bs4',
    'lxml',
    'html5lib',

    # HTTP clients
    'httpx',
    'requests',

    # Scheduling
    'apscheduler',
    'apscheduler.schedulers',
    'apscheduler.schedulers.background',

    # Utilities
    'dotenv',
    'tenacity',
    'jinja2',

    # Finance
    'yfinance',

    # Pydantic
    'pydantic',
    'pydantic_core',

    # Email (for alerts)
    'email',
    'email.mime',
    'email.mime.text',
    'email.mime.multipart',
    'smtplib',

    # PIL/Pillow (needed by some dependencies)
    'PIL',
    'PIL._imaging',
    'PIL.Image',

    # Our custom modules
    'database',
    'analytics',
    'extended_features',
    'discovery_agent',
    'scheduler',
    'alerts',
    'reports',
    'extractor',
    'scraper',
    'glassdoor_scraper',
    'indeed_scraper',
    'sec_edgar_scraper',
    'uspto_scraper',
    'klas_scraper',
    'appstore_scraper',
    'himss_scraper',
]

# Collect all submodules for complex packages
hiddenimports += collect_submodules('uvicorn')
hiddenimports += collect_submodules('fastapi')
hiddenimports += collect_submodules('starlette')
hiddenimports += collect_submodules('sqlalchemy')
hiddenimports += collect_submodules('pydantic')

# Analysis
a = Analysis(
    ['__main__.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary packages to reduce size
        'tkinter',
        'matplotlib',
        'scipy',
        'cv2',
        'torch',
        'tensorflow',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Create the PYZ archive
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='certify_backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Use UPX compression if available
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Show console window (useful for debugging)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../desktop-app/resources/icons/icon.ico' if sys.platform == 'win32' else None,
)

# For macOS, you might want to create an app bundle
# Uncomment below if needed:
# app = BUNDLE(
#     exe,
#     name='Certify Intel Backend.app',
#     icon='../desktop-app/resources/icons/icon.icns',
#     bundle_identifier='com.certifyhealth.intel.backend',
# )
