import os
import sys


def configure_playwright_browser_path():
    """Use the Chromium bundled by PyInstaller when running the EXE."""

    if getattr(sys, "frozen", False):
        bundle_root = getattr(
            sys,
            "_MEIPASS",
            os.path.dirname(sys.executable)
        )

        browser_path = os.path.join(
            bundle_root,
            "playwright",
            "driver",
            "package",
            ".local-browsers"
        )

        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browser_path