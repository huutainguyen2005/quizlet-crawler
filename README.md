# Quizlet Crawler

Simple Python CLI tool for extracting publicly available Quizlet
question data and exporting it into A/B/C/D format.

## Requirements

- Python 3.10+
- Internet connection

## Installation

```bash
pip install -r requirements.txt
```

```bash
python -m playwright install chromium
```
## Build .exe

```bash
pyinstaller --noconfirm --clean --onedir --windowed --name QuizletCrawler --icon=icon.ico main.py
```