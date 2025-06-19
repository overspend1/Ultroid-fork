# 🐳 Ultroid Docker Deployment (Fork: overspend1/Ultroid-fork)

Complete Docker-based deployment solution for this fork of [Ultroid Telegram UserBot](https://github.com/overspend1/Ultroid-fork) with all dependencies, databases, and services included. This guide helps you build and run a Docker image directly from this repository's source code.

## ⚡ Quick Start (Recommended)

The easiest way to set up Ultroid Docker for this fork is by using the unified setup script:
```bash
# 1. Clone this repository
git clone https://github.com/overspend1/Ultroid-fork.git
cd Ultroid-fork

# 2. Run the setup script
bash ultroid_setup.sh
```
Follow the prompts, and choose the Docker setup option. The script will handle `.env` configuration, session generation guidance, and Docker build/run steps.

For manual Docker commands and more details, see below.

## 🎯 What's Included

### 📦 Complete Docker Stack
- **Ultroid Bot** - Main userbot service
- **Redis Database** - Primary data storage (recommended)
- **MongoDB** - Alternative database option
- **Session Generator** - Multiple methods for session creation

### 🔧 Management Tools
- **Automated deployment** - `docker-deploy.sh`
- **Session generation** - `generate-session.sh`
- **Easy commands** - `Makefile` with shortcuts
- **Health monitoring** - Built-in status checks

### 📚 Documentation
- **Docker Guide** - `DOCKER_DEPLOYMENT.md`
- **Deployment Summary** - `DEPLOYMENT_SUMMARY.md`
- **Environment Template** - `.env.sample`

## 🚀 Manual Docker Deployment Methods

If you prefer not to use `ultroid_setup.sh` or want more control:

### Method 1: Using Docker Compose (Recommended for Manual Setup)
Ensure you have an `.env` file configured (see [Configuration](#⚙️-configuration) and [Necessary Variables from Main README](../README.md#important-necessary-variables)).
```bash
# 1. Clone this repository (if not already done)
# git clone https://github.com/overspend1/Ultroid-fork.git
# cd Ultroid-fork

# 2. Configure .env file with your variables
# cp .env.sample .env
# nano .env # Fill in API_ID, API_HASH, SESSION, etc.

# 3. Build and start containers
docker-compose build
docker-compose up -d
```

### Method 2: Using Makefile (Shortcuts for Docker Compose)
The `Makefile` provides convenient shortcuts for Docker Compose commands.
```bash
# Configure .env file first

make build  # Build the Docker image
make start  # Start services (equivalent to docker-compose up -d)
# make logs, make stop, etc. are also available. See Makefile.
```

### Older Scripts (Deprecated)
The `quick-start.sh` and `docker-deploy.sh` scripts are now superseded by `ultroid_setup.sh`. While they might still work, using `ultroid_setup.sh` or manual `docker-compose` commands is recommended.

## 📋 Prerequisites

- Docker & Docker Compose
- Telegram API credentials ([my.telegram.org](https://my.telegram.org/apps))
- Session string (generated automatically)

## 🔑 Session String Generation

Choose your preferred method:

### 1. Telegram Bot (Easiest)
- Go to [@SessionGeneratorBot](https://t.me/SessionGeneratorBot)
- Follow the prompts

### 2. Docker Method
```bash
./generate-session.sh
# Select option 1 (Docker)
```

### 3. Online Method
- Visit [Replit Session Generator](https://replit.com/@TeamUltroid/UltroidStringSession)
- Fork and run

### 4. Local Method
```bash
wget -O session.py https://git.io/JY9JI && python3 session.py
```

## ⚙️ Configuration

### Required Variables (.env)
```env
SESSION=your_session_string_here
API_ID=your_api_id
API_HASH=your_api_hash
```

### Database Options

**Redis (Default)**
```env
REDIS_URI=redis://redis:6379
REDIS_PASSWORD=ultroid123
```

**MongoDB**
```env
MONGO_URI=mongodb://ultroid:ultroid123@mongodb:27017/ultroid?authSource=admin
```

**External Database**
```env
DATABASE_URL=postgresql://user:pass@host:port/db
```

### Optional Features
```env
BOT_TOKEN=          # Assistant bot
LOG_CHANNEL=        # Logging channel
OWNER_ID=           # Your user ID
HEROKU_API_KEY=     # For updates
TZ=Asia/Kolkata     # Set your desired timezone (e.g., Europe/London, America/New_York)
```

## 🎮 Management Commands

### Using Makefile (Recommended)
```bash
make help           # Show all commands
make start          # Start services
make stop           # Stop services
make restart        # Restart bot
make logs           # View logs
make shell          # Access container
make backup         # Backup database
make update         # Update and restart
make health         # Health check
make stats          # Resource usage
```

### Using Docker Compose
```bash
docker-compose up -d                    # Start
docker-compose down                     # Stop
docker-compose logs -f ultroid          # Logs
docker-compose restart ultroid          # Restart
docker-compose exec ultroid bash        # Shell (Note: Container runs as 'ultroid' user, WORKDIR is /home/ultroid/app)
```

## 🔍 Monitoring & Troubleshooting

### Check Status
```bash
make status         # Service overview
make health         # Health check  
make logs           # Recent logs
```

### Common Issues

**Services not starting**
```bash
make status
docker-compose logs ultroid
```

**Database connection issues**
```bash
make redis-cli      # Access Redis
make mongo-cli      # Access MongoDB
```

**Bot not responding**
```bash
make logs           # Check for errors
make restart        # Restart bot
```

## 📊 Features & Benefits

### ✅ Complete Solution
- All 188+ plugins/addons included
- Google Drive integration ready
- Media processing (images, videos, audio)
- Web scraping capabilities
- Database persistence
- Automated backups

### ✅ Production Ready
- Auto-restart on failure
- Health monitoring
- Volume persistence
- Easy updates
- Resource monitoring
- Security isolation

### ✅ Easy Management
- One-command deployment
- Simple update process
- Built-in backup system
- Comprehensive logging
- Shell access for debugging

## 🔄 Updates

### Automatic Updates
```bash
make update         # Pull, build, restart
```

### Manual Updates
```bash
git pull
docker-compose build
docker-compose up -d
```

## 💾 Backup & Restore

### Create Backup
```bash
make backup         # Creates timestamped backup
```

### Restore Backup
```bash
# Copy backup file to container
docker cp backup.rdb ultroid-redis:/data/dump.rdb
docker-compose restart redis
```

## 🌐 External Access

### Database Access
- **Redis**: `localhost:6379`
- **MongoDB**: `localhost:27017`

### Volume Mounts
```
./downloads     → /home/ultroid/app/downloads
./uploads       → /home/ultroid/app/uploads
./logs          → /home/ultroid/app/logs
./resources     → /home/ultroid/app/resources
# .env and credentials.json are also mounted into /home/ultroid/app/
```

## 🆚 Comparison with Other Methods

| Feature | Docker | Traditional | Heroku |
|---------|--------|-------------|---------|
| Setup Time | 5 minutes | 30+ minutes | 10 minutes |
| Dependencies | Automated | Manual | Automated |
| Database | Included | External setup | Add-on required |
| Updates | One command | Complex | Auto |
| Isolation | Full | None | Full |
| Cost | Free | Free | Limited free |

## 📞 Support & Resources

- **This Fork's Repository**: [overspend1/Ultroid-fork](https://github.com/overspend1/Ultroid-fork)
- **Original Ultroid Support (Telegram)**: [@UltroidSupport](https://t.me/UltroidSupport) (for general Ultroid questions)
- **Session Bot**: [@SessionGeneratorBot](https://t.me/SessionGeneratorBot)
- **Original Ultroid Documentation**: [Official Docs](https://ultroid.tech) (may differ from this fork)

## 📄 Files Overview

This repository contains:
```
📁 Ultroid-fork/
├── 🚀 ultroid_setup.sh         # Recommended unified setup script
├── 🐳 Dockerfile               # Defines how your fork's Docker image is built
├── 🐳 docker-compose.yml       # Orchestrates Docker services (bot, db)
├── 🔑 generate-session.sh      # Standalone session string generator utility
├── ⚙️ .env.sample              # Template for environment variables
├── 📖 README.md                # Main README for this fork
├── 📖 README_DOCKER.md         # This file - Docker specific guide for the fork
├── 📖 DOCKER_DEPLOYMENT.md     # Detailed Docker deployment steps
├── 🔧 Makefile                 # Shortcuts for common commands
└── ... (rest of the bot code and resources)
```

## 🎉 Success Indicators

Your deployment is successful when:

- ✅ `make status` shows all services running
- ✅ `make logs` shows no critical errors  
- ✅ Bot responds to `.alive` command
- ✅ All plugins load without issues
- ✅ Database connection is stable

---

**🚀 Ready to deploy your Ultroid fork with Docker!**

Use `bash ultroid_setup.sh` for the guided experience.
