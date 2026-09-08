@echo off
setlocal
cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
) else if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
)

python -c "import fastapi, sentence_transformers, numpy, pandas, pypdf, fpdf" 2>nul
if errorlevel 1 (
    echo Installing Python dependencies...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install dependencies. Create a venv first:
        echo   python -m venv venv
        echo   venv\Scripts\activate
        echo   pip install -r requirements.txt
        exit /b 1
    )
)

if not exist "corpus\medical_exemption.pdf" (
    echo Generating medical exemption PDF...
    python scripts\generate_pdf.py
    if errorlevel 1 exit /b 1
)

if not exist "data\embeddings.npy" (
    echo Building vector index. First run downloads the embedding model...
    python scripts\build_index.py
    if errorlevel 1 exit /b 1
)

echo Starting RuleGuard at http://127.0.0.1:8000
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
