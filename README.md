# Quizlet Crawler

Simple Python CLI tool for extracting publicly available Quizlet question data and exporting it into A/B/C/D format.

## Requirements

* Python 3.10+
* Internet connection
* Playwright Chromium

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd quizlet-crawler
```

### 2. Create a virtual environment

```bash
py -3.14 -m venv .venv
```

### 3. Activate the virtual environment

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

**Windows CMD:**

```cmd
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Install Playwright Chromium

```bash
python -m playwright install chromium
```

## Run

Run the crawler directly with Python:

```bash
python main.py
```

## Build `.exe`

Build the Windows executable with PyInstaller:

```bash
python -m PyInstaller --noconfirm --clean --onedir --windowed --name QuizletCrawler --icon=icon.ico main.py
```

The built application will be located at:

```text
dist/
└── QuizletCrawler/
    ├── QuizletCrawler.exe
    └── ...
```

### Notes

* `.venv/`, `build/`, and `dist/` are not included in the repository.
* `PyInstaller` and `Pillow` are included in `requirements.txt` because they are required for building the `.exe` with the application icon.
* Playwright Chromium must be installed separately using:

```bash
python -m playwright install chromium
```

* The generated `.exe` may require additional Playwright browser packaging if it is intended to run on a machine without Playwright/Chromium installed.

## Project Structure

```text
quizlet-crawler/
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
└── icon.ico
```
