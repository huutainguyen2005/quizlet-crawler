import html as html_lib
import json
import re

from bs4 import BeautifulSoup

from .models import Question


class QuizletParser:

    MAX_QUESTIONS = 500

    def __init__(
        self,
        max_questions: int = MAX_QUESTIONS
    ):
        self.max_questions = min(
            max_questions,
            self.MAX_QUESTIONS
        )

        # Cards that were found but could not be converted into
        # a valid A/B/C/D question are kept here so the user can
        # manually fix the source data.
        self.failed_cards: list[dict[str, str | int]] = []

    def parse(
        self,
        html: str
    ) -> list[Question]:

        self.failed_cards = []

        print(
            "[INFO] Trying DOM parser..."
        )

        questions = self._parse_dom(
            html
        )

        if questions:

            print(
                f"[INFO] Found "
                f"{len(questions)} questions "
                f"from DOM."
            )

            return questions[
                :self.max_questions
            ]

        print(
            "[INFO] DOM parser found nothing."
        )

        print(
            "[INFO] Trying JSON-LD parser..."
        )

        questions = self._parse_json_ld(
            html
        )

        if questions:

            print(
                f"[INFO] Found "
                f"{len(questions)} questions "
                f"from JSON-LD."
            )

        return questions[
            :self.max_questions
        ]

    # ==================================================
    # DOM PARSER
    # ==================================================

    def _parse_dom(
        self,
        html: str
    ) -> list[Question]:

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        cards = soup.select(
            'div[aria-label="Term"]'
        )

        print(
            f"[DEBUG] Found "
            f"{len(cards)} DOM term cards."
        )

        questions = []
        seen = set()
        rejected = 0

        for index, card in enumerate(
            cards,
            start=1
        ):

            if len(questions) >= self.max_questions:
                break

            question, reason = self._parse_card(
                card
            )

            if question is None:

                rejected += 1

                failure = self._build_failed_card(
                    index,
                    card,
                    reason
                )

                self.failed_cards.append(
                    failure
                )

                print(
                    f"[FAILED] CARD #{index}: "
                    f"{reason}"
                )

                if failure["question"]:
                    print(
                        f"[FAILED] Question: "
                        f"{failure['question']}"
                    )

                self._debug_card(
                    index,
                    card
                )

                continue

            key = self._normalize_key(
                question.question
            )

            if key in seen:
                continue

            seen.add(key)

            questions.append(
                question
            )

        if rejected:

            print(
                f"[WARNING] Rejected "
                f"{rejected} cards."
            )

        return questions

    # ==================================================
    # CARD PARSER
    # ==================================================

    def _parse_card(
        self,
        card
    ) -> tuple[Question | None, str]:

        term_texts = card.select(
            ".TermText"
        )

        texts = []

        for element in term_texts:

            text = element.get_text(
                "\n",
                strip=True
            )

            text = html_lib.unescape(
                text
            ).strip()

            if not text:
                continue

            if text not in texts:

                texts.append(
                    text
                )

        if len(texts) < 2:
            return None, "Not enough term data."

        question_text = None
        answer = None

        # ----------------------------------------------
        # Find question containing A/B/C/D
        # ----------------------------------------------

        for text in texts:

            if self._looks_like_mcq(
                text
            ):

                question_text = text
                break

        if question_text is None:
            return None, "No question with four choices A/B/C/D was detected."

        # ----------------------------------------------
        # Find correct answer
        # ----------------------------------------------

        for text in texts:

            answer = self._extract_answer(
                text
            )

            if answer:
                break

        if answer is None:
            return None, "No correct answer (A/B/C/D) was detected."

        question = self._build_question(
            question_text,
            answer
        )

        if question is None:
            choices = self._extract_choices(
                question_text
            )

            if len(choices) != 4:
                missing = [
                    letter
                    for letter in ("A", "B", "C", "D")
                    if letter not in choices
                ]

                if missing:
                    return None, (
                        "Missing choice(s): "
                        + ", ".join(missing)
                    )

                return None, (
                    f"Expected 4 choices, found {len(choices)}."
                )

            return None, "Invalid question format."

        return question, "OK"

    # ==================================================
    # ANSWER
    # ==================================================

    def _extract_answer(
        self,
        text: str
    ) -> str | None:

        text = text.strip()

        # -----------------------------
        # A / B / C / D
        # -----------------------------

        if text.upper() in {
            "A",
            "B",
            "C",
            "D"
        }:

            return text.upper()

        # -----------------------------
        # A. answer
        # A) answer
        # A: answer
        # -----------------------------

        match = re.match(
            r"^\s*([A-D])\s*[\.\):]\s*",
            text,
            re.IGNORECASE
        )

        if match:

            return match.group(
                1
            ).upper()

        return None

    # ==================================================
    # MCQ DETECTION
    # ==================================================

    def _looks_like_mcq(
        self,
        text: str
    ) -> bool:

        choices = self._extract_choices(
            text
        )

        # Treat a card as an MCQ candidate when at least two
        # labelled choices are present. This is intentional:
        # malformed cards (for example A/B/C with missing D)
        # must be reported as FAILED instead of silently ignored.
        return len(choices) >= 2

    # ==================================================
    # EXTRACT CHOICES
    # ==================================================

    def _extract_choices(
        self,
        text: str
    ) -> dict[str, str]:

        text = html_lib.unescape(
            text
        ).strip()

        choices = {}

        # ------------------------------------------------
        # Normalize all whitespace
        # ------------------------------------------------

        text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()

        # ------------------------------------------------
        # Important:
        #
        # Supports:
        #
        # Question?
        # A. answer
        # B. answer
        #
        # AND
        #
        # Question? A. answer B. answer C. answer D. answer
        # ------------------------------------------------

        pattern = re.compile(
            r"(?:^|\s)"
            r"([A-D])"
            r"\s*[\.\):]\s*"
            r"(.*?)"
            r"(?=\s+[A-D]\s*[\.\):]\s+|$)",
            re.IGNORECASE
        )

        matches = pattern.findall(
            text
        )

        for letter, value in matches:

            letter = letter.upper()

            value = re.sub(
                r"\s+",
                " ",
                value
            ).strip()

            if value:

                choices[letter] = value

        return choices

    # ==================================================
    # BUILD QUESTION
    # ==================================================

    def _build_question(
        self,
        text: str,
        answer: str
    ) -> Question | None:

        text = html_lib.unescape(
            text
        ).strip()

        # Normalize whitespace
        normalized_text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()

        # ------------------------------------------------
        # Find first choice
        # ------------------------------------------------

        first_choice = re.search(
            r"\s+[A-D]\s*[\.\):]\s+",
            normalized_text,
            re.IGNORECASE
        )

        if first_choice is None:
            return None

        question_text = normalized_text[
            :first_choice.start()
        ].strip()

        # ------------------------------------------------
        # Remove question number
        #
        # 10. What is ...
        # ↓
        # What is ...
        # ------------------------------------------------

        question_text = re.sub(
            r"^\s*\d+\s*[\.\)]\s*",
            "",
            question_text
        ).strip()

        if not question_text:
            return None

        choices = self._extract_choices(
            normalized_text
        )

        if len(choices) != 4:
            return None

        answer = answer.strip().upper()

        if answer not in {
            "A",
            "B",
            "C",
            "D"
        }:

            return None

        return Question(
            question=question_text,
            choices=[
                choices["A"],
                choices["B"],
                choices["C"],
                choices["D"]
            ],
            answer=answer
        )

    # ==================================================
    # FAILED CARD
    # ==================================================

    def _build_failed_card(
        self,
        index: int,
        card,
        reason: str
    ) -> dict[str, str | int]:

        term_texts = card.select(
            ".TermText"
        )

        texts = []

        for element in term_texts:

            text = element.get_text(
                " ",
                strip=True
            )

            text = html_lib.unescape(
                text
            ).strip()

            if text and text not in texts:
                texts.append(text)

        # Try to extract the question even when the card is malformed.
        question_text = ""

        for text in texts:
            first_choice = re.search(
                r"\s+[A-D]\s*[\.\):]\s+",
                re.sub(r"\s+", " ", text),
                re.IGNORECASE
            )

            if first_choice:
                question_text = re.sub(
                    r"^\s*\d+\s*[\.\)]\s*",
                    "",
                    re.sub(r"\s+", " ", text[:first_choice.start()]).strip()
                )
                break

        return {
            "index": index,
            "question": question_text,
            "reason": reason
        }

    # ==================================================
    # DEBUG
    # ==================================================

    def _debug_card(
        self,
        index: int,
        card
    ):

        term_texts = card.select(
            ".TermText"
        )

        for text_index, element in enumerate(
            term_texts,
            start=1
        ):

            text = element.get_text(
                "\n",
                strip=True
            )

            print(
                f"[DEBUG] CARD #{index} "
                f"TermText {text_index}:"
            )

            print(
                repr(text)
            )

    # ==================================================
    # NORMALIZE
    # ==================================================

    @staticmethod
    def _normalize_key(
        text: str
    ) -> str:

        return " ".join(
            text.lower().split()
        )

    # ==================================================
    # JSON-LD FALLBACK
    # ==================================================

    def _parse_json_ld(
        self,
        html: str
    ) -> list[Question]:

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        questions = []
        seen = set()

        scripts = soup.find_all(
            "script",
            {
                "type": "application/ld+json"
            }
        )

        print(
            f"[DEBUG] Found "
            f"{len(scripts)} JSON-LD scripts."
        )

        for script in scripts:

            raw = script.string

            if not raw:
                continue

            try:

                data = json.loads(raw)

            except json.JSONDecodeError:

                continue

            quizzes = self._find_quizzes(
                data
            )

            for quiz in quizzes:

                parts = quiz.get(
                    "hasPart",
                    []
                )

                if not isinstance(
                    parts,
                    list
                ):
                    continue

                for item in parts:

                    if len(questions) >= self.max_questions:
                        return questions

                    if not isinstance(
                        item,
                        dict
                    ):
                        continue

                    if item.get(
                        "@type"
                    ) != "Question":
                        continue

                    question = self._parse_json_question(
                        item
                    )

                    if question is None:
                        continue

                    key = self._normalize_key(
                        question.question
                    )

                    if key in seen:
                        continue

                    seen.add(key)

                    questions.append(
                        question
                    )

        return questions

    def _find_quizzes(
        self,
        data
    ) -> list[dict]:

        quizzes = []

        if isinstance(
            data,
            dict
        ):

            if data.get(
                "@type"
            ) == "Quiz":

                quizzes.append(
                    data
                )

            for value in data.values():

                quizzes.extend(
                    self._find_quizzes(
                        value
                    )
                )

        elif isinstance(
            data,
            list
        ):

            for item in data:

                quizzes.extend(
                    self._find_quizzes(
                        item
                    )
                )

        return quizzes

    def _parse_json_question(
        self,
        data: dict
    ) -> Question | None:

        text = data.get(
            "text"
        )

        accepted_answer = data.get(
            "acceptedAnswer"
        )

        if not isinstance(
            text,
            str
        ):
            return None

        if not isinstance(
            accepted_answer,
            dict
        ):
            return None

        answer = accepted_answer.get(
            "text"
        )

        if not isinstance(
            answer,
            str
        ):
            return None

        return self._build_question(
            text,
            answer
        )