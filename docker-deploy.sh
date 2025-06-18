#!/bin/bash

# Ultroid Docker Deployment Script
# Based on official Ultroid deployment guide

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    🚀 ULTROID DOCKER SETUP                  ║"
echo "║              Advanced Telegram UserBot Deployment           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Docker and Docker Compose
echo -e "${BLUE}🔍 Checking dependencies...${NC}"
if ! command_exists docker; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    echo "Installation: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command_exists docker-compose && ! docker compose version &>/dev/null; then
    echo -e "${RED}❌ Docker Compose not found. Please install Docker Compose first.${NC}"
    echo "Installation: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✅ Docker found: $(docker --version)${NC}"
echo -e "${GREEN}✅ Docker Compose found${NC}"

# Setup environment
echo -e "\n${BLUE}📋 Setting up environment...${NC}"

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 Creating .env file from template...${NC}"
    cp .env.sample .env
    echo -e "${YELLOW}⚠️  Please edit .env file with your configuration before starting!${NC}"
    
    echo -e "\n${PURPLE}📖 Required variables to fill in .env:${NC}"
    echo -e "   ${YELLOW}SESSION${NC}     - Get from @SessionGeneratorBot"
    echo -e "   ${YELLOW}API_ID${NC}      - Get from https://my.telegram.org/apps"
    echo -e "   ${YELLOW}API_HASH${NC}    - Get from https://my.telegram.org/apps"
    echo -e "   ${YELLOW}BOT_TOKEN${NC}   - Optional assistant bot token"
    echo -e "   ${YELLOW}OWNER_ID${NC}    - Your Telegram user ID"
    
    read -p "Press Enter to continue after editing .env file..."
else
    echo -e "${GREEN}✅ .env file found${NC}"
fi

# Check if SESSION is configured
if ! grep -q "SESSION=.\+" .env; then
    echo -e "${RED}❌ SESSION not configured in .env file${NC}"
    echo -e "${YELLOW}💡 Generate session string first!${NC}"
    
    read -p "Do you want to generate session string using Docker? (y/n): " generate_session
    if [[ $generate_session =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}🔑 Generating session string...${NC}"
        mkdir -p session_output
        docker-compose --profile session run --rm session-gen
        echo -e "${GREEN}✅ Session generated! Add it to your .env file.${NC}"
        exit 0
    else
        echo -e "${YELLOW}📝 Please generate session string manually:${NC}"
        echo "   1. Go to @SessionGeneratorBot"
        echo "   2. Or run: wget -O session.py https://git.io/JY9JI && python3 session.py"
        echo "   3. Add the session string to .env file"
        exit 1
    fi
fi

# Create necessary directories
echo -e "\n${BLUE}📁 Creating directories...${NC}"
mkdir -p downloads uploads logs resources/session session_output

# Database selection
echo -e "\n${BLUE}🗄️  Database Configuration${NC}"
echo "Choose your database:"
echo "1. Redis (Recommended, included in docker-compose)"
echo "2. MongoDB (Alternative, included in docker-compose)"  
echo "3. External Database (PostgreSQL/MongoDB)"

read -p "Select database (1-3): " db_choice

case $db_choice in
    1)
        echo -e "${GREEN}✅ Using Redis database${NC}"
        # Update .env to use Redis
        sed -i 's/^#.*REDIS_URI=/REDIS_URI=/' .env
        sed -i 's/^#.*REDIS_PASSWORD=/REDIS_PASSWORD=/' .env
        ;;
    2)
        echo -e "${GREEN}✅ Using MongoDB database${NC}"
        # Update .env to use MongoDB
        sed -i 's/^REDIS_URI=/#REDIS_URI=/' .env
        sed -i 's/^REDIS_PASSWORD=/#REDIS_PASSWORD=/' .env
        sed -i 's/^#.*MONGO_URI=/MONGO_URI=/' .env
        ;;
    3)
        echo -e "${YELLOW}⚠️  Please configure external database in .env file${NC}"
        ;;
    *)
        echo -e "${GREEN}✅ Using default Redis configuration${NC}"
        ;;
esac

# Optional features
echo -e "\n${BLUE}🔧 Optional Features${NC}"

read -p "Enable Google Drive features? (y/n): " enable_gdrive
if [[ $enable_gdrive =~ ^[Yy]$ ]]; then
    if [ ! -f "credentials.json" ]; then
        echo -e "${YELLOW}📝 Google Drive credentials.json not found${NC}"
        echo "   1. Go to https://console.developers.google.com/"
        echo "   2. Create a project and enable Google Drive API"
        echo "   3. Download credentials.json to this directory"
        read -p "Continue without Google Drive? (y/n): " continue_without
        if [[ ! $continue_without =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo -e "${GREEN}✅ Google Drive credentials found${NC}"
    fi
fi

# Safety check for existing bot setup
echo -e "${BLUE}🔍 Checking for existing bot setup...${NC}"

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
    echo -e "${YELLOW}⚠️  EXISTING BOT SETUP DETECTED!${NC}"
    echo ""
    echo -e "${BLUE}� Detected method:${STARTUP_METHOD}${NC}"
    echo -e "${RED}🛑 Found evidence of existing Ultroid setup${NC}"
    echo ""
    echo -e "${YELLOW}📋 Choose your deployment method:${NC}"
    echo "1. Safe Docker Setup (Recommended) - Creates isolated environment"
    echo "2. Replace existing setup (DANGEROUS - will overwrite)"
    echo "3. Cancel deployment"
    echo ""
    read -p "Select option (1-3): " safety_choice
    
    case $safety_choice in
        1)
            echo -e "${GREEN}✅ Switching to safe Docker setup...${NC}"
            echo -e "${BLUE}Your 'bash startup' method will remain untouched!${NC}"
            exec ./safe-docker-setup.sh
            exit 0
            ;;
        2)
            echo -e "${RED}⚠️  WARNING: This will overwrite your existing setup!${NC}"
            echo -e "${YELLOW}This includes your current 'bash startup' configuration!${NC}"
            read -p "Are you absolutely sure? Type 'YES' to continue: " confirm
            if [ "$confirm" != "YES" ]; then
                echo "Deployment cancelled for safety."
                exit 0
            fi
            echo -e "${YELLOW}🔄 Proceeding with replacement...${NC}"
            ;;
        3)
            echo "Deployment cancelled."
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Invalid selection${NC}"
            exit 1
            ;;
    esac
fi

# Build and start services
echo -e "\n${BLUE}🚀 Starting Ultroid services...${NC}"

echo -e "${YELLOW}📦 Building Docker image...${NC}"
docker-compose build

case $db_choice in
    1)
        echo -e "${BLUE}🚀 Starting Redis + Ultroid...${NC}"
        docker-compose up -d redis ultroid
        ;;
    2)
        echo -e "${BLUE}🚀 Starting MongoDB + Ultroid...${NC}"
        docker-compose up -d mongodb ultroid
        ;;
    *)
        echo -e "${BLUE}🚀 Starting Ultroid only...${NC}"
        docker-compose up -d ultroid
        ;;
esac

# Wait for services to start
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 10

# Check service status
echo -e "\n${BLUE}📊 Service Status:${NC}"
docker-compose ps

# Show logs
echo -e "\n${BLUE}📝 Recent logs:${NC}"
docker-compose logs --tail=20 ultroid

# Success message
echo -e "\n${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    🎉 DEPLOYMENT COMPLETE!                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${GREEN}✅ Ultroid is now running in Docker!${NC}"
echo -e "\n${BLUE}📋 Management Commands:${NC}"
echo -e "   ${YELLOW}View logs:${NC}        docker-compose logs -f ultroid"
echo -e "   ${YELLOW}Restart bot:${NC}      docker-compose restart ultroid"
echo -e "   ${YELLOW}Stop bot:${NC}         docker-compose down"
echo -e "   ${YELLOW}Update bot:${NC}       git pull && docker-compose build && docker-compose up -d"
echo -e "   ${YELLOW}Shell access:${NC}     docker-compose exec ultroid bash"

echo -e "\n${BLUE}🔍 Service URLs:${NC}"
if [[ $db_choice == "1" ]]; then
    echo -e "   ${YELLOW}Redis:${NC}           localhost:6379"
fi
if [[ $db_choice == "2" ]]; then
    echo -e "   ${YELLOW}MongoDB:${NC}         localhost:27017"
fi

echo -e "\n${PURPLE}💡 Next Steps:${NC}"
echo -e "   1. Check logs to ensure bot is working: ${YELLOW}docker-compose logs -f ultroid${NC}"
echo -e "   2. Send ${YELLOW}.alive${NC} command to your bot to test"
echo -e "   3. Configure additional features in .env if needed"
echo -e "   4. Add more plugins from addons/ directory"

echo -e "\n${GREEN}🎊 Happy botting!${NC}"
