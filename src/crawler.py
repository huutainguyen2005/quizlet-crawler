from playwright.sync_api import sync_playwright


class QuizletCrawler:

    MAX_QUESTIONS = 500

    def __init__(
        self,
        timeout: int = 30_000,
        headless: bool = False,
        max_questions: int = MAX_QUESTIONS
    ):
        self.timeout = timeout
        self.headless = headless

        self.max_questions = min(
            max_questions,
            self.MAX_QUESTIONS
        )

    def fetch(self, url: str) -> str:

        with sync_playwright() as p:

            print("[INFO] Starting Chromium...")

            browser = p.chromium.launch(
                headless=self.headless
            )

            context = browser.new_context(
                viewport={
                    "width": 1366,
                    "height": 768
                },
                locale="en-US"
            )

            page = context.new_page()

            page.set_default_timeout(
                self.timeout
            )

            print("[INFO] Opening Quizlet...")

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.timeout
            )

            self._handle_cookie(page)

            print(
                f"[INFO] Page title: {page.title()}"
            )

            print(
                "[INFO] Waiting for JavaScript..."
            )

            page.wait_for_timeout(5000)

            self._load_all_content(page)

            html = page.content()

            print(
                f"[INFO] HTML size: "
                f"{len(html):,} bytes"
            )

            with open(
                "debug_quizlet.html",
                "w",
                encoding="utf-8"
            ) as file:

                file.write(html)

            print(
                "[DEBUG] Saved rendered HTML "
                "to debug_quizlet.html"
            )

            browser.close()

            return html

    def _handle_cookie(self, page):

        print(
            "[INFO] Handling cookie consent..."
        )

        try:

            page.get_by_role(
                "button",
                name="Reject All"
            ).click(
                timeout=3000
            )

            print(
                "[INFO] Cookie: Reject All"
            )

            return

        except Exception:
            pass

        try:

            page.get_by_role(
                "button",
                name="Accept All"
            ).click(
                timeout=3000
            )

            print(
                "[INFO] Cookie: Accept All"
            )

            return

        except Exception:
            pass

        print(
            "[INFO] Cookie popup not found."
        )

    def _load_all_content(self, page):

        print(
            "[INFO] Loading quiz content..."
        )

        last_height = 0
        stable_rounds = 0

        for i in range(100):

            current_height = page.evaluate(
                """
                () => document.documentElement.scrollHeight
                """
            )

            print(
                f"[DEBUG] Scroll {i + 1}: "
                f"height={current_height}"
            )

            if current_height == last_height:

                stable_rounds += 1

            else:

                stable_rounds = 0

            last_height = current_height

            if stable_rounds >= 5:

                print(
                    "[INFO] Page height stopped "
                    "changing."
                )

                break

            page.evaluate(
                """
                () => {
                    window.scrollTo(
                        0,
                        document.documentElement.scrollHeight
                    );
                }
                """
            )

            page.wait_for_timeout(1000)

        # Go back to the top.
        page.evaluate(
            """
            () => {
                window.scrollTo(0, 0);
            }
            """
        )

        page.wait_for_timeout(1000)

        print(
            "[INFO] Finished loading page content."
        )