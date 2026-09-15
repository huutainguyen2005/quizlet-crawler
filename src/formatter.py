import html

from .models import Question


class QuestionFormatter:

    def format_txt(
        self,
        questions: list[Question]
    ) -> str:

        blocks = []

        for question in questions:

            lines = [
                question.question,
                f"A. {question.choices[0]}",
                f"B. {question.choices[1]}",
                f"C. {question.choices[2]}",
                f"D. {question.choices[3]}",
                f"Answer: {question.answer}",
            ]

            blocks.append(
                "\n".join(lines)
            )

        return (
            "\n\n".join(blocks)
            + "\n"
        )

    def format_html(
        self,
        questions: list[Question]
    ) -> str:

        blocks = []

        for question in questions:

            lines = []

            # Question
            lines.append(
                f"<p><b>"
                f"{self._escape(question.question)}"
                f"</b></p>"
            )

            # Choices
            for index, choice in enumerate(
                question.choices
            ):

                letter = chr(
                    ord("A") + index
                )

                choice_text = (
                    f"{letter}. "
                    f"{self._escape(choice)}"
                )

                # Correct answer -> red
                if letter == question.answer:

                    choice_text = (
                        '<span style="color:red;">'
                        f"{choice_text}"
                        "</span>"
                    )

                lines.append(
                    f"<p>{choice_text}</p>"
                )

            blocks.append(
                "\n".join(lines)
            )

        # One blank line between questions
        return (
            '<div style="font-family:Arial;">'
            + '<p>&nbsp;</p>'.join(blocks)
            + "</div>"
        )

    @staticmethod
    def _escape(
        text: str
    ) -> str:

        return html.escape(
            text
        )