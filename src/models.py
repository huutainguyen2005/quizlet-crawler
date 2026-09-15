from dataclasses import dataclass


@dataclass
class Question:
    question: str
    choices: list[str]
    answer: str