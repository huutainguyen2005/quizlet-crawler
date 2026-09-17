# Quizlet Crawler

Simple Python GUI tool for extracting publicly available Quizlet multiple-choice question data and exporting it into A/B/C/D format.

## Requirements

- Windows
- Python 3.14+
- Internet connection

## Installation

### 1. Clone the repository

```cmd
git clone <repository-url>
cd quizlet-crawler
```

### 2. Create a virtual environment

```cmd
py -3.14 -m venv .venv
```

### 3. Activate the virtual environment

**Windows CMD:**

```cmd
.venv\Scripts\activate
```

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```cmd
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Install Playwright Chromium

For running the Python source:

```cmd
python -m playwright install chromium
```

### 6. Run

```cmd
python main.py
```

## Build a Standalone `.exe`

The project includes `QuizletCrawler.spec` and `build.bat` so Chromium is bundled into the PyInstaller application.

From **Windows CMD**:

```cmd
build.bat
```

The executable will be created at:

```text
dist\QuizletCrawler\QuizletCrawler.exe
```

The build process automatically:

1. Activates `.venv`.
2. Installs Python dependencies from `requirements.txt`.
3. Sets `PLAYWRIGHT_BROWSERS_PATH=0`.
4. Installs Chromium into the Playwright package directory.
5. Bundles that Chromium into the PyInstaller build.
6. Configures the EXE to use its bundled Chromium.

Therefore, a user who receives `dist\QuizletCrawler\` can run the EXE without installing Python or Playwright separately.

## Invalid Questions

The crawler validates every multiple-choice card.

A valid question must contain all four choices:

```text
A. ...
B. ...
C. ...
D. ...
```

If a Quizlet card has a typo, for example A/B/C but no D, it is **not silently discarded**. The application reports it as `[FAILED]` and shows the card number and question so it can be fixed manually.

Example:

```text
[FAILED] CARD #12: Missing choice(s): D
[FAILED] Question: Quan điểm nào cho rằng: ...
```

Only valid questions are exported.

## Google Docs Export

The correct answer is determined separately from the question choices. The question text itself is never treated as the correct-answer source.

The Google Docs export marks the detected correct choice in red.

If a card has no identifiable correct answer, it is reported as `[FAILED]` instead of exporting a potentially incorrect answer.

## Project Structure

```text
quizlet-crawler/
├── main.py
├── requirements.txt
├── README.md
├── QuizletCrawler.spec
├── build.bat
├── .gitignore
├── icon.ico
└── src/
    ├── __init__.py
    ├── crawler.py
    ├── formatter.py
    ├── google_docs.py
    ├── models.py
    ├── parser.py
    └── playwright_config.py
```
