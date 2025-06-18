# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import get_help

__doc__ = get_help("help_bot")

import os
import re
import sys
import time
import asyncio
from platform import python_version as pyver
from random import choice

from telethon import __version__
from telethon.errors.rpcerrorlist import (
    BotMethodInvalidError,
    ChatSendMediaForbiddenError,
)

from pyUltroid.version import __version__ as UltVer

from . import HOSTED_ON, LOGS

try:
    from git import Repo
    from git.exc import InvalidGitRepositoryError, NoSuchPathError
except ImportError:
    LOGS.error("bot: 'gitpython' module not found!")
    Repo = None

from telethon.utils import resolve_bot_file_id

from . import (
    ATRA_COL,
    LOGS,
    OWNER_NAME,
    ULTROID_IMAGES,
    Button,
    Carbon,
    Telegraph,
    Var,
    allcmds,
    asst,
    bash,
    call_back,
    callback,
    def_logs,
    eor,
    get_string,
    heroku_logs,
    in_pattern,
    inline_pic,
    restart,
    shutdown,
    start_time,
    time_formatter,
    udB,
    ultroid_cmd,
    ultroid_version,
    updater,
)


def ULTPIC():
    return inline_pic() or choice(ULTROID_IMAGES)


buttons = [
    [
        Button.url(get_string("bot_3"), "https://github.com/ThePrateekBhatia/Ultroid"),
        Button.url(get_string("bot_4"), "t.me/UltroidSupportChat"),
    ]
]

# Will move to strings
alive_txt = """
The Ultroid Userbot

  ◍ Version - {}
  ◍ Py-Ultroid - {}
  ◍ Telethon - {}
"""

in_alive = "{}\n\n🌀 <b>Ultroid Version -><b> <code>{}</code>\n🌀 <b>PyUltroid -></b> <code>{}</code>\n🌀 <b>Python -></b> <code>{}</code>\n🌀 <b>Uptime -></b> <code>{}</code>\n🌀 <b>Branch -></b>[ {} ]\n\n• <b>Join @TeamUltroid</b>"


@callback("alive")
async def alive(event):
    text = alive_txt.format(ultroid_version, UltVer, __version__)
    await event.answer(text, alert=True)


@ultroid_cmd(
    pattern="alive( (.*)|$)",
)
async def lol(ult):
    match = ult.pattern_match.group(1).strip()
    inline = None
    if match in ["inline", "i"]:
        try:
            res = await ult.client.inline_query(asst.me.username, "alive")
            return await res[0].click(ult.chat_id)
        except BotMethodInvalidError:
            pass
        except BaseException as er:
            LOGS.exception(er)
        inline = True
    pic = udB.get_key("ALIVE_PIC")
    if isinstance(pic, list):
        pic = choice(pic)
    uptime = time_formatter((time.time() - start_time) * 1000)
    header = udB.get_key("ALIVE_TEXT") or get_string("bot_1")
    y = Repo().active_branch
    xx = Repo().remotes[0].config_reader.get("url")
    rep = xx.replace(".git", f"/tree/{y}")
    kk = f" `[{y}]({rep})` "
    if inline:
        kk = f"<a href={rep}>{y}</a>"
        parse = "html"
        als = in_alive.format(
            header,
            f"{ultroid_version} [{HOSTED_ON}]",
            UltVer,
            pyver(),
            uptime,
            kk,
        )

        if _e := udB.get_key("ALIVE_EMOJI"):
            als = als.replace("🌀", _e)
    else:
        parse = "md"
        als = (get_string("alive_1")).format(
            header,
            OWNER_NAME,
            f"{ultroid_version} [{HOSTED_ON}]",
            UltVer,
            uptime,
            pyver(),
            __version__,
            kk,
        )

        if a := udB.get_key("ALIVE_EMOJI"):
            als = als.replace("✵", a)
    if pic:
        try:
            await ult.reply(
                als,
                file=pic,
                parse_mode=parse,
                link_preview=False,
                buttons=buttons if inline else None,
            )
            return await ult.try_delete()
        except ChatSendMediaForbiddenError:
            pass
        except BaseException as er:
            LOGS.exception(er)
            try:
                await ult.reply(file=pic)
                await ult.reply(
                    als,
                    parse_mode=parse,
                    buttons=buttons if inline else None,
                    link_preview=False,
                )
                return await ult.try_delete()
            except BaseException as er:
                LOGS.exception(er)
    await eor(
        ult,
        als,
        parse_mode=parse,
        link_preview=False,
        buttons=buttons if inline else None,
    )


@ultroid_cmd(pattern="ping$", chats=[], type=["official", "assistant"])
async def _(event):
    start = time.time()
    x = await event.eor("Pong !")
    end = round((time.time() - start) * 1000)
    uptime = time_formatter((time.time() - start_time) * 1000)
    await x.edit(get_string("ping").format(end, uptime))


@ultroid_cmd(
    pattern="cmds$",
)
async def cmds(event):
    await allcmds(event, Telegraph)


heroku_api = Var.HEROKU_API


@ultroid_cmd(
    pattern="restart$",
    fullsudo=True,
)
async def restartbt(ult):
    ok = await ult.eor(get_string("bot_5"))
    call_back()
    who = "bot" if ult.client._bot else "user"
    udB.set_key("_RESTART", f"{who}_{ult.chat_id}_{ok.id}")
    if heroku_api:
        return await restart(ok)
    await bash("git pull && pip3 install -r requirements.txt")
    await bash("pip3 install -r requirements.txt --break-system-packages")
    if len(sys.argv) > 1:
        os.execl(sys.executable, sys.executable, "main.py")
    else:
        os.execl(sys.executable, sys.executable, "-m", "pyUltroid")


@ultroid_cmd(
    pattern="shutdown$",
    fullsudo=True,
)
async def shutdownbot(ult):
    await shutdown(ult)


@ultroid_cmd(
    pattern="logs( (.*)|$)",
    chats=[],
)
async def _(event):
    opt = event.pattern_match.group(1).strip()
    file = f"ultroid{sys.argv[-1]}.log" if len(sys.argv) > 1 else "ultroid.log"
    if opt == "heroku":
        await heroku_logs(event)
    elif opt == "carbon" and Carbon:
        event = await event.eor(get_string("com_1"))
        with open(file, "r") as f:
            code = f.read()[-2500:]
        file = await Carbon(
            file_name="ultroid-logs",
            code=code,
            backgroundColor=choice(ATRA_COL),
        )
        if isinstance(file, dict):
            await event.eor(f"`{file}`")
            return
        await event.reply("**Ultroid Logs.**", file=file)
    elif opt == "open":
        with open("ultroid.log", "r") as f:
            file = f.read()[-4000:]
        return await event.eor(f"`{file}`")
    elif (
        opt.isdigit() and 5 <= int(opt) <= 100
    ):  # Check if input is a number between 10 and 100
        num_lines = int(opt)
        with open("ultroid.log", "r") as f:
            lines = f.readlines()[-num_lines:]
            file = "".join(lines)
        return await event.eor(f"`{file}`")
    else:
        await def_logs(event, file)
    await event.try_delete()


@in_pattern("alive", owner=True)
async def inline_alive(ult):
    pic = udB.get_key("ALIVE_PIC")
    if isinstance(pic, list):
        pic = choice(pic)
    uptime = time_formatter((time.time() - start_time) * 1000)
    header = udB.get_key("ALIVE_TEXT") or get_string("bot_1")
    y = Repo().active_branch
    xx = Repo().remotes[0].config_reader.get("url")
    rep = xx.replace(".git", f"/tree/{y}")
    kk = f"<a href={rep}>{y}</a>"
    als = in_alive.format(
        header, f"{ultroid_version} [{HOSTED_ON}]", UltVer, pyver(), uptime, kk
    )

    if _e := udB.get_key("ALIVE_EMOJI"):
        als = als.replace("🌀", _e)
    builder = ult.builder
    if pic:
        try:
            if ".jpg" in pic:
                results = [
                    await builder.photo(
                        pic, text=als, parse_mode="html", buttons=buttons
                    )
                ]
            else:
                if _pic := resolve_bot_file_id(pic):
                    pic = _pic
                    buttons.insert(
                        0, [Button.inline(get_string("bot_2"), data="alive")]
                    )
                results = [
                    await builder.document(
                        pic,
                        title="Inline Alive",
                        description="@TeamUltroid",
                        parse_mode="html",
                        buttons=buttons,
                    )
                ]
            return await ult.answer(results)
        except BaseException as er:
            LOGS.exception(er)
    result = [
        await builder.article(
            "Alive", text=als, parse_mode="html", link_preview=False, buttons=buttons
        )
    ]
    await ult.answer(result)


@ultroid_cmd(pattern="setrepo( (.*)|$)")
async def set_repo(event):
    """
    Sets the upstream repository for updates.
    Usage: .setrepo <your_fork_url>
    """
    repo_url = event.pattern_match.group(2)
    if not repo_url:
        return await eor(event, "Please provide your forked repository URL. Example: `.setrepo https://github.com/user/repo`")
    if not repo_url.endswith(".git"):
        repo_url += ".git"
    udB.set_key("UPSTREAM_REPO", repo_url)
    await eor(event, f"Upstream repository has been set to: `{repo_url}`")


async def get_updates(ulttext, repo_url):
    """Checks for updates and returns repo, is_new, and changelog."""
    try:
        repo = Repo()
    except (InvalidGitRepositoryError, NoSuchPathError):
        await ulttext.edit(
            "`No .git directory found. Please re-clone Ultroid.`"
        )
        return None, False, None

    branch = repo.active_branch.name

    try:
        upstream_remote = repo.remote("upstream")
        upstream_remote.set_url(repo_url)
    except ValueError:
        upstream_remote = repo.create_remote("upstream", repo_url)

    try:
        await ulttext.edit(f"`Fetching updates from {repo_url}...`")
        upstream_remote.fetch(branch)
    except Exception as e:
        try:
            repo.delete_remote("upstream")
        except Exception as del_e:
            LOGS.error(f"Failed to delete remote 'upstream': {del_e}")
        await ulttext.edit(f"**Update failed!**\n\n**Error:**\n`{e}`")
        return None, False, None

    try:
        commits_behind = list(repo.iter_commits(f'{branch}..upstream/{branch}'))
    except Exception:
        commits_behind = [1]

    if not commits_behind:
        return repo, False, None

    changelog = f"**New updates are available for [{branch}]({repo_url.replace('.git', '')}/tree/{branch})!**\n\n**Changelog:**\n"
    for commit in repo.iter_commits(f'{branch}..upstream/{branch}'):
        changelog += f"  •  `{commit.summary}` by __{commit.author.name}__\n"

    return repo, True, changelog


def launch_update_script(repo_url=None):
    """Launch the external update script and shutdown the bot."""
    import subprocess
    import sys
    
    script_path = "update_script.py"
    
    # Prepare command arguments
    cmd = [sys.executable, script_path]
    if repo_url:
        cmd.append(repo_url)
    
    # Add original start arguments so the script knows how to restart
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    
    # Launch the update script
    subprocess.Popen(cmd, cwd=os.getcwd())
    
    # Shutdown the bot
    os._exit(0)


@ultroid_cmd(
    pattern="update(.*)",
    command="update",
    description="Update your Ultroid.",
)
async def updater(event):
    """Usage: {tr}update [now] [original]

Description: Checks for updates for your userbot.

• `{tr}update`: Checks for updates from your forked repo (if set), otherwise from original.
• `{tr}update now`: Forces an immediate update using external script from the configured repo.
• `{tr}update original`: Checks for updates from the official Ultroid repo.
• `{tr}update now original`: Forces an immediate update from the official Ultroid repo.

Note: Use `{tr}setrepo <your_fork_url>` to update from your own fork."""
    if Var.HEROKU_API:
        return await event.eor(
            "Heroku user! Please update from Heroku dashboard.",
        )

    ulttext = await event.eor("`Checking for updates, please wait...`")
    args = event.pattern_match.group(1).strip().split()
    is_now = "now" in args
    is_original = "original" in args

    repo_url = (
        "https://github.com/ThePrateekBhatia/Ultroid.git"
        if is_original
        else udB.get_key("UPSTREAM_REPO")
        or "https://github.com/overspend1/Ultroid-fork.git"
    )

    if is_now:
        # Use external script for immediate update
        await ulttext.edit(
            "🔄 **Starting update process...**\n\n"
            f"📦 Repository: `{repo_url}`\n"
            "⚡ Using external script for reliable update\n\n"
            "🤖 Bot will shutdown and restart automatically after update completes."
        )
        
        # Wait a moment for the message to be sent
        await asyncio.sleep(2)
        
        # Launch external update script and shutdown
        launch_update_script(repo_url)
        return

    # Regular update check (non-destructive)
    off_repo, is_new, changelog = await get_updates(ulttext, repo_url=repo_url)

    if not off_repo:
        return

    branch = off_repo.active_branch.name

    if is_new:
        # Show update available with options
        buttons = [
            [
                Button.inline("🔄 Update Now", data=f"update_now|{repo_url}"),
                Button.inline("📋 View Changes", data=f"update_changelog|{repo_url}"),
            ],
            [Button.inline("❌ Dismiss", data="close_update")],
        ]
        
        m = await asst.send_message(
            udB.get_key("LOG_CHANNEL"),
            f"🆕 **Update Available!**\n\n"
            f"📦 Repository: `{repo_url}`\n"
            f"🌿 Branch: `{branch}`\n\n"
            f"Use the buttons below to update or view changes.",
            buttons=buttons,
        )
        Link = m.message_link
        await ulttext.edit(
            f'**🆕 Update available!**\n\n'
            f'📦 Repository: `{repo_url.replace(".git", "")}`\n'
            f'🌿 Branch: `{branch}`\n\n'
            f'[📋 View Options & Update]({Link})',
            parse_mode="md",
            link_preview=False,
        )
    else:
        await ulttext.edit(
            f'✅ **Your bot is up-to-date!**\n\n'
            f'📦 Repository: `{repo_url.replace(".git", "")}`\n'
            f'🌿 Branch: `{branch}`',
            parse_mode="md",
            link_preview=False,
        )

    try:
        off_repo.delete_remote("upstream")
    except Exception:
        pass


@callback(re.compile(b"update_now\\|(.*)"))
async def update_now_callback(event):
    repo_url = event.data_match.group(1).decode("utf-8")
    await event.edit(
        "🔄 **Starting update process...**\n\n"
        f"📦 Repository: `{repo_url}`\n"
        "⚡ Using external script for reliable update\n\n"
        "🤖 Bot will shutdown and restart automatically after update completes."
    )
    
    # Wait a moment for the message to be sent
    await asyncio.sleep(2)
    
    # Launch external update script and shutdown
    launch_update_script(repo_url)


@callback(re.compile(b"update_changelog\\|(.*)"))
async def update_changelog_callback(event):
    repo_url = event.data_match.group(1).decode("utf-8")
    
    # Get changelog
    try:
        repo = Repo()
        branch = repo.active_branch.name
        
        # Set up upstream remote
        try:
            upstream_remote = repo.remote("upstream")
            upstream_remote.set_url(repo_url)
        except ValueError:
            upstream_remote = repo.create_remote("upstream", repo_url)
        
        # Fetch updates
        upstream_remote.fetch(branch)
        
        # Generate changelog
        changelog = f"**📋 Changelog for [{branch}]({repo_url.replace('.git', '')}/tree/{branch})**\n\n"
        for commit in repo.iter_commits(f'{branch}..upstream/{branch}'):
            changelog += f"• `{commit.summary}` by __{commit.author.name}__\n"
        
        # Cleanup
        repo.delete_remote("upstream")
        
        await event.edit(
            changelog,
            buttons=[
                [Button.inline("🔄 Update Now", data=f"update_now|{repo_url}")],
                [Button.inline("❌ Close", data="close_update")],
            ],
        )
    except Exception as e:
        await event.edit(f"**Error getting changelog:**\n`{e}`")


@callback("close_update")
async def close_update_callback(event):
    await event.delete()
