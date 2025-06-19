# 🐳 Ultroid Docker Deployment Guide (Fork: overspend1/Ultroid-fork)

Complete Docker-based deployment guide for this fork of Ultroid Telegram UserBot. This guide assumes you are building the Docker image from the source code of this repository.

## 📋 Prerequisites

- Docker & Docker Compose installed
- Telegram API credentials (API_ID, API_HASH)
- Session string
- Basic knowledge of environment variables

## 🚀 Recommended Setup: Using `ultroid_setup.sh`

The easiest and recommended way to deploy this fork using Docker is with the unified setup script:

1.  **Clone this repository:**
    ```bash
    git clone https://github.com/overspend1/Ultroid-fork.git
    cd Ultroid-fork
    ```
2.  **Run the setup script:**
    ```bash
    bash ultroid_setup.sh
    ```
    Select the Docker setup option when prompted. The script will guide you through:
    *   Checking dependencies (Docker, Docker Compose).
    *   Configuring your `.env` file with necessary variables (API keys, session string, database choice, etc.).
    *   Guiding session string generation if needed.
    *   Building the Docker image from this fork's source.
    *   Starting the Docker containers.

## Manually Deploying with Docker Compose (Advanced)

If you prefer a manual approach:

### 1. Clone This Repository
```bash
git clone https://github.com/overspend1/Ultroid-fork.git
cd Ultroid-fork
```

### 2. Configure Environment (`.env` file)
Copy the sample environment file and edit it with your details:
```bash
cp .env.sample .env
nano .env # Or your preferred editor
```
**Essential variables to fill:**
```env
SESSION=your_session_string_here # See README.md for generation methods
API_ID=your_api_id               # From my.telegram.org/apps
API_HASH=your_api_hash           # From my.telegram.org/apps
# Plus database configuration (see below or .env.sample)
```
Refer to [Necessary Variables in the main README](../README.md#important-necessary-variables) for more details on each variable. Session string can be generated using `bash generate-session.sh` or other methods.

### 3. Build and Deploy with Docker Compose
```bash
docker-compose build   # Builds the Docker image from this fork's Dockerfile
docker-compose up -d   # Starts the services (bot, database) in detached mode
```
This uses the `Dockerfile` and `docker-compose.yml` present in this repository.

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

The following host directories are mounted into the `ultroid` container. Note that the internal working directory is now `/home/ultroid/app`.
```
./downloads          → /home/ultroid/app/downloads
./uploads            → /home/ultroid/app/uploads
./logs               → /home/ultroid/app/logs
./resources/session  → /home/ultroid/app/resources/session
./.env               → /home/ultroid/app/.env (mounted read-only)
./credentials.json   → /home/ultroid/app/credentials.json (if present, mounted read-only)
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

# Timezone
TZ=Asia/Kolkata  # Example: Europe/London, America/New_York. Sets the container timezone.
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
docker-compose exec ultroid bash # Note: You will be logged in as the 'ultroid' user in /home/ultroid/app

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
docker-compose ps # Services should show (healthy) status after startup period
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
# Run as non-root (in production) - Implemented: Bot now runs as non-root 'ultroid' user.
# Use Docker secrets for sensitive data - Consider for advanced setups.
# Regular security updates
docker-compose pull && docker-compose up -d # Pulls latest base images and rebuilds Ultroid
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

- **This Fork's Repository**: [overspend1/Ultroid-fork](https://github.com/overspend1/Ultroid-fork)
- **Original Ultroid Support (Telegram)**: [@UltroidSupport](https://t.me/UltroidSupport) (for general Ultroid questions)
- **Original Ultroid Documentation**: [Official Docs](https://ultroid.tech) (may differ for this fork)
- **Session Generator Bot**: [@SessionGeneratorBot](https://t.me/SessionGeneratorBot) (for generating session strings)

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
- ✅ Isolated environment (now more secure with non-root user)
- ✅ Easy deployment
- ✅ Consistent across platforms
- ✅ Built-in database services (with healthchecks)
- ✅ Volume persistence
- ✅ Health monitoring (via Docker healthchecks and `health_check.sh`)
- ✅ Easy scaling

---

**🎉 Ready for production Docker deployment!**
