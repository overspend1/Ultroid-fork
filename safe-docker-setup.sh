#!/bin/bash

# Ultroid Docker Setup - SAFE MODE
# This script preserves your existing configuration and creates a separate Docker environment

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║               🛡️ ULTROID DOCKER - SAFE MODE                 ║"
echo "║            Preserves Your Existing Configuration            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${GREEN}✅ This script will:${NC}"
echo "  • Create a separate Docker environment"
echo "  • Keep your existing bot configuration untouched"
echo "  • Use different ports to avoid conflicts"
echo "  • Create isolated volumes for Docker data"
echo "  • Allow you to run both setups side by side"
echo ""

echo -e "${YELLOW}⚠️  What this script WON'T do:${NC}"
echo "  • Modify your existing .env file"
echo "  • Touch your current session files"
echo "  • Interfere with your running bot"
echo "  • Change any existing configurations"
echo ""

read -p "Continue with safe Docker setup? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled."
    exit 0
fi

# Enhanced detection for existing bot setup
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

# Check for running processes (including startup script)
if pgrep -f "pyUltroid\|startup\|multi_client" > /dev/null 2>&1; then
    EXISTING_SETUP=true
    STARTUP_METHOD="${STARTUP_METHOD}, Running bot process"
fi

# Check if startup script exists and is executable (indicates active setup)
if [ -f "startup" ] && [ -x "startup" ]; then
    EXISTING_SETUP=true
    STARTUP_METHOD="${STARTUP_METHOD}, Startup script (bash startup)"
fi

if [ "$EXISTING_SETUP" = true ]; then
    echo -e "${GREEN}✅ EXISTING ULTROID BOT DETECTED!${NC}"
    echo ""
    echo -e "${BLUE}📋 Detected setup method:${STARTUP_METHOD}${NC}"
    echo -e "${GREEN}🛡️ Perfect! This safe Docker setup will create an isolated environment.${NC}"
    echo -e "${YELLOW}Your current 'bash startup' method will remain completely untouched!${NC}"
    echo ""
    echo -e "${BLUE}You'll be able to run both:${NC}"
    echo -e "   • ${YELLOW}bash startup${NC} (your current bot)"
    echo -e "   • ${YELLOW}cd docker-ultroid && ./manage.sh start${NC} (new Docker bot)"
    echo ""
else
    echo -e "${GREEN}✅ No existing setup detected. Creating fresh Docker environment.${NC}"
fi

# Create Docker-specific directory
DOCKER_DIR="docker-ultroid"
echo -e "\n${BLUE}📁 Creating separate Docker environment...${NC}"

if [ -d "$DOCKER_DIR" ]; then
    echo -e "${YELLOW}⚠️  Docker directory already exists. Remove it? (y/n):${NC}"
    read -p "" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$DOCKER_DIR"
    else
        echo "Using existing directory..."
    fi
fi

mkdir -p "$DOCKER_DIR"/{downloads,uploads,logs,resources/session,backups}

# Create Docker-specific .env file
echo -e "${BLUE}⚙️ Creating Docker-specific configuration...${NC}"

# Auto-populate from existing config if available
AUTO_SESSION=""
AUTO_API_ID=""
AUTO_API_HASH=""
AUTO_BOT_TOKEN=""
AUTO_LOG_CHANNEL=""

# Try to extract from existing .env file
if [ -f "../.env" ]; then
    echo -e "${GREEN}📋 Found existing .env file, copying credentials...${NC}"
    AUTO_SESSION=$(grep "^SESSION=" ../.env 2>/dev/null | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    AUTO_API_ID=$(grep "^API_ID=" ../.env 2>/dev/null | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    AUTO_API_HASH=$(grep "^API_HASH=" ../.env 2>/dev/null | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    AUTO_BOT_TOKEN=$(grep "^BOT_TOKEN=" ../.env 2>/dev/null | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    AUTO_LOG_CHANNEL=$(grep "^LOG_CHANNEL=" ../.env 2>/dev/null | cut -d'=' -f2- | tr -d '"' | tr -d "'")
fi

# Try to extract from environment variables (if running in current session)
if [ -z "$AUTO_SESSION" ] && [ ! -z "$SESSION" ]; then
    AUTO_SESSION="$SESSION"
fi
if [ -z "$AUTO_API_ID" ] && [ ! -z "$API_ID" ]; then
    AUTO_API_ID="$API_ID"
fi
if [ -z "$AUTO_API_HASH" ] && [ ! -z "$API_HASH" ]; then
    AUTO_API_HASH="$API_HASH"
fi

cat > "$DOCKER_DIR/.env" << EOF
# Ultroid Docker Environment - Auto-populated from existing setup
# This is completely separate from your main bot configuration

# === REQUIRED (Auto-populated from your existing setup) ===
SESSION=${AUTO_SESSION}
API_ID=${AUTO_API_ID}
API_HASH=${AUTO_API_HASH}

# === DOCKER DATABASE (Isolated) ===
REDIS_URI=redis://redis:6380
REDIS_PASSWORD=ultroid_docker_123

# === OPTIONAL (Auto-populated if available) ===
BOT_TOKEN=${AUTO_BOT_TOKEN}
LOG_CHANNEL=${AUTO_LOG_CHANNEL}

# === DOCKER-SPECIFIC SETTINGS ===
BOT_MODE=True
DUAL_MODE=True
TZ=Asia/Kolkata

# === DATABASE CREDENTIALS ===
MONGO_USER=ultroid_docker
MONGO_PASSWORD=ultroid_docker_123
EOF

# Create Docker-specific compose file with different ports
echo -e "${BLUE}🐳 Creating isolated Docker configuration...${NC}"

cat > "$DOCKER_DIR/docker-compose.yml" << 'EOF'
version: '3.8'

services:
  # Redis Database (Different port to avoid conflicts)
  redis:
    image: redis:7-alpine
    container_name: ultroid-docker-redis
    restart: unless-stopped
    ports:
      - "6380:6379"  # Different port!
    volumes:
      - ultroid_docker_redis_data:/data
    environment:
      - REDIS_PASSWORD=ultroid_docker_123
    command: redis-server --requirepass ultroid_docker_123
    networks:
      - ultroid-docker-network

  # MongoDB Database (Different port to avoid conflicts)
  mongodb:
    image: mongo:6
    container_name: ultroid-docker-mongo
    restart: unless-stopped
    ports:
      - "27018:27017"  # Different port!
    volumes:
      - ultroid_docker_mongo_data:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=ultroid_docker
      - MONGO_INITDB_ROOT_PASSWORD=ultroid_docker_123
    networks:
      - ultroid-docker-network

  # Ultroid Bot (Isolated)
  ultroid:
    build: 
      context: ..
      dockerfile: Dockerfile
    container_name: ultroid-docker-bot
    restart: unless-stopped
    depends_on:
      - redis
    volumes:
      - ./downloads:/root/TeamUltroid/downloads
      - ./uploads:/root/TeamUltroid/uploads
      - ./logs:/root/TeamUltroid/logs
      - ./resources:/root/TeamUltroid/resources
      - ./.env:/root/TeamUltroid/.env
      - ../credentials.json:/root/TeamUltroid/credentials.json:ro
    environment:
      - REDIS_URI=redis://redis:6379
      - REDIS_PASSWORD=ultroid_docker_123
    networks:
      - ultroid-docker-network

volumes:
  ultroid_docker_redis_data:
  ultroid_docker_mongo_data:

networks:
  ultroid-docker-network:
    driver: bridge
EOF

# Create Docker management script
cat > "$DOCKER_DIR/manage.sh" << 'EOF'
#!/bin/bash

# Docker Ultroid Management Script

case "$1" in
    start)
        echo "🚀 Starting Docker Ultroid..."
        docker-compose up -d
        ;;
    stop)
        echo "⏹️ Stopping Docker Ultroid..."
        docker-compose down
        ;;
    restart)
        echo "🔄 Restarting Docker Ultroid..."
        docker-compose restart ultroid
        ;;
    logs)
        echo "📝 Showing Docker Ultroid logs..."
        docker-compose logs -f ultroid
        ;;
    status)
        echo "📊 Docker Ultroid status:"
        docker-compose ps
        ;;
    shell)
        echo "🐚 Accessing Docker Ultroid shell..."
        docker-compose exec ultroid bash
        ;;
    backup)
        echo "💾 Backing up Docker database..."
        mkdir -p backups
        docker-compose exec redis redis-cli BGSAVE
        docker cp ultroid-docker-redis:/data/dump.rdb backups/docker-backup-$(date +%Y%m%d-%H%M%S).rdb
        ;;
    clean)
        echo "🧹 Cleaning Docker Ultroid..."
        docker-compose down --rmi all --volumes --remove-orphans
        ;;
    *)
        echo "🐳 Docker Ultroid Management"
        echo "Usage: $0 {start|stop|restart|logs|status|shell|backup|clean}"
        echo ""
        echo "Commands:"
        echo "  start   - Start Docker Ultroid"
        echo "  stop    - Stop Docker Ultroid"
        echo "  restart - Restart Docker Ultroid"
        echo "  logs    - View logs"
        echo "  status  - Show status"
        echo "  shell   - Access shell"
        echo "  backup  - Backup database"
        echo "  clean   - Remove everything"
        ;;
esac
EOF

chmod +x "$DOCKER_DIR/manage.sh"

# Create instructions file
cat > "$DOCKER_DIR/README.md" << 'EOF'
# Docker Ultroid - Isolated Setup

This is a completely separate Docker environment that won't interfere with your existing bot.

## Quick Start

1. **Configure credentials:**
   ```bash
   nano .env
   # Add your SESSION, API_ID, API_HASH
   ```

2. **Start Docker bot:**
   ```bash
   ./manage.sh start
   ```

## Management Commands

```bash
./manage.sh start      # Start Docker bot
./manage.sh stop       # Stop Docker bot
./manage.sh restart    # Restart Docker bot
./manage.sh logs       # View logs
./manage.sh status     # Check status
./manage.sh shell      # Access container
./manage.sh backup     # Backup database
./manage.sh clean      # Remove everything
```

## Differences from Main Bot

- **Different ports:** Redis (6380), MongoDB (27018)
- **Isolated data:** Separate downloads, uploads, logs
- **Separate database:** Won't conflict with existing setup
- **Independent:** Can run alongside your main bot

## Safety Features

- ✅ Uses different container names
- ✅ Uses different network
- ✅ Uses different ports
- ✅ Isolated volumes
- ✅ Separate configuration
- ✅ Won't touch existing files

Your existing bot setup remains completely untouched!
EOF

echo -e "\n${GREEN}✅ Safe Docker environment created!${NC}"
echo -e "\n${BLUE}📁 Location: ${DOCKER_DIR}/${NC}"

# Show configuration status
echo -e "\n${BLUE}📋 Configuration Status:${NC}"
if [ ! -z "$AUTO_SESSION" ] && [ ! -z "$AUTO_API_ID" ] && [ ! -z "$AUTO_API_HASH" ]; then
    echo -e "   ${GREEN}✅ SESSION, API_ID, API_HASH auto-populated from existing setup${NC}"
    echo -e "   ${GREEN}✅ Ready to start immediately!${NC}"
    echo -e "\n${YELLOW}� Quick Start:${NC}"
    echo -e "   1. ${BLUE}cd ${DOCKER_DIR}${NC}"
    echo -e "   2. ${BLUE}./manage.sh start${NC}"
else
    echo -e "   ${YELLOW}⚠️  Please manually add your credentials${NC}"
    echo -e "\n${YELLOW}�📋 Next steps:${NC}"
    echo -e "   1. ${BLUE}cd ${DOCKER_DIR}${NC}"
    echo -e "   2. ${BLUE}nano .env${NC} (add your SESSION, API_ID, API_HASH)"
    echo -e "   3. ${BLUE}./manage.sh start${NC}"
fi
echo ""
echo -e "${GREEN}🛡️ Your existing bot configuration is completely safe!${NC}"
echo -e "${BLUE}📖 Check ${DOCKER_DIR}/README.md for detailed instructions${NC}"

echo -e "\n${YELLOW}💡 Port differences to avoid conflicts:${NC}"
echo -e "   Redis: 6380 (instead of 6379)"
echo -e "   MongoDB: 27018 (instead of 27017)"
echo -e "   All containers have 'docker' prefix"
echo ""
echo -e "${GREEN}🎉 You can now run both setups side by side safely!${NC}"
