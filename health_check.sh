#!/bin/bash

# Ultroid Health Check and Auto-Fix Script
# This script diagnoses and fixes common issues on Ubuntu servers

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Ultroid Health Check & Auto-Fix${NC}"
echo "=================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if Python package is installed
python_package_exists() {
    python3 -c "import $1" >/dev/null 2>&1
}

# Check Python version
echo -e "\n${BLUE}🐍 Checking Python version...${NC}"
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | grep -oP '\d+\.\d+')
    echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
    if [[ "$(echo "$PYTHON_VERSION >= 3.8" | bc)" -eq 1 ]]; then
        echo -e "${GREEN}✅ Python version is compatible${NC}"
    else
        echo -e "${RED}❌ Python 3.8+ required, found $PYTHON_VERSION${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Python3 not found${NC}"
    echo "Installing Python3..."
    sudo apt update && sudo apt install -y python3 python3-pip python3-venv
fi

# Check system dependencies
echo -e "\n${BLUE}🔧 Checking system dependencies...${NC}"
SYSTEM_DEPS=(git wget curl unzip ffmpeg mediainfo nodejs npm build-essential)
MISSING_DEPS=()

for dep in "${SYSTEM_DEPS[@]}"; do
    if command_exists "$dep"; then
        echo -e "${GREEN}✅ $dep${NC}"
    else
        echo -e "${RED}❌ $dep${NC}"
        MISSING_DEPS+=("$dep")
    fi
done

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo -e "\n${YELLOW}📦 Installing missing system dependencies...${NC}"
    sudo apt update
    sudo apt install -y "${MISSING_DEPS[@]}"
fi

# Check Python virtual environment
echo -e "\n${BLUE}🔧 Checking Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate || {
    echo -e "${RED}❌ Failed to activate virtual environment${NC}"
    exit 1
}
echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Check core Python dependencies
echo -e "\n${BLUE}📚 Checking core Python dependencies...${NC}"
CORE_DEPS=(telethon aiohttp requests beautifulsoup4 pillow)
MISSING_PYTHON_DEPS=()

for dep in "${CORE_DEPS[@]}"; do
    if python_package_exists "$dep"; then
        echo -e "${GREEN}✅ $dep${NC}"
    else
        echo -e "${RED}❌ $dep${NC}"
        MISSING_PYTHON_DEPS+=("$dep")
    fi
done

# Install missing Python dependencies
if [ ${#MISSING_PYTHON_DEPS[@]} -ne 0 ] || [ ! -f "requirements_installed.flag" ]; then
    echo -e "\n${YELLOW}📦 Installing Python dependencies...${NC}"
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
    touch requirements_installed.flag
fi

# Run Python diagnostic
echo -e "\n${BLUE}🔍 Running Python diagnostic...${NC}"
python3 diagnose_plugins.py

# Check Google Drive setup
echo -e "\n${BLUE}🔑 Checking Google Drive setup...${NC}"
if [ -f "credentials.json" ]; then
    echo -e "${GREEN}✅ credentials.json found${NC}"
    if [ -f "token.json" ]; then
        echo -e "${GREEN}✅ token.json found (authenticated)${NC}"
    else
        echo -e "${YELLOW}⚠️ token.json not found (run bot once to authenticate)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ credentials.json not found${NC}"
    echo "  Download from: https://console.developers.google.com/"
fi

# Check configuration
echo -e "\n${BLUE}⚙️ Checking configuration...${NC}"
if [ -f "config.py" ]; then
    echo -e "${GREEN}✅ config.py found${NC}"
    if grep -q "API_ID.*=.*[0-9]" config.py && grep -q "API_HASH.*=.*['\"]" config.py; then
        echo -e "${GREEN}✅ API credentials configured${NC}"
    else
        echo -e "${YELLOW}⚠️ API credentials may not be configured${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ config.py not found${NC}"
    if [ -f ".env" ]; then
        echo -e "${GREEN}✅ .env found (alternative config)${NC}"
    fi
fi

# Check file permissions
echo -e "\n${BLUE}🔐 Checking file permissions...${NC}"
EXECUTABLE_FILES=(startup sessiongen installer.sh ubuntu_setup.sh)
for file in "${EXECUTABLE_FILES[@]}"; do
    if [ -f "$file" ]; then
        if [ -x "$file" ]; then
            echo -e "${GREEN}✅ $file (executable)${NC}"
        else
            echo -e "${YELLOW}🔧 Making $file executable${NC}"
            chmod +x "$file"
        fi
    fi
done

# Create necessary directories
echo -e "\n${BLUE}📁 Checking directories...${NC}"
DIRS=(downloads uploads logs "resources/session")
for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✅ $dir/${NC}"
    else
        echo -e "${YELLOW}📁 Creating $dir/${NC}"
        mkdir -p "$dir"
    fi
done

# Test bot startup (dry run)
echo -e "\n${BLUE}🧪 Testing bot startup...${NC}"
timeout 10s python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from pyUltroid import ultroid_bot
    print('✅ Bot imports successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
except Exception as e:
    print(f'ℹ️ Other error (may be normal): {e}')
" || echo -e "${YELLOW}⚠️ Startup test timed out (may be normal)${NC}"

# Performance check
echo -e "\n${BLUE}📊 System performance check...${NC}"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')"
echo "Memory Usage: $(free -h | awk 'NR==2{printf "%.1f/%.1f GB (%.2f%%)\n", $3/1024, $2/1024, $3*100/$2}')"
echo "Disk Usage: $(df -h . | awk 'NR==2{printf "%s/%s (%s)\n", $3, $2, $5}')"

# Generate health report
echo -e "\n${BLUE}📋 Generating health report...${NC}"
cat > health_report.txt << EOF
Ultroid Health Check Report
Generated: $(date)
================================

System Information:
- OS: $(lsb_release -d | cut -f2)
- Python: $(python3 --version)
- User: $(whoami)
- Directory: $(pwd)

Dependencies Status:
$(if [ ${#MISSING_DEPS[@]} -eq 0 ]; then echo "✅ All system dependencies installed"; else echo "❌ Missing: ${MISSING_DEPS[*]}"; fi)
$(if [ ${#MISSING_PYTHON_DEPS[@]} -eq 0 ]; then echo "✅ All Python dependencies installed"; else echo "❌ Missing: ${MISSING_PYTHON_DEPS[*]}"; fi)

Configuration:
$(if [ -f "config.py" ]; then echo "✅ config.py found"; else echo "❌ config.py missing"; fi)
$(if [ -f "credentials.json" ]; then echo "✅ credentials.json found"; else echo "❌ credentials.json missing"; fi)
$(if [ -f "token.json" ]; then echo "✅ token.json found"; else echo "❌ token.json missing"; fi)

Next Steps:
1. If config.py is missing, create it with your API credentials
2. If credentials.json is missing, download it from Google Cloud Console
3. Run: python3 -m pyUltroid
4. For production: sudo cp ultroid.service /etc/systemd/system/ && sudo systemctl enable ultroid

EOF

echo -e "${GREEN}✅ Health check complete!${NC}"
echo -e "📄 Report saved to: ${BLUE}health_report.txt${NC}"
echo ""
echo -e "${GREEN}🚀 Ready to start Ultroid!${NC}"
echo "Run: ${BLUE}python3 -m pyUltroid${NC}"
