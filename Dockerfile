# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

FROM python:3.11-slim

# Set timezone
ENV TZ=Asia/Kolkata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    unzip \
    ffmpeg \
    mediainfo \
    neofetch \
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
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /root/TeamUltroid

# Copy requirements and install Python dependencies
COPY requirements.txt .
COPY resources/ ./resources/
COPY re*/ ./re*/

# Install requirements following official method
RUN pip install --upgrade pip setuptools wheel
RUN pip install -U -r re*/st*/optional-requirements.txt || true
RUN pip install -U -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p downloads uploads logs resources/session
RUN chmod +x startup sessiongen installer.sh

# Start the bot using official startup method
CMD ["bash", "startup"]
