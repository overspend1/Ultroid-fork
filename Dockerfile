# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

# Builder stage
FROM python:3.11-slim AS builder

# Set timezone ARG and ENV
ARG TZ_ARG=Asia/Kolkata
ENV TZ=${TZ_ARG}

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
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
    # Runtime dependencies that are also needed at build time for some packages
    git \
    curl \
    wget \
    ffmpeg \
    mediainfo \
    libmagic1 \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set up a virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
COPY resources/startup/optional-requirements.txt ./resources/startup/optional-requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel
# récit: re*/st*/optional-requirements.txt was in the original Dockerfile. Assuming re* is a glob for resources
# For simplicity and to ensure it matches original intent, copying the directory structure
# However, this makes the builder less efficient if these files change often.
# A better approach would be to list specific files if possible.
COPY resources/ ./resources/
RUN pip install -U -r resources/startup/optional-requirements.txt || true
RUN pip install -U -r requirements.txt

# Final stage
FROM python:3.11-slim AS final

# Create a non-root user and group
ARG UID=10001
RUN addgroup --system ultroid && \
    adduser --system --ingroup ultroid --no-create-home --uid ${UID} --shell /sbin/nologin --disabled-password ultroid

# Set timezone ARG and ENV
ARG TZ_ARG=Asia/Kolkata
ENV TZ=${TZ_ARG}
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install runtime system dependencies
# Reduced set compared to builder stage
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    mediainfo \
    libmagic1 \
    neofetch \
    # Git, curl, wget, unzip might be used by plugins at runtime. Keeping them for now.
    git \
    curl \
    wget \
    unzip \
    # libjpeg, libpng etc. are needed if Pillow was compiled against them and not statically linked
    # For simplicity, keeping ones that Pillow usually needs dynamically.
    # A more minimal image would require testing which .so files are truly needed by the installed wheels.
    libjpeg62-turbo \
    libpng16-16 \
    libwebp7 \
    libopenjp2-7 \
    libtiff5 \
    libfreetype6 \
    liblcms2-2 \
    libxml2 \
    libxslt1.1 \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
ENV VIRTUAL_ENV=/opt/venv
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Set working directory
WORKDIR /home/ultroid/app
USER ultroid

# Copy application code
# Ensure files are owned by the ultroid user after copying
COPY --chown=ultroid:ultroid . .

# Create necessary directories (as non-root user, these will be owned by ultroid)
# These paths should be relative to WORKDIR or absolute paths writable by ultroid
RUN mkdir -p downloads uploads logs resources/session

# Ensure scripts are executable by the user
RUN chmod +x startup sessiongen installer.sh health_check.sh

# Expose port if the application uses one (though this bot likely doesn't serve HTTP)
# EXPOSE 8080

# Start the bot
CMD ["bash", "startup"]
