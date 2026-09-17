# Quizlet Crawler

A simple Python CLI tool for extracting publicly available Quizlet question data and exporting it into A/B/C/D format.

## Features

* Extract publicly available Quizlet question data.
* Supports up to 500 questions per crawl.
* Supports questions with a variable number of choices.
* Does not require every question to have A, B, C, and D.
* Reports invalid questions when no valid choices can be extracted.
* Exports extracted questions to A/B/C/D format.
* Supports Google Docs export.
* Can be packaged as a Windows `.exe`.
* Bundles Playwright Chromium with the PyInstaller build.

## Requirements

* Windows
* Python 3.14+
* Internet connection

The project currently uses:

* Playwright 1.63.0
* Chromium 1243
* PyInstaller
* BeautifulSoup
* Pillow

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

CMD:

```cmd
.venv\Scripts\activate
```

PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run from Python

```cmd
python main.py
```

The Python version uses Playwright and Chromium installed in the current virtual environment.

## Question Choices

The crawler does **not** require every question to contain A, B, C, and D.

For example, all of the following can be valid:

```text
A. Choice A
B. Choice B
C. Choice C
D. Choice D
```

```text
A. Choice A
B. Choice B
C. Choice C
```

```text
A. Choice A
B. Choice B
```

The crawler only requires that valid choices can be extracted.

A question with no valid choices should be reported as `FAILED`.

## Answer Validation

The crawler should only export an answer when it can reliably determine that the answer belongs to one of the extracted choices.

Letters such as `A`, `B`, `C`, or `D` appearing inside the question text must not be incorrectly interpreted as the answer.

If the correct answer cannot be determined reliably, the crawler should report the question as `FAILED` instead of guessing.

## Build Windows EXE

The project uses `QuizletCrawler.spec` to configure PyInstaller and bundle Playwright Chromium.

### Recommended build

Run:

```cmd
build.bat
```

The build process:

1. Installs the required Python packages.
2. Sets `PLAYWRIGHT_BROWSERS_PATH=0`.
3. Installs Chromium locally inside the Playwright package.
4. Builds the application using `QuizletCrawler.spec`.
5. Includes the Chromium browser in the generated application.

The generated application is:

```text
dist\QuizletCrawler\QuizletCrawler.exe
```

### Manual build

If you want to build manually:

```cmd
set PLAYWRIGHT_BROWSERS_PATH=0
python -m playwright install chromium
python -m PyInstaller --noconfirm --clean QuizletCrawler.spec
```

## Playwright Chromium

The PyInstaller spec expects Chromium to be installed at:

```text
.venv\Lib\site-packages\playwright\driver\package\.local-browsers\
```

The current Chromium executable is located under:

```text
chromium-1243\chrome-win64\chrome.exe
```

The build copies this browser into the PyInstaller application.

The application also configures `PLAYWRIGHT_BROWSERS_PATH` automatically when running as a frozen PyInstaller application.

Therefore, the generated EXE does not require the target computer to separately install Chromium or Playwright.

## Running the EXE

After a successful build:

```cmd
dist\QuizletCrawler\QuizletCrawler.exe
```

Keep the entire directory together:

```text
dist\
└── QuizletCrawler\
    ├── QuizletCrawler.exe
    ├── _internal\
    └── playwright\
        └── driver\
            └── package\
                └── .local-browsers\
```

Do not copy only `QuizletCrawler.exe`.

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

## Git Ignore

Generated files such as `build/`, `dist/`, and `.venv/` are ignored by Git.

`QuizletCrawler.spec` is **not** ignored because it is required to build the application and bundle Chromium.

## Build Output

The following should not be committed:

```text
build/
dist/
.venv/
__pycache__/
*.pyc
```

The following build configuration files **must be committed**:

```text
QuizletCrawler.spec
build.bat
requirements.txt
```

## Git Workflow

After updating the project:

```cmd
git status
git add README.md requirements.txt .gitignore QuizletCrawler.spec build.bat src main.py
git commit -m "fix: bundle Chromium and update project documentation"
git push
```
