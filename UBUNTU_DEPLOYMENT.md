# Ultroid Ubuntu Server Deployment Guide

This guide helps you deploy Ultroid userbot on Ubuntu Server with all dependencies and plugins working correctly.

## 🚀 Quick Setup

### Method 1: Automated Setup Script
```bash
# Clone the repository
git clone https://github.com/TeamUltroid/Ultroid.git
cd Ultroid

# Run the automated setup script
chmod +x ubuntu_setup.sh
./ubuntu_setup.sh
```

### Method 2: Docker Deployment
```bash
# Build and run with Docker
docker build -t ultroid .
docker run -d --name ultroid-bot ultroid
```

### Method 3: Manual Installation

#### 1. System Dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git wget curl unzip ffmpeg mediainfo nodejs npm build-essential python3-dev libffi-dev libssl-dev libjpeg-dev libpng-dev libwebp-dev libopenjp2-7-dev libtiff5-dev libfreetype6-dev liblcms2-dev libxml2-dev libxslt1-dev zlib1g-dev libmagic1
```

#### 2. Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

#### 3. Configuration
```bash
# Copy example config
cp config.py.example config.py

# Edit configuration
nano config.py
```

## 📋 Required Dependencies

All required Python packages are listed in `requirements.txt`. The setup script automatically installs:

### Core Dependencies
- telethon
- gitpython
- python-decouple
- python-dotenv
- telegraph
- enhancer
- requests
- aiohttp
- catbox-uploader
- cloudscraper

### Plugin Dependencies
- beautifulsoup4 (web scraping)
- opencv-python (image/video processing)
- pillow (image manipulation)
- pytz (timezone handling)
- pygments (syntax highlighting)
- youtube-dl, yt-dlp (video downloading)
- qrcode (QR code generation)
- matplotlib, numpy, scipy (data visualization)
- selenium (web automation)
- And 40+ more specialized packages

## 🔧 Configuration

### 1. Bot Credentials
Add your credentials to `config.py`:
```python
API_ID = your_api_id
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"
```

### 2. Google Drive Setup (Optional)
1. Go to [Google Cloud Console](https://console.developers.google.com/)
2. Create a project and enable Google Drive API
3. Download `credentials.json`
4. Place it in the Ultroid root directory

### 3. Database (Optional)
Configure Redis or MongoDB for enhanced features:
```python
REDIS_URI = "redis://localhost:6379"
DATABASE_URL = "mongodb://localhost:27017/ultroid"
```

## 🎯 Running the Bot

### Development Mode
```bash
source venv/bin/activate
python3 -m pyUltroid
```

### Production Mode (systemd service)
```bash
# Copy service file
sudo cp ultroid.service /etc/systemd/system/

# Enable and start service
sudo systemctl enable ultroid
sudo systemctl start ultroid

# Check status
sudo systemctl status ultroid
```

### Docker Mode
```bash
docker run -d \
  --name ultroid-bot \
  -v $(pwd)/config.py:/app/config.py \
  -v $(pwd)/credentials.json:/app/credentials.json \
  ultroid
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Import Errors
Most plugins fail with "attempted relative import" because they need to be imported as modules:
```bash
# Run from project root
python3 -m pyUltroid
```

#### 2. Missing Dependencies
```bash
# Install missing packages
pip install package_name

# Or reinstall all requirements
pip install -r requirements.txt --force-reinstall
```

#### 3. Google Drive Issues
- Ensure `credentials.json` is in the root directory
- Run the bot once to generate `token.json`
- Check Google Cloud Console for API quotas

#### 4. Permission Errors
```bash
chmod +x startup sessiongen installer.sh
```

#### 5. FFmpeg Issues
```bash
sudo apt install ffmpeg mediainfo
```

### Plugin Health Check
Use the built-in diagnostic tool:
```bash
python3 diagnose_plugins.py
```

This will:
- Test all plugins for import errors
- Check for missing dependencies
- Generate a fix script
- Test Google Drive functionality

## 📊 Monitoring

### View Logs
```bash
# Service logs
sudo journalctl -u ultroid -f

# Manual logs
tail -f logs/ultroid.log
```

### Performance Monitoring
```bash
# Check resource usage
htop
docker stats ultroid-bot  # if using Docker
```

## 🛡️ Security

### File Permissions
```bash
chmod 600 config.py credentials.json
chmod 755 *.sh
```

### Firewall (if needed)
```bash
sudo ufw allow ssh
sudo ufw enable
```

## 🔄 Updates

### Manual Update
```bash
git pull origin main
pip install -r requirements.txt --upgrade
sudo systemctl restart ultroid  # if using systemd
```

### Auto-Update (Optional)
Add to crontab:
```bash
0 6 * * * cd /path/to/Ultroid && git pull && pip install -r requirements.txt --upgrade && systemctl restart ultroid
```

## 📞 Support

- **Telegram**: [@UltroidSupport](https://t.me/UltroidSupport)
- **GitHub Issues**: [Report Issues](https://github.com/TeamUltroid/Ultroid/issues)
- **Documentation**: [Wiki](https://github.com/TeamUltroid/Ultroid/wiki)

## 🎉 Success Indicators

Your bot is working correctly when:
- ✅ No import errors in logs
- ✅ Google Drive commands work (if configured)
- ✅ Media processing plugins work
- ✅ All dependencies installed successfully
- ✅ Bot responds to commands

Happy hosting! 🚀
