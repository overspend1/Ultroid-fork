# 🐳 Ultroid Docker Deployment Guide

Complete Docker-based deployment guide for Ultroid Telegram UserBot following the official deployment patterns.

## 📋 Prerequisites

- Docker & Docker Compose installed
- Telegram API credentials (API_ID, API_HASH)
- Session string
- Basic knowledge of environment variables

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/TeamUltroid/Ultroid.git
cd Ultroid
```

### 2. Generate Session String
```bash
chmod +x generate-session.sh
./generate-session.sh
```

Choose from multiple methods:
- **Docker** (Recommended)
- **Telegram Bot** (@SessionGeneratorBot) 
- **Local Python**
- **Online Repl.it**

### 3. Configure Environment
```bash
cp .env.sample .env
nano .env
```

**Required variables:**
```env
SESSION=your_session_string
API_ID=your_api_id
API_HASH=your_api_hash
REDIS_URI=redis://redis:6379
REDIS_PASSWORD=ultroid123
```

### 4. Deploy with Docker
```bash
chmod +x docker-deploy.sh
./docker-deploy.sh
```

The script will:
- ✅ Check dependencies
- ✅ Setup environment
- ✅ Configure database
- ✅ Build Docker images
- ✅ Start all services

## 🏗️ Architecture

### Services Included

1. **Ultroid Bot** - Main userbot service
2. **Redis** - Primary database (recommended)
3. **MongoDB** - Alternative database option
4. **Session Generator** - One-time session creation

### Docker Compose Structure

```yaml
services:
  redis:          # Redis database
  mongodb:        # MongoDB alternative
  ultroid:        # Main bot service
  session-gen:    # Session generator (profile)
```

## 📁 Volume Mounts

```
./downloads     → /root/TeamUltroid/downloads
./uploads       → /root/TeamUltroid/uploads  
./logs          → /root/TeamUltroid/logs
./resources     → /root/TeamUltroid/resources
./.env          → /root/TeamUltroid/.env
```

## 🔧 Configuration Options

### Database Selection

**Redis (Recommended)**
```env
REDIS_URI=redis://redis:6379
REDIS_PASSWORD=ultroid123
```

**MongoDB Alternative**
```env
MONGO_URI=mongodb://ultroid:ultroid123@mongodb:27017/ultroid?authSource=admin
```

**External Database**
```env
DATABASE_URL=postgresql://user:pass@host:port/db
```

### Optional Features

```env
# Assistant Bot
BOT_TOKEN=your_bot_token
BOT_MODE=True
DUAL_MODE=True

# Logging
LOG_CHANNEL=your_log_channel_id
OWNER_ID=your_user_id

# Heroku Integration
HEROKU_API_KEY=your_heroku_api
HEROKU_APP_NAME=your_app_name

# Additional APIs
SPAMWATCH_API=your_spamwatch_api
OPENWEATHER_API=your_weather_api
REMOVE_BG_API=your_removebg_api
```

## 🎯 Management Commands

### Basic Operations
```bash
# View logs
docker-compose logs -f ultroid

# Restart bot
docker-compose restart ultroid

# Stop all services
docker-compose down

# Start services
docker-compose up -d
```

### Updates
```bash
# Update bot
git pull
docker-compose build
docker-compose up -d
```

### Maintenance
```bash
# Shell access
docker-compose exec ultroid bash

# Database access (Redis)
docker-compose exec redis redis-cli

# Database access (MongoDB)
docker-compose exec mongodb mongo
```

### Backup & Restore
```bash
# Backup data
docker-compose exec redis redis-cli --rdb /data/backup.rdb

# View container stats
docker stats
```

## 🔍 Troubleshooting

### Common Issues

**1. Session String Issues**
```bash
# Regenerate session
./generate-session.sh
```

**2. Database Connection Issues**
```bash
# Check database status
docker-compose ps
docker-compose logs redis
```

**3. Permission Issues**
```bash
# Fix permissions
sudo chown -R $USER:$USER downloads uploads logs
```

**4. Plugin Issues**
```bash
# Check plugin logs
docker-compose logs -f ultroid | grep -i error
```

### Health Checks

```bash
# Service status
docker-compose ps

# Resource usage
docker stats ultroid-bot

# Recent logs
docker-compose logs --tail=50 ultroid
```

## 🔐 Security Best Practices

### Environment Security
```bash
# Secure .env file
chmod 600 .env

# Use strong database passwords
REDIS_PASSWORD=generate_strong_password
MONGO_PASSWORD=generate_strong_password
```

### Container Security
```bash
# Run as non-root (in production)
# Use Docker secrets for sensitive data
# Regular security updates
docker-compose pull && docker-compose up -d
```

## 📊 Monitoring & Logs

### Log Locations
```
./logs/                    # Application logs
docker-compose logs        # Container logs
```

### Monitoring
```bash
# Real-time logs
docker-compose logs -f ultroid

# Resource monitoring
docker stats

# Service health
docker-compose ps
```

## 🚀 Production Deployment

### Recommended Setup
```bash
# Use external database for production
DATABASE_URL=postgresql://...

# Enable auto-restart
restart: unless-stopped

# Use proper logging
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Scaling
```bash
# Multiple bot instances
docker-compose up -d --scale ultroid=2
```

## 🔄 Updates & Maintenance

### Auto Updates
```bash
# Add to crontab
0 6 * * * cd /path/to/Ultroid && git pull && docker-compose build && docker-compose up -d
```

### Manual Updates
```bash
# 1. Backup data
docker-compose exec redis redis-cli BGSAVE

# 2. Update code
git pull

# 3. Rebuild and restart
docker-compose build
docker-compose up -d
```

## 📞 Support & Resources

- **Official Repository**: [TeamUltroid/Ultroid](https://github.com/TeamUltroid/Ultroid)
- **Telegram Support**: [@UltroidSupport](https://t.me/UltroidSupport)
- **Documentation**: [Official Docs](https://ultroid.tech)
- **Session Generator Bot**: [@SessionGeneratorBot](https://t.me/SessionGeneratorBot)

## ✨ Features Included

### Core Features
- ✅ All 188+ plugins/addons
- ✅ Google Drive integration
- ✅ Media processing (images, videos, audio)
- ✅ Web scraping capabilities
- ✅ Assistant bot support
- ✅ Database persistence
- ✅ Auto-updates
- ✅ Comprehensive logging

### Docker Benefits
- ✅ Isolated environment
- ✅ Easy deployment
- ✅ Consistent across platforms
- ✅ Built-in database services
- ✅ Volume persistence
- ✅ Health monitoring
- ✅ Easy scaling

---

**🎉 Ready for production Docker deployment!**
