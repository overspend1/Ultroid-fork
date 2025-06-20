<p align="center">
  <img src="./resources/extras/logo_readme.jpg" alt="TeamUltroid Logo">
</p>
<h1 align="center">
  <b>Ultroid - UserBot</b>
</h1>

<b>A stable pluggable Telegram userbot + Voice & Video Call music bot, based on Telethon.</b>

[![](https://img.shields.io/badge/Ultroid-v0.8-crimson)](#)
[![Stars](https://img.shields.io/github/stars/TeamUltroid/Ultroid?style=flat-square&color=yellow)](https://github.com/TeamUltroid/Ultroid/stargazers)
[![Forks](https://img.shields.io/github/forks/TeamUltroid/Ultroid?style=flat-square&color=orange)](https://github.com/TeamUltroid/Ultroid/fork)
[![Size](https://img.shields.io/github/repo-size/TeamUltroid/Ultroid?style=flat-square&color=green)](https://github.com/TeamUltroid/Ultroid/)   
[![Python](https://img.shields.io/badge/Python-v3.10.3-blue)](https://www.python.org/)
[![CodeFactor](https://www.codefactor.io/repository/github/teamultroid/ultroid/badge/main)](https://www.codefactor.io/repository/github/teamultroid/ultroid/overview/main)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/TeamUltroid/Ultroid/graphs/commit-activity)
[![Docker Pulls](https://img.shields.io/docker/pulls/theteamultroid/ultroid?style=flat-square)](https://img.shields.io/docker/pulls/theteamultroid/ultroid?style=flat-square)   
[![Open Source Love svg2](https://badges.frapsoft.com/os/v2/open-source.svg?v=103)](https://github.com/TeamUltroid/Ultroid)
[![Contributors](https://img.shields.io/github/contributors/TeamUltroid/Ultroid?style=flat-square&color=green)](https://github.com/TeamUltroid/Ultroid/graphs/contributors)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://makeapullrequest.com)
[![License](https://img.shields.io/badge/License-AGPL-blue)](https://github.com/TeamUltroid/Ultroid/blob/main/LICENSE)   
[![Sparkline](https://stars.medv.io/Teamultroid/Ultroid.svg)](https://stars.medv.io/TeamUltroid/Ultroid)
----

# 🚀 Getting Started

The easiest way to set up Ultroid is by using our unified setup script.

**Run this command in your terminal:**
```bash
bash <(curl -s https://raw.githubusercontent.com/overspend1/Ultroid-fork/main/ultroid_setup.sh)
```
Or, clone this repository and run the script:
```bash
git clone https://github.com/overspend1/Ultroid-fork.git
cd Ultroid-fork
bash ultroid_setup.sh
```
This script will guide you through choosing either a Docker-based or a local Python installation for this fork and help configure the necessary variables.

For more detailed deployment options, including manual Docker setup, see below.

# Deployment Options

- **Automated Setup (Recommended)**: Use the `ultroid_setup.sh` script as described above.
- **Docker (Manual)**: For a manual Docker setup, see the [Manual Docker Setup](#manual-docker-setup) section below or the comprehensive [README_DOCKER.md](./README_DOCKER.md) for advanced details.
- **Local Python (Manual)**: See [Manual Local Python Setup](#manual-local-python-setup).
- **Okteto**: See [Deploy to Okteto](#deploy-to-okteto).

# Documentation
[![Documentation](https://img.shields.io/badge/Documentation-Ultroid-blue)](http://ultroid.tech/)

# Tutorial 
- Full Tutorial - [![Full Tutorial](https://img.shields.io/badge/Watch%20Now-blue)](https://www.youtube.com/watch?v=0wAV7pUzhDQ)

- Tutorial to get Redis URL and password - [here.](./resources/extras/redistut.md)
---

## Deploy to Okteto
Get the [Necessary Variables](#Necessary-Variables) and then click the button below!

[![Develop on Okteto](https://okteto.com/develop-okteto.svg)](https://cloud.okteto.com/deploy?repository=https://github.com/TeamUltroid/Ultroid)

## Manual Docker Setup
If you prefer a manual Docker setup instead of using the `ultroid_setup.sh` script:

**1. Prerequisites:**
   - Docker and Docker Compose installed on your system.
   - Telegram API credentials (API_ID and API_HASH) from [my.telegram.org/apps](https://my.telegram.org/apps).
   - A Telegram `SESSION` string (see [Session String](#Session-String) section for generation methods).

**2. Clone the Repository:**
   ```bash
   git clone https://github.com/overspend1/Ultroid-fork.git
   cd Ultroid-fork
   ```

**3. Configure `.env` File:**
   Copy the sample environment file and fill in your details.
   ```bash
   cp .env.sample .env
   nano .env # Or use your preferred text editor
   ```
   **Key variables to configure in `.env`:**
   ```env
   # Mandatory
   SESSION=your_session_string_here
   API_ID=your_api_id
   API_HASH=your_api_hash

   # Database (choose one, Redis is recommended for Docker)
   # Option 1: Redis (Default)
   REDIS_URI=redis://redis:6379 # Default for docker-compose setup
   REDIS_PASSWORD=ultroid123    # Default for docker-compose setup

   # Option 2: MongoDB (Uncomment and configure if using Mongo)
   # MONGO_URI=mongodb://ultroid:ultroid123@mongodb:27017/ultroid?authSource=admin

   # Option 3: External SQL Database (Uncomment and configure if using external SQL)
   # DATABASE_URL=postgresql://user:pass@host:port/db

   # Optional, but recommended
   BOT_TOKEN=your_assistant_bot_token # Optional, from @BotFather
   LOG_CHANNEL=your_log_channel_id    # Numeric ID, e.g., -100xxxxxxxx
   OWNER_ID=your_telegram_user_id     # Your numeric Telegram User ID
   TZ=Asia/Kolkata                    # Your timezone, e.g., Europe/London
   ```
   For a complete list of variables and their descriptions, refer to the `.env.sample` file and the [Necessary Variables](#Necessary-Variables) section.

**4. Build and Run with Docker Compose:**
   This is the recommended way to run Ultroid with Docker manually.
   ```bash
   docker-compose build
   docker-compose up -d
   ```
   This command will:
   - Build the Docker images for Ultroid and any associated services (like Redis or MongoDB if enabled in `docker-compose.yml`).
   - Start all services in detached mode (running in the background).

**5. Basic Management Commands:**
   - **View logs**: `docker-compose logs -f ultroid`
   - **Stop services**: `docker-compose down`
   - **Restart Ultroid service**: `docker-compose restart ultroid`
   - **Update (after `git pull`):** `docker-compose build && docker-compose up -d`

For a comprehensive guide to Docker deployment, including advanced configurations, troubleshooting, Makefile shortcuts, backup/restore, and more, please refer to the detailed **[README_DOCKER.md](./README_DOCKER.md)**.

## Manual Local Python Setup
The `ultroid_setup.sh` script automates these steps, but if you prefer manual local Python setup:

1.  Clone this repository: `git clone https://github.com/overspend1/Ultroid-fork.git && cd Ultroid-fork`
2.  Create a Python virtual environment: `python3 -m venv .venv`
3.  Activate it: `source .venv/bin/activate` (for Linux/macOS) or `.\.venv\Scripts\activate` (for Windows)
4.  Install dependencies: `pip install -r requirements.txt`
5.  Configure your variables in a `.env` file (see [Necessary Variables](#Necessary-Variables) below).
6.  Run the bot: `python3 -m pyUltroid`

---
## Important: Necessary Variables
Whether using the setup script or a manual method, you will need the following:

- **`SESSION`**: Your Telegram user account session string. The setup script and other utilities can help you generate this. See [Session String](#Session-String) for methods.

One of the following database:
- For **Redis** (tutorial [here](./resources/extras/redistut.md))
  - `REDIS_URI` - Redis endpoint URL, from [redislabs](http://redislabs.com/).
  - `REDIS_PASSWORD` - Redis endpoint Password, from [redislabs](http://redislabs.com/).
- For **MONGODB**
  - `MONGO_URI` - Get it from [mongodb](https://mongodb.com/atlas).
- For **SQLDB**
  - `DATABASE_URL`- Get it from [elephantsql](https://elephantsql.com).

## Session String
Different ways to get your `SESSION`:
* [![Run on Repl.it](https://replit.com/badge/github/TeamUltroid/Ultroid)](https://replit.com/@TeamUltroid/UltroidStringSession)
* Linux : `wget -O session.py https://git.io/JY9JI && python3 session.py`
* PowerShell : `cd desktop ; wget https://git.io/JY9JI -OutFile session.py ; python session.py`
* Termux : `wget -O session.py https://git.io/JY9JI && python session.py`
* Telegram Bot : [@SessionGeneratorBot](https://t.me/SessionGeneratorBot)
* **Using `ultroid_setup.sh`**: The setup script will guide you through session generation if needed.
* **Using `generate-session.sh`**: This script in the repository provides various methods: `bash generate-session.sh`

---

# Core Contributor Team

<table>
  <tr>
    <td align="center"><a href="https://github.com/xditya"><img src="https://avatars.githubusercontent.com/xditya" width="75px;" alt=""/><br/><sub><b>@xditya</b></sub></a></td>
    <td align="center"><a href="https://github.com/1danish-00"><img src="https://avatars.githubusercontent.com/1danish-00" width="75px;" alt=""/><br/><sub><b>@1danish_00</b></sub></a></td>
    <td align="center"><a href="https://github.com/buddhhu"><img src="https://avatars.githubusercontent.com/buddhhu" width="75px;" alt=""/><br/><sub><b>@buddhhu</b></sub></a></td>
    <td align="center"><a href="https://github.com/TechiError"><img src="https://avatars.githubusercontent.com/TechiError" width="75px;" alt=""/><br/><sub><b>@TechiError</b></sub></a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/New-dev0"><img src="https://avatars.githubusercontent.com/New-dev0" width="75px;" alt=""/><br/><sub><b>@New-dev0</b></sub></a></td>
    <td align="center"><a href="https://github.com/ArnabXD"><img src="https://avatars.githubusercontent.com/ArnabXD" width="75px;" alt=""/><br/><sub><b>@Arnab431</b></sub></a></td>
    <td align="center"><a href="https://github.com/sppidy"><img src="https://avatars.githubusercontent.com/sppidy" width="75px;" alt=""/><br/><sub><b>@sppidy</b></sub></a></td>
    <td align="center"><a href="https://github.com/Atul-Kumar-Jena"><img src="https://avatars.githubusercontent.com/Atul-kumar-Jena" width="75px;" alt=""/><br/><sub><b>@hellboi_atul</b></sub></a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/iAkashPattnaik"><img src="https://avatars.githubusercontent.com/iAkashPattnaik" width="75px;" alt=""/><br/><sub><b>@iAkashPattnaik</b></sub></a></td>
  </tr>
</table>

## Contributors

<a href="https://github.com/TeamUltroid/Ultroid/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=TeamUltroid/Ultroid" />
</a>

We are highly grateful for all the contributions made by our amazing community! ❤️

---

# License
[![License](https://www.gnu.org/graphics/agplv3-155x51.png)](LICENSE)   
Ultroid is licensed under [GNU Affero General Public License](https://www.gnu.org/licenses/agpl-3.0.en.html) v3 or later.


---
# Credits
* [![TeamUltroid-Devs](https://img.shields.io/static/v1?label=Teamultroid&message=devs&color=critical)](https://t.me/UltroidDevs)
* [Lonami](https://github.com/LonamiWebs/) for [Telethon.](https://github.com/LonamiWebs/Telethon)
* [MarshalX](https://github.com/MarshalX) for [PyTgCalls.](https://github.com/MarshalX/tgcalls)

> Made with 💕 by [@TeamUltroid](https://t.me/TeamUltroid).    