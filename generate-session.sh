#!/bin/bash

# Ultroid Session Generator - Docker Version
# Generate Telegram session string using Docker

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                🔑 ULTROID SESSION GENERATOR                 ║"
echo "║             Generate Telegram Session String                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}📱 Choose session generation method:${NC}"
echo "1. Docker (Recommended)"
echo "2. Local Python"
echo "3. Telegram Bot (@SessionGeneratorBot)"
echo "4. Online Repl.it"

read -p "Select method (1-4): " method

case $method in
    1)
        echo -e "\n${BLUE}🐳 Using Docker method...${NC}"
        
        # Create temporary session container
        echo -e "${YELLOW}📦 Setting up session generator...${NC}"
        mkdir -p session_output
        
        # Build if needed
        if ! docker images | grep -q ultroid-main; then
            echo -e "${YELLOW}🔨 Building Docker image...${NC}"
            docker build -t ultroid-session .
        fi
        
        echo -e "${GREEN}🚀 Starting session generator...${NC}"
        echo -e "${YELLOW}📝 Follow the prompts to enter your Telegram credentials${NC}"
        
        docker run -it --rm \
            -v "$(pwd)/session_output:/output" \
            ultroid-session \
            bash -c "
                cd /output
                wget -O session.py https://git.io/JY9JI
                python3 session.py
                echo
                echo '✅ Session generated successfully!'
                echo '📋 Copy the session string above to your .env file'
                echo '📁 Session files saved to session_output/ directory'
            "
        ;;
        
    2)
        echo -e "\n${BLUE}🐍 Using local Python method...${NC}"
        
        # Check if Python is available
        if ! command -v python3 &> /dev/null; then
            echo -e "${RED}❌ Python3 not found. Please install Python3 or use Docker method.${NC}"
            exit 1
        fi
        
        echo -e "${YELLOW}📥 Downloading session generator...${NC}"
        wget -O session.py https://git.io/JY9JI
        
        echo -e "${GREEN}🚀 Starting session generator...${NC}"
        python3 session.py
        
        echo -e "${GREEN}✅ Session generated!${NC}"
        rm -f session.py
        ;;
        
    3)
        echo -e "\n${BLUE}🤖 Using Telegram Bot method...${NC}"
        echo -e "${YELLOW}📱 Steps:${NC}"
        echo "1. Open Telegram"
        echo "2. Search for @SessionGeneratorBot"
        echo "3. Start the bot and follow instructions"
        echo "4. Copy the session string to your .env file"
        echo ""
        echo -e "${GREEN}✨ This is the easiest method!${NC}"
        ;;
        
    4)
        echo -e "\n${BLUE}🌐 Using Online Repl.it method...${NC}"
        echo -e "${YELLOW}📱 Steps:${NC}"
        echo "1. Go to: https://replit.com/@TeamUltroid/UltroidStringSession"
        echo "2. Click 'Fork' to create your own copy"
        echo "3. Click 'Run' and follow the instructions"
        echo "4. Copy the session string to your .env file"
        echo ""
        echo -e "${GREEN}✨ No local setup required!${NC}"
        ;;
        
    *)
        echo -e "${RED}❌ Invalid selection${NC}"
        exit 1
        ;;
esac

echo -e "\n${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                     📋 NEXT STEPS                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}1.${NC} Add the session string to your .env file:"
echo -e "   ${BLUE}SESSION=your_session_string_here${NC}"
echo ""
echo -e "${YELLOW}2.${NC} Make sure you have configured:"
echo -e "   ${BLUE}API_ID=your_api_id${NC}"
echo -e "   ${BLUE}API_HASH=your_api_hash${NC}"
echo ""
echo -e "${YELLOW}3.${NC} Start the bot:"
echo -e "   ${BLUE}./docker-deploy.sh${NC}"
echo ""
echo -e "${GREEN}🎉 You're ready to deploy Ultroid!${NC}"
