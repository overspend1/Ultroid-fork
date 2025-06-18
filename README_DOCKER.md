# 🐳 Ultroid Docker Deployment

Complete Docker-based deployment solution for [Ultroid Telegram UserBot](https://github.com/TeamUltroid/Ultroid) with all dependencies, databases, and services included.

## ⚡ Quick Start

```bash
# 1. Clone repository
git clone https://github.com/TeamUltroid/Ultroid.git
cd Ultroid

# 2. One-command deployment
chmod +x quick-start.sh && ./quick-start.sh
```

That's it! The script will guide you through session generation and deployment.

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

## 🚀 Deployment Methods

### Method 1: Quick Start (Recommended)
```bash
./quick-start.sh
```

### Method 2: Step by Step
```bash
# Generate session
./generate-session.sh

# Configure environment
cp .env.sample .env
nano .env

# Deploy
./docker-deploy.sh
```

### Method 3: Manual Commands
```bash
# Build and start
make build
make start

# Or using docker-compose directly
docker-compose up -d
```

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
docker-compose exec ultroid bash        # Shell
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
./downloads     → Bot downloads
./uploads       → Bot uploads  
./logs          → Application logs
./resources     → Bot resources
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

- **Repository**: [TeamUltroid/Ultroid](https://github.com/TeamUltroid/Ultroid)
- **Telegram**: [@UltroidSupport](https://t.me/UltroidSupport)
- **Session Bot**: [@SessionGeneratorBot](https://t.me/SessionGeneratorBot)
- **Documentation**: [Official Docs](https://ultroid.tech)

## 📄 Files Overview

```
📁 Ultroid/
├── 🐳 docker-compose.yml       # Service orchestration
├── 🐳 Dockerfile               # Container definition
├── 🚀 quick-start.sh           # One-command deployment
├── 🚀 docker-deploy.sh         # Advanced deployment
├── 🔑 generate-session.sh      # Session generator
├── ⚙️ .env.sample              # Environment template
├── 📖 DOCKER_DEPLOYMENT.md     # Complete guide
├── 📋 DEPLOYMENT_SUMMARY.md    # Summary
├── 🔧 Makefile                 # Easy commands
└── 📚 README_DOCKER.md         # This file
```

## 🎉 Success Indicators

Your deployment is successful when:

- ✅ `make status` shows all services running
- ✅ `make logs` shows no critical errors  
- ✅ Bot responds to `.alive` command
- ✅ All plugins load without issues
- ✅ Database connection is stable

---

**🚀 Ready to deploy Ultroid with Docker!**

Start with `./quick-start.sh` for the easiest experience.
