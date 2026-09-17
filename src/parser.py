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
        self.failed_cards: list[dict] = []

        self.max_questions = min(
            max_questions,
            self.MAX_QUESTIONS
        )

    def parse(
        self,
        html: str
    ) -> list[Question]:

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
            f"[DEBUG] Found {len(cards)} DOM term cards."
        )

        questions = []
        seen = set()

        for index, card in enumerate(cards, start=1):

            if len(questions) >= self.max_questions:
                break

            question, reason = self._parse_card(card)

            if question is None:
                failure = self._build_failed_card(
                    index, card, reason
                )
                self.failed_cards.append(failure)

                print(f"[FAILED] CARD #{index}: {reason}")
                if failure["question"]:
                    print(f"[FAILED] Question: {failure['question']}")
                self._debug_card(index, card)
                continue

            key = self._normalize_key(question.question)
            if key in seen:
                continue

            seen.add(key)
            questions.append(question)

        if self.failed_cards:
            print(
                f"[WARNING] Failed {len(self.failed_cards)} card(s)."
            )

        return questions

    # ==================================================
    # CARD PARSER
    # ==================================================

    def _parse_card(
        self,
        card
    ) -> tuple[Question | None, str]:

        term_texts = card.select(".TermText")
        texts = []

        for element in term_texts:
            text = html_lib.unescape(
                element.get_text("\n", strip=True)
            ).strip()

            if text and text not in texts:
                texts.append(text)

        if len(texts) < 2:
            return None, "Not enough term data."

        # Find the question side first. Do NOT use it as the answer
        # source because its A/B/C/D labels are merely the choices.
        question_text = None
        for text in texts:
            choices = self._extract_choices(text)
            if len(choices) >= 2:
                question_text = text
                break

        if question_text is None:
            return None, "No multiple-choice question detected."

        choices = self._extract_choices(question_text)
        missing = [
            letter for letter in ("A", "B", "C", "D")
            if letter not in choices
        ]

        if missing:
            return None, "Missing choice(s): " + ", ".join(missing)

        # Only inspect term texts OTHER than the question for the correct
        # answer. This prevents a question beginning with "A." from being
        # incorrectly interpreted as answer A.
        answer = None
        for text in texts:
            if text == question_text:
                continue
            answer = self._extract_answer(text, choices)
            if answer:
                break

        if answer is None:
            return None, "No correct answer (A/B/C/D) was detected."

        question = self._build_question(
            question_text,
            answer
        )

        if question is None:
            return None, "Invalid question format."

        return question, "OK"

    # ==================================================
    # ANSWER
    # ==================================================

    def _extract_answer(
        self,
        text: str,
        choices: dict[str, str] | None = None
    ) -> str | None:

        text = re.sub(
            r"\s+",
            " ",
            html_lib.unescape(text)
        ).strip()

        if text.upper() in {"A", "B", "C", "D"}:
            return text.upper()

        # Answer: D / Đáp án: D / Correct answer: D
        match = re.match(
            r"^(?:answer|correct answer|đáp án)\s*[:\-]?\s*([A-D])\b",
            text,
            re.IGNORECASE
        )
        if match:
            return match.group(1).upper()

        # D. answer / D) answer / D: answer
        match = re.match(
            r"^\s*([A-D])\s*[\.\):]\s*(.*)$",
            text,
            re.IGNORECASE
        )
        if match:
            letter = match.group(1).upper()
            value = match.group(2).strip()
            if choices is None or not value:
                return letter
            if self._same_text(value, choices.get(letter, "")):
                return letter
            # A labelled answer can still be authoritative if it contains
            # the answer text; the label itself is the useful signal.
            return letter

        # Quizlet/JSON-LD may expose the correct answer as the full text.
        if choices:
            for letter, choice in choices.items():
                if self._same_text(text, choice):
                    return letter

        return None

    @staticmethod
    def _same_text(left: str, right: str) -> bool:
        normalize = lambda value: " ".join(
            html_lib.unescape(value).lower().split()
        )
        return normalize(left) == normalize(right)

    # ==================================================
    # MCQ DETECTION
    # ==================================================

    def _looks_like_mcq(
        self,
        text: str
    ) -> bool:
        return len(self._extract_choices(text)) >= 2

    # ==================================================
    # EXTRACT CHOICES
    # ==================================================

    def _extract_choices(
        self,
        text: str
    ) -> dict[str, str]:

        text = html_lib.unescape(text).strip()
        text = re.sub(r"\s+", " ", text).strip()

        choices = {}

        pattern = re.compile(
            r"(?:^|\s)([A-D])\s*[\.\):]\s*"
            r"(.*?)(?=\s+[A-D]\s*[\.\):]\s+|$)",
            re.IGNORECASE
        )

        for letter, value in pattern.findall(text):
            value = re.sub(r"\s+", " ", value).strip()
            if value:
                choices[letter.upper()] = value

        return choices

    # ==================================================
    # BUILD QUESTION
    # ==================================================

    def _build_question(
        self,
        text: str,
        answer: str
    ) -> Question | None:

        normalized_text = re.sub(
            r"\s+", " ", html_lib.unescape(text)
        ).strip()

        first_choice = re.search(
            r"\s+[A-D]\s*[\.\):]\s+",
            normalized_text,
            re.IGNORECASE
        )

        if first_choice is None:
            return None

        question_text = normalized_text[:first_choice.start()].strip()
        question_text = re.sub(
            r"^\s*\d+\s*[\.\)]\s*",
            "",
            question_text
        ).strip()

        if not question_text:
            return None

        choices = self._extract_choices(normalized_text)
        if set(choices) != {"A", "B", "C", "D"}:
            return None

        answer = answer.strip().upper()
        if answer not in {"A", "B", "C", "D"}:
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

    def _build_failed_card(
        self,
        index: int,
        card,
        reason: str
    ) -> dict:
        texts = []
        for element in card.select(".TermText"):
            text = html_lib.unescape(
                element.get_text(" ", strip=True)
            ).strip()
            if text and text not in texts:
                texts.append(text)

        question_preview = ""
        for text in texts:
            if len(self._extract_choices(text)) >= 2:
                question_preview = text
                break

        if not question_preview and texts:
            question_preview = texts[0]

        return {
            "index": index,
            "reason": reason,
            "question": question_preview
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

        if not isinstance(answer, str):
            return None

        choices = self._extract_choices(text)
        if set(choices) != {"A", "B", "C", "D"}:
            return None

        answer_letter = self._extract_answer(
            answer,
            choices
        )
        if answer_letter is None:
            return None

        return self._build_question(
            text,
            answer_letter
        )