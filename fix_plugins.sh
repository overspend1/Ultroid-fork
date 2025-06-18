#!/bin/bash
# Auto-generated Ultroid Plugin Fixes Script

echo "🔧 Installing missing dependencies..."

# Install Google API dependencies
pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Install common web dependencies
pip3 install requests aiohttp

# Install media dependencies
pip3 install Pillow

# Install other common dependencies
pip3 install beautifulsoup4 lxml

echo "✅ Dependencies installation complete!"
echo ""
echo "🔑 Next steps for Google Drive:"
echo "1. Message your assistant bot with /start"
echo "2. Follow the setup process for Google Drive"
echo "3. Set GDRIVE_CLIENT_ID and GDRIVE_CLIENT_SECRET if using custom credentials"
echo ""
echo "🧪 Run the diagnostic again: python3 diagnose_plugins.py"
