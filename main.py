import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from src.crawler import QuizletCrawler
from src.formatter import QuestionFormatter
from src.google_docs import GoogleDocsExporter
from src.parser import QuizletParser


MAX_QUESTIONS = 500


class QuizletCrawlerGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Quizlet Crawler")
        self.root.geometry("760x620")
        self.root.minsize(700, 560)

        self.log_queue = queue.Queue()

        self.quizlet_url = tk.StringVar()
        self.docs_url = tk.StringVar()
        self.max_questions = tk.IntVar(value=500)
        self.output_file = tk.StringVar(
            value="output/questions.txt"
        )

        self._build_ui()

        self.root.after(
            100,
            self._process_logs
        )

    # ==================================================
    # UI
    # ==================================================

    def _build_ui(self):

        main = ttk.Frame(
            self.root,
            padding=20
        )

        main.pack(
            fill="both",
            expand=True
        )

        title = ttk.Label(
            main,
            text="Quizlet Crawler",
            font=(
                "Segoe UI",
                20,
                "bold"
            )
        )

        title.pack(
            pady=(0, 20)
        )

        # Quizlet URL
        ttk.Label(
            main,
            text="Quizlet URL:"
        ).pack(
            anchor="w"
        )

        quizlet_frame = ttk.Frame(main)

        quizlet_frame.pack(
            fill="x",
            pady=(5, 15)
        )

        quizlet_entry = ttk.Entry(
            quizlet_frame,
            textvariable=self.quizlet_url
        )

        quizlet_entry.pack(
            side="left",
            fill="x",
            expand=True
        )

        # Google Docs URL
        ttk.Label(
            main,
            text="Google Docs URL:"
        ).pack(
            anchor="w"
        )

        docs_frame = ttk.Frame(main)

        docs_frame.pack(
            fill="x",
            pady=(5, 15)
        )

        docs_entry = ttk.Entry(
            docs_frame,
            textvariable=self.docs_url
        )

        docs_entry.pack(
            side="left",
            fill="x",
            expand=True
        )

        # Options
        options = ttk.Frame(main)

        options.pack(
            fill="x",
            pady=(0, 15)
        )

        ttk.Label(
            options,
            text="Max Questions:"
        ).pack(
            side="left"
        )

        max_entry = ttk.Spinbox(
            options,
            from_=1,
            to=500,
            textvariable=self.max_questions,
            width=8
        )

        max_entry.pack(
            side="left",
            padx=(10, 20)
        )

        ttk.Label(
            options,
            text="Output:"
        ).pack(
            side="left"
        )

        output_entry = ttk.Entry(
            options,
            textvariable=self.output_file
        )

        output_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(10, 10)
        )

        ttk.Button(
            options,
            text="Browse",
            command=self._browse_output
        ).pack(
            side="right"
        )

        # Start button
        self.start_button = ttk.Button(
            main,
            text="Start Crawling",
            command=self._start
        )

        self.start_button.pack(
            pady=(0, 15)
        )

        # Progress
        self.progress = ttk.Progressbar(
            main,
            mode="indeterminate"
        )

        self.progress.pack(
            fill="x",
            pady=(0, 15)
        )

        # Log
        ttk.Label(
            main,
            text="Log:"
        ).pack(
            anchor="w"
        )

        self.log_text = scrolledtext.ScrolledText(
            main,
            height=20,
            font=(
                "Consolas",
                10
            ),
            state="disabled"
        )

        self.log_text.pack(
            fill="both",
            expand=True
        )

        self._log(
            "Ready."
        )

    # ==================================================
    # Browse
    # ==================================================

    def _browse_output(self):

        path = filedialog.asksaveasfilename(
            title="Save questions",
            defaultextension=".txt",
            filetypes=[
                (
                    "Text files",
                    "*.txt"
                ),
                (
                    "All files",
                    "*.*"
                )
            ]
        )

        if path:

            self.output_file.set(
                path
            )

    # ==================================================
    # Start
    # ==================================================

    def _start(self):

        quizlet_url = (
            self.quizlet_url
            .get()
            .strip()
        )

        docs_url = (
            self.docs_url
            .get()
            .strip()
        )

        try:

            max_questions = int(
                self.max_questions.get()
            )

        except (ValueError, tk.TclError):

            messagebox.showerror(
                "Invalid value",
                "Max Questions must be a number."
            )

            return

        if not quizlet_url:

            messagebox.showerror(
                "Missing URL",
                "Please enter the Quizlet URL."
            )

            return

        if not docs_url:

            messagebox.showerror(
                "Missing URL",
                "Please enter the Google Docs URL."
            )

            return

        if not 1 <= max_questions <= 500:

            messagebox.showerror(
                "Invalid value",
                "Max Questions must be between 1 and 500."
            )

            return

        self.start_button.config(
            state="disabled"
        )

        self.progress.start(
            10
        )

        self._log(
            "=" * 60
        )

        self._log(
            "Starting crawler..."
        )

        thread = threading.Thread(
            target=self._crawl,
            args=(
                quizlet_url,
                docs_url,
                max_questions
            ),
            daemon=True
        )

        thread.start()

    # ==================================================
    # Crawl
    # ==================================================

    def _crawl(
        self,
        quizlet_url,
        docs_url,
        max_questions
    ):

        try:

            self._log(
                f"[INFO] Quizlet URL: "
                f"{quizlet_url}"
            )

            self._log(
                f"[INFO] Max questions: "
                f"{max_questions}"
            )

            # ------------------------------------------
            # Crawl Quizlet
            # ------------------------------------------

            crawler = QuizletCrawler(
                timeout=30_000,
                headless=False,
                max_questions=max_questions
            )

            self._log(
                "[INFO] Starting Quizlet browser..."
            )

            html = crawler.fetch(
                quizlet_url
            )

            # ------------------------------------------
            # Parse
            # ------------------------------------------

            self._log(
                "[INFO] Parsing questions..."
            )

            parser = QuizletParser(
                max_questions=max_questions
            )

            questions = parser.parse(
                html
            )

            if not questions:

                raise RuntimeError(
                    "No questions found."
                )

            self._log(
                f"[SUCCESS] Found "
                f"{len(questions)} questions."
            )

            # ------------------------------------------
            # Failed cards
            # ------------------------------------------

            failed_cards = parser.failed_cards

            if failed_cards:

                self._log(
                    f"[FAILED] {len(failed_cards)} card(s) "
                    f"could not be converted."
                )

                self._log(
                    "[FAILED] Please fix these Quizlet cards "
                    "manually and run the crawler again:"
                )

                for failed in failed_cards:

                    question_preview = (
                        failed.get("question", "").strip()
                    )

                    if question_preview:

                        self._log(
                            f"[FAILED] CARD #{failed['index']} | "
                            f"{failed['reason']} | "
                            f"{question_preview}"
                        )

                    else:

                        self._log(
                            f"[FAILED] CARD #{failed['index']} | "
                            f"{failed['reason']}"
                        )

            # ------------------------------------------
            # Format
            # ------------------------------------------

            formatter = QuestionFormatter()

            content_txt = formatter.format_txt(
                questions
            )

            content_html = formatter.format_html(
                questions
            )

            # ------------------------------------------
            # Save TXT
            # ------------------------------------------

            output_path = (
                self.output_file
                .get()
                .strip()
            )

            if not output_path:

                output_path = (
                    "output/questions.txt"
                )

            output_dir = os.path.dirname(
                output_path
            )

            if output_dir:

                os.makedirs(
                    output_dir,
                    exist_ok=True
                )

            with open(
                output_path,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    content_txt
                )

            self._log(
                f"[SUCCESS] Saved TXT: "
                f"{output_path}"
            )

            # ------------------------------------------
            # Google Docs
            # ------------------------------------------

            self._log(
                "[INFO] Exporting to Google Docs..."
            )

            exporter = GoogleDocsExporter(
                headless=False
            )

            exporter.export(
                docs_url=docs_url,
                content_html=content_html
            )

            self._log(
                "[SUCCESS] Exported to Google Docs."
            )

            self._log(
                "=" * 60
            )

            self._log(
                "[SUCCESS] Done."
            )

            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Success",
                    f"Completed successfully.\n\n"
                    f"Questions: {len(questions)}\n"
                    f"TXT: {output_path}"
                )
            )

        except Exception as error:

            self._log(
                f"[ERROR] {error}"
            )

            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Crawler Error",
                    str(error)
                )
            )

        finally:

            self.root.after(
                0,
                self._finish
            )

    # ==================================================
    # Finish
    # ==================================================

    def _finish(self):

        self.progress.stop()

        self.start_button.config(
            state="normal"
        )

    # ==================================================
    # Logging
    # ==================================================

    def _log(
        self,
        message
    ):

        self.log_queue.put(
            message
        )

    def _process_logs(self):

        try:

            while True:

                message = self.log_queue.get_nowait()

                self.log_text.config(
                    state="normal"
                )

                self.log_text.insert(
                    "end",
                    message + "\n"
                )

                self.log_text.see(
                    "end"
                )

                self.log_text.config(
                    state="disabled"
                )

        except queue.Empty:
            pass

        self.root.after(
            100,
            self._process_logs
        )


def main():

    root = tk.Tk()

    app = QuizletCrawlerGUI(
        root
    )

    root.mainloop()


if __name__ == "__main__":
    main()