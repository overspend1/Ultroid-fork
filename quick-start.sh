#!/bin/bash

# Ultroid Quick Start Script
# One command deployment following official guide

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                    🚀 ULTROID QUICK START                   ║
║                Docker-based Deployment                      ║
║            Following Official Repository Guide              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${YELLOW}This script will:${NC}"
echo "✅ Check Docker installation"
echo "✅ Generate session string"
echo "✅ Configure environment"
echo "✅ Deploy with Docker Compose"
echo "✅ Start all services"
echo ""

read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Safety check for existing setup
echo -e "\n${BLUE}🔍 Checking for existing bot setup...${NC}"

EXISTING_SETUP=false
STARTUP_METHOD=""

# Check for existing .env file with session
if [ -f ".env" ] && grep -q "SESSION=.\+" .env; then
    EXISTING_SETUP=true
    STARTUP_METHOD="Environment file (.env)"
fi

# Check for existing session files  
if [ -f "resources/session/"* ] 2>/dev/null || [ -f "*.session" ] 2>/dev/null; then
    EXISTING_SETUP=true
    STARTUP_METHOD="${STARTUP_METHOD}, Session files"
fi

# Check for running processes (including startup script and multi_client)
if pgrep -f "pyUltroid\|startup\|multi_client" > /dev/null 2>&1; then
    EXISTING_SETUP=true
    STARTUP_METHOD="${STARTUP_METHOD}, Running bot process"
fi

# Check if startup script exists and is executable (bash startup method)
if [ -f "startup" ] && [ -x "startup" ]; then
    EXISTING_SETUP=true
    STARTUP_METHOD="${STARTUP_METHOD}, Startup script (bash startup)"
fi

if [ "$EXISTING_SETUP" = true ]; then
    echo -e "${YELLOW}⚠️  EXISTING BOT DETECTED!${NC}"
    echo ""
    echo -e "${BLUE}📋 Detected method:${STARTUP_METHOD}${NC}"
    echo -e "${GREEN}🛡️ I'll use the SAFE Docker setup to protect your existing bot.${NC}"
    echo -e "${BLUE}This creates an isolated environment that won't interfere with 'bash startup'.${NC}"
    echo ""
    read -p "Continue with safe setup? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    
    # Switch to safe setup
    chmod +x safe-docker-setup.sh
    exec ./safe-docker-setup.sh
    exit 0
fi

# Make scripts executable
echo -e "\n${BLUE}🔧 Setting up permissions...${NC}"
chmod +x docker-deploy.sh generate-session.sh

# Check if we have the necessary variables
if [ ! -f ".env" ] || ! grep -q "SESSION=.\+" .env; then
    echo -e "\n${YELLOW}🔑 Session string needed...${NC}"
    ./generate-session.sh
    
    echo -e "\n${YELLOW}📝 Please edit .env file with your credentials:${NC}"
    echo "   SESSION=your_session_string"
    echo "   API_ID=your_api_id"
    echo "   API_HASH=your_api_hash"
    echo ""
    read -p "Press Enter after editing .env file..."
fi

# Deploy
echo -e "\n${BLUE}🚀 Starting deployment...${NC}"
./docker-deploy.sh

echo -e "\n${GREEN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                   🎉 DEPLOYMENT COMPLETE!                   ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${YELLOW}📋 Quick Commands:${NC}"
echo "   make logs      - View bot logs"
echo "   make restart   - Restart bot"
echo "   make health    - Health check"
echo "   make backup    - Backup database"
echo ""
echo -e "${GREEN}🎊 Your Ultroid is now running!${NC}"
echo "Send .alive to your bot to test it!"
