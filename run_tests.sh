#!/bin/bash
# Test runner script for Ultroid

echo "🧪 Ultroid Test Suite"
echo "====================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}Installing test dependencies...${NC}"
    pip3 install -r test-requirements.txt
fi

# Run different test categories
echo -e "${BLUE}Running Core Tests...${NC}"
pytest tests/test_core.py -v --tb=short

echo -e "${BLUE}Running Plugin Tests...${NC}"
pytest tests/test_plugins.py -v --tb=short

echo -e "${BLUE}Running Database Tests...${NC}"
pytest tests/test_database.py -v --tb=short -m "not slow"

echo -e "${BLUE}Running Update Tests...${NC}"
pytest tests/test_updates.py -v --tb=short

echo -e "${BLUE}Running All Tests with Coverage...${NC}"
pytest tests/ --cov=pyUltroid --cov-report=html --cov-report=term-missing

echo -e "${GREEN}Test run complete!${NC}"
echo "📊 Coverage report available at htmlcov/index.html"
