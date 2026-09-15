import html
import time

import win32clipboard
import win32con
from playwright.sync_api import sync_playwright


class GoogleDocsExporter:

    def __init__(
        self,
        headless: bool = False
    ):
        self.headless = headless

    def export(
        self,
        docs_url: str,
        content_html: str
    ):

        self._copy_html_to_clipboard(
            content_html
        )

        with sync_playwright() as p:

            print(
                "[INFO] Starting Chromium "
                "for Google Docs..."
            )

            browser = p.chromium.launch(
                headless=self.headless
            )

            context = browser.new_context()

            page = context.new_page()

            print(
                "[INFO] Opening Google Docs..."
            )

            page.goto(
                docs_url,
                wait_until="domcontentloaded"
            )

            print(
                "[INFO] Waiting for Google Docs..."
            )

            page.wait_for_timeout(5000)

            print(
                "[INFO] Pasting questions..."
            )

            page.keyboard.press(
                "Control+A"
            )

            page.wait_for_timeout(500)

            page.keyboard.press(
                "Control+V"
            )

            page.wait_for_timeout(3000)

            print(
                "[SUCCESS] Questions pasted "
                "into Google Docs."
            )

            browser.close()

    def _copy_html_to_clipboard(
        self,
        html_content: str
    ):

        html_data = self._build_windows_html(
            html_content
        )

        win32clipboard.OpenClipboard()

        try:

            win32clipboard.EmptyClipboard()

            win32clipboard.SetClipboardData(
                win32clipboard.RegisterClipboardFormat(
                    "HTML Format"
                ),
                html_data.encode(
                    "utf-8"
                )
            )

            # Fallback plain text
            plain_text = self._html_to_text(
                html_content
            )

            win32clipboard.SetClipboardData(
                win32con.CF_UNICODETEXT,
                plain_text
            )

        finally:

            win32clipboard.CloseClipboard()

    def _build_windows_html(
        self,
        html_content: str
    ) -> str:

        prefix = (
            "Version:0.9\r\n"
            "StartHTML:{start_html:08d}\r\n"
            "EndHTML:{end_html:08d}\r\n"
            "StartFragment:{start_fragment:08d}\r\n"
            "EndFragment:{end_fragment:08d}\r\n"
        )

        html = (
            "<html>"
            "<body>"
            "<!--StartFragment-->"
            f"{html_content}"
            "<!--EndFragment-->"
            "</body>"
            "</html>"
        )

        placeholder = prefix.format(
            start_html=0,
            end_html=0,
            start_fragment=0,
            end_fragment=0
        )

        start_html = len(
            placeholder.encode("utf-8")
        )

        end_html = (
            start_html
            + len(
                html.encode("utf-8")
            )
        )

        fragment_start = (
            html.index(
                "<!--StartFragment-->"
            )
            + len(
                "<!--StartFragment-->"
            )
        )

        fragment_end = html.index(
            "<!--EndFragment-->"
        )

        start_fragment = (
            start_html
            + len(
                html[
                    :fragment_start
                ].encode("utf-8")
            )
        )

        end_fragment = (
            start_html
            + len(
                html[
                    :fragment_end
                ].encode("utf-8")
            )
        )

        header = prefix.format(
            start_html=start_html,
            end_html=end_html,
            start_fragment=start_fragment,
            end_fragment=end_fragment
        )

        return header + html

    def _html_to_text(
        self,
        html_content: str
    ) -> str:

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(
            html_content,
            "html.parser"
        )

        return soup.get_text(
            "\n",
            strip=True
        )