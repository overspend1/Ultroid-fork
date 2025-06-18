#!/bin/bash

# Ultroid Ubuntu Server Setup Script
# This script sets up Ultroid userbot on Ubuntu with all dependencies

set -e  # Exit on error

echo "🚀 Ultroid Ubuntu Server Setup"
echo "================================"

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    wget \
    curl \
    unzip \
    ffmpeg \
    neofetch \
    mediainfo \
    nodejs \
    npm \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libmagic1

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Install additional optional dependencies
echo "🔧 Installing additional dependencies..."
pip install \
    telethonpatch \
    jikanpy \
    pyfiglet \
    lyrics-extractor \
    speech-recognition \
    shazamio \
    htmlwebshot \
    twikit \
    covid \
    pokedex \
    pydub \
    gtts \
    googletrans==4.0.0rc1 \
    python-barcode \
    qrcode[pil] \
    --ignore-errors

# Setup Google Drive (if credentials are available)
echo "🔑 Setting up Google Drive..."
if [ ! -f "credentials.json" ]; then
    echo "⚠️  Google Drive credentials.json not found!"
    echo "   Please add your credentials.json file to enable Google Drive features."
    echo "   Get it from: https://console.developers.google.com/"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p downloads uploads resources/session logs

# Set permissions
echo "🔐 Setting permissions..."
chmod +x startup
chmod +x sessiongen
chmod +x installer.sh

# Create systemd service file for autostart
echo "🎯 Creating systemd service..."
cat > ultroid.service << EOF
[Unit]
Description=Ultroid Userbot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python -m pyUltroid
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "📋 Setup complete! Next steps:"
echo ""
echo "1. Configure your bot:"
echo "   - Add your API credentials to config.py or .env"
echo "   - Add Google Drive credentials.json (optional)"
echo "   - Run: python3 -m pyUltroid"
echo ""
echo "2. Install as system service (optional):"
echo "   sudo cp ultroid.service /etc/systemd/system/"
echo "   sudo systemctl enable ultroid"
echo "   sudo systemctl start ultroid"
echo ""
echo "3. Manual start:"
echo "   source venv/bin/activate"
echo "   python3 -m pyUltroid"
echo ""
echo "🎉 Ultroid is ready for Ubuntu deployment!"
