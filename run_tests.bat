@echo off
REM Test runner script for Ultroid (Windows)

echo 🧪 Ultroid Test Suite
echo =====================

REM Check if pytest is installed
python -c "import pytest" 2>nul
if %errorlevel% neq 0 (
    echo Installing test dependencies...
    pip install -r test-requirements.txt
)

REM Run different test categories
echo Running Core Tests...
pytest tests/test_core.py -v --tb=short

echo Running Plugin Tests...
pytest tests/test_plugins.py -v --tb=short

echo Running Database Tests...
pytest tests/test_database.py -v --tb=short -m "not slow"

echo Running Update Tests...
pytest tests/test_updates.py -v --tb=short

echo Running All Tests with Coverage...
pytest tests/ --cov=pyUltroid --cov-report=html --cov-report=term-missing

echo Test run complete!
echo 📊 Coverage report available at htmlcov/index.html
