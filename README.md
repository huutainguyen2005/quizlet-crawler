# Quizlet Crawler

Simple Python CLI tool for extracting publicly available Quizlet question data and exporting it into A/B/C/D format.

## Features

- Extracts publicly available Quizlet question data.
- Supports up to 500 questions per crawl.
- Validates that every question has choices A, B, C, and D.
- Reports invalid questions as `FAILED` instead of silently skipping them.
- Exports valid questions to A/B/C/D format.
- Supports Google Docs export.
- Can be packaged as a Windows `.exe` with Playwright Chromium bundled for the build.

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

For **CMD**:

```cmd
.venv\Scripts\activate
```

For **PowerShell**:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run from Python

Run the crawler directly:

```cmd
python main.py
```

The crawler will open the configured workflow and process the Quizlet URL.

## Invalid Questions

The crawler validates each question before exporting it.

For example, this is invalid:

```text
Question:
Quan điểm nào cho rằng: Không gian, thời gian và vận động không liên quan với nhau ở bên ngoài vật chất?

A. Quan điểm chủ nghĩa duy vật siêu hình.
B. Quan điểm chủ nghĩa duy vật biện chứng.
C. Quan điểm chủ nghĩa duy tâm khách quan.
Quan điểm chủ nghĩa duy vật chất phác.
```

The question is missing choice `D`, so the crawler reports it as:

```text
[FAILED] Missing choice(s): D
```

The invalid question is not exported as a normal question. This makes it easy to find and manually fix the original Quizlet card.

## Google Docs Export

Only validated questions should be exported to Google Docs.

The answer must match one of the four choices (`A`, `B`, `C`, or `D`). The crawler does not treat an `A/B/C/D` string appearing inside the question text as the correct answer.

If a question cannot be reliably matched to a valid choice, it is reported as `FAILED` instead of being exported with a potentially incorrect answer.

## Build Windows `.exe`

Use the included build script:

```cmd
build.bat
```

The script prepares the Playwright browser and builds the application with PyInstaller.

The output will be:

```text
dist/
└── QuizletCrawler/
    ├── QuizletCrawler.exe
    └── _internal/
        └── ...
```

### Manual build

If you prefer to build manually:

```cmd
set PLAYWRIGHT_BROWSERS_PATH=0
python -m playwright install chromium
python -m PyInstaller --noconfirm --clean QuizletCrawler.spec
```

The `QuizletCrawler.spec` file is configured to include the Playwright Chromium browser in the application bundle.

## Important: Python vs `.exe`

There are two different ways to run the project:

### Run source code

```cmd
python main.py
```

In this mode, Playwright uses the browser installed for the current Python environment.

### Run the built `.exe`

```cmd
dist\QuizletCrawler\QuizletCrawler.exe
```

The `.exe` build includes the required Chromium browser through the PyInstaller configuration. Do not assume that installing Chromium globally on another machine will fix a missing browser inside an already-built application.

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

## Gitignored Files

The following local/generated files should not be committed:

```text
.venv/
build/
dist/
*.spec
__pycache__/
*.py[cod]
```

Each developer creates their own `.venv` and installs dependencies from `requirements.txt`.
