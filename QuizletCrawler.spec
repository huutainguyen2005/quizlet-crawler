# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import playwright

from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

project_root = Path(SPEC).resolve().parent
playwright_root = Path(playwright.__file__).resolve().parent
browser_root = playwright_root / "driver" / "package" / ".local-browsers"

if not browser_root.exists():
    raise SystemExit(
        "Playwright Chromium was not installed locally. "
        "Run build.bat or set PLAYWRIGHT_BROWSERS_PATH=0 and "
        "run 'python -m playwright install chromium' first."
    )

browser_datas = [
    (
        str(browser_root),
        "playwright/driver/package/.local-browsers"
    )
]

analysis = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=browser_datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(analysis.pure)

exe = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="QuizletCrawler",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=str(project_root / "icon.ico"),
)

coll = COLLECT(
    exe,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=True,
    name="QuizletCrawler",
)