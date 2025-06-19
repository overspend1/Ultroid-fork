# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import asyncio
import os
import random
import shutil
import time
from random import randint

from ..configs import Var as UltroidConfigVars # Renamed for clarity

try:
    from pytz import timezone, exceptions as pytz_exceptions
except ImportError:
    timezone = None
    pytz_exceptions = None # Define if pytz not available

from telethon.errors import (
    ChannelsTooMuchError,
    ChatAdminRequiredError,
    MessageIdInvalidError,
    MessageNotModifiedError,
    UserNotParticipantError,
    # Specific RPC errors if known for some operations
    # e.g. rpcerrorlist.PhoneNumberInvalidError
)
from telethon.tl.custom import Button
from telethon.tl.functions.channels import (
    CreateChannelRequest,
    EditAdminRequest,
    EditPhotoRequest,
    InviteToChannelRequest,
)
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.contacts import UnblockRequest
from telethon.tl.types import (
    ChatAdminRights,
    ChatPhotoEmpty,
    InputChatUploadedPhoto,
    InputMessagesFilterDocument,
)
from telethon.utils import get_peer_id
from decouple import config as decouple_config, RepositoryEnv # Aliased decouple.config
from .. import LOGS, ULTConfig
from ..fns.helper import download_file, inline_mention, updater

db_url = 0 # Module level global


async def autoupdate_local_database():
    # Var here refers to the UltroidConfigVars instance if it's made global in __main__ or similar
    # Or it should be passed or accessed consistently.
    # Assuming Var is an instance of UltroidConfigVars accessible here.
    # For now, let's assume it's correctly accessed from `from .. import Var` if Var is an instance.
    # If `from .. import Var` actually imports the class, then this needs `ultroid_vars = UltroidConfigVars()`
    # For this fix, I'll assume `Var` is the instance for now, as per original structure.
    # If `Var` is the class, then `Var.TGDB_URL` would be an issue.
    # The `configs.py` defines Var as a class. So `Var.TGDB_URL` is indeed problematic.
    # This function is complex and relies on how Var, asst, udB, ultroid_bot are initialized and made available.
    # Let's use `decouple_config` for TGDB_URL for safety, assuming it's an env var.
    from .. import asst, udB, ultroid_bot, Var as GlobalUltroidConfig # Assuming this Var is the instance

    global db_url
    # Prioritize udB, then direct decouple_config, then cache
    # GlobalUltroidConfig.TGDB_URL isn't defined in configs.py.
    # This line was `udB.get_key("TGDB_URL") or Var.TGDB_URL or ultroid_bot._cache.get("TGDB_URL")`
    # Var.TGDB_URL is problematic.
    current_tgdb_url_env = decouple_config("TGDB_URL", default=None)
    db_url = (
        udB.get_key("TGDB_URL") or current_tgdb_url_env or ultroid_bot._cache.get("TGDB_URL")
    )

    if db_url:
        _split = db_url.split("/")
        if len(_split) > 2: # Basic check
            _channel = _split[-2]
            _id = _split[-1]
            try:
                await asst.edit_message(
                    int(_channel) if _channel.isdigit() else _channel,
                    message=int(_id), # message id should be int
                    file="database.json",
                    text="**Do not delete this file.**",
                )
            except MessageNotModifiedError:
                return
            except (MessageIdInvalidError, ValueError): # ValueError if _id is not int
                LOGS.warning("Invalid message ID or channel for TGDB_URL update: %s", db_url)
            except Exception as e_inner: # More specific Telethon errors if possible
                LOGS.error("Error editing TGDB message: %s", e_inner)
        else:
            LOGS.warning("Malformed TGDB_URL: %s", db_url)

    try:
        # Similar issue with Var.LOG_CHANNEL
        current_log_channel_env = decouple_config("LOG_CHANNEL", default=0, cast=int)
        log_channel_val = (
            udB.get_key("LOG_CHANNEL")
            or current_log_channel_env
            or asst._cache.get("LOG_CHANNEL")
            or "me"
        )
        # Ensure log_channel_val is int if it's a number string for user_id/chat_id
        if isinstance(log_channel_val, str) and log_channel_val.isdigit():
            log_channel_val = int(log_channel_val)
        elif isinstance(log_channel_val, str) and log_channel_val.startswith("-") and log_channel_val[1:].isdigit():
            log_channel_val = int(log_channel_val)


        msg = await asst.send_message(
            log_channel_val, "**Do not delete this file.**", file="database.json"
        )
        asst._cache["TGDB_URL"] = msg.message_link
        udB.set_key("TGDB_URL", msg.message_link)
    except Exception as ex: # Catch more specific errors if known (e.g., telethon RPC errors)
        LOGS.error("Error on autoupdate_local_database (sending new DB backup): %s", ex)


def update_envs():
    """Update Var attributes to udB"""
    from .. import udB

    _envs = [*list(os.environ)]
    if ".env" in os.listdir("."):
        # Original: RepositoryEnv(config._find_file('.')).data
        # decouple.config is now decouple_config. We need the original config object for _find_file
        # This is tricky because decouple.config is a function.
        # RepositoryEnv itself finds the .env file.
        try:
            env_data = RepositoryEnv(".env").data # Attempt to directly use RepositoryEnv
            for key_val_tuple in env_data: # RepositoryEnv.data is a list of tuples
                 _envs.append(key_val_tuple[0]) # Add only keys to _envs list for consistency
        except Exception as e:
            LOGS.warning("Could not read .env file for update_envs: %s", e)

    for env_name in _envs:
        # Check if this is one of the envs we care about syncing to udB
        if (
            env_name in ["LOG_CHANNEL", "BOT_TOKEN", "BOTMODE", "DUAL_MODE", "language"]
            or env_name in udB.keys() # Sync if it's already a key in udB
        ):
            # Prioritize os.environ, then decouple_config (which reads .env)
            _value = os.environ.get(env_name)
            if _value is None:
                _value = decouple_config(env_name, default=None) # Use decouple_config here

            if _value is not None: # Only set if we found a value
                udB.set_key(env_name, _value)
            # No else needed: if not in os.environ and not in .env (decouple_config returns None), don't change udB


async def startup_stuff():
    from .. import udB

    # Original: x = ["resources/auth", "resources/downloads"]
    # Original: for x in x: if not os.path.isdir(x): os.mkdir(x)
    # This was the E0602: Undefined variable 'x' because 'x' (the list) was overwritten by 'x' (the item)
    folder_paths = ["resources/auth", "resources/downloads"]
    for folder_path in folder_paths:
        if not os.path.isdir(folder_path):
            try:
                os.makedirs(folder_path, exist_ok=True) # Use makedirs for safety
            except OSError as e:
                LOGS.error("Failed to create directory %s: %s", folder_path, e)


    CT = udB.get_key("CUSTOM_THUMBNAIL")
    if CT:
        path = "resources/extras/thumbnail.jpg"
        ULTConfig.thumb = path
        try:
            await download_file(CT, path)
        except IOError as e: # More specific for file download issues
            LOGS.error("Failed to download custom thumbnail: %s", e)
        except Exception as er: # Catch other potential errors from download_file
            LOGS.error("Generic error downloading custom thumbnail: %s", er)
    elif CT is False:
        ULTConfig.thumb = None
    GT = udB.get_key("GDRIVE_AUTH_TOKEN")
    if GT:
        try:
            with open("resources/auth/gdrive_creds.json", "w", encoding="utf-8") as t_file:
                t_file.write(GT)
        except IOError as e:
            LOGS.error("Failed to write gdrive_creds.json: %s", e)


    if udB.get_key("AUTH_TOKEN"):
        udB.del_key("AUTH_TOKEN")

    MM = udB.get_key("MEGA_MAIL")
    MP = udB.get_key("MEGA_PASS")
    if MM and MP:
        try:
            with open(".megarc", "w", encoding="utf-8") as mega:
                mega.write(f"[Login]\nUsername = {MM}\nPassword = {MP}")
        except IOError as e:
            LOGS.error("Failed to write .megarc file: %s", e)

    TZ = udB.get_key("TIMEZONE")
    if TZ and timezone and pytz_exceptions: # Ensure pytz was imported
        try:
            timezone(TZ) # Validate timezone
            os.environ["TZ"] = TZ
            time.tzset()
        except pytz_exceptions.UnknownTimeZoneError: # Specific exception for timezone
            LOGS.error(
                "Incorrect Timezone '%s'. Check available timezones. Defaulting to UTC.", TZ
            )
            os.environ["TZ"] = "UTC"
            time.tzset()
        except AttributeError as er: # If timezone() call failed for other reasons
            LOGS.debug("AttributeError setting timezone: %s", er)
        # Removed broad BaseException catch here, be more specific if other errors occur
    elif not timezone and TZ :
        LOGS.warning("Timezone package (pytz) not available, cannot set timezone %s", TZ)


async def autobot():
    from .. import udB, ultroid_bot

    if udB.get_key("BOT_TOKEN"):
        return
    await ultroid_bot.start() # Assuming ultroid_bot is already connected if this is called
    LOGS.info("MAKING A TELEGRAM BOT FOR YOU AT @BotFather, Kindly Wait")
    who = ultroid_bot.me
    name = who.first_name + "'s Bot"
    if who.username:
        username = who.username + "_bot"
    else:
        username = "ultroid_" + (str(who.id))[5:] + "_bot"
    bf = "@BotFather"

    try:
        await ultroid_bot(UnblockRequest(bf))
        await ultroid_bot.send_message(bf, "/cancel")
        await asyncio.sleep(1) # Consider making delays configurable or shorter if possible
        await ultroid_bot.send_message(bf, "/newbot")
        await asyncio.sleep(1)
        isdone_msg = await ultroid_bot.get_messages(bf, limit=1)
        if not isdone_msg:
            LOGS.error("Failed to get response from BotFather after /newbot.")
            return # Or sys.exit as originally
        isdone = isdone_msg[0].text

        if isdone.startswith("That I cannot do.") or "20 bots" in isdone:
            LOGS.critical(
                "Please make a Bot from @BotFather and add its token in BOT_TOKEN, as an env var and restart me."
            )
            sys.exit(1) # Keep sys.exit for critical setup failures

        await ultroid_bot.send_message(bf, name)
        await asyncio.sleep(1)
        isdone_msg = await ultroid_bot.get_messages(bf, limit=1)
        if not isdone_msg:
            LOGS.error("Failed to get response from BotFather after sending bot name.")
            return
        isdone = isdone_msg[0].text

        if not isdone.startswith("Good."):
            await ultroid_bot.send_message(bf, "My Assistant Bot") # Fallback name
            await asyncio.sleep(1)
            isdone_msg = await ultroid_bot.get_messages(bf, limit=1)
            if not isdone_msg:
                LOGS.error("Failed to get response from BotFather after sending fallback name.")
                return
            isdone = isdone_msg[0].text
            if not isdone.startswith("Good."):
                LOGS.critical(
                    "Failed to set bot name. Please make a Bot from @BotFather and add its token in BOT_TOKEN."
                )
                sys.exit(1)

        await ultroid_bot.send_message(bf, username)
        await asyncio.sleep(1)
        isdone_msg = await ultroid_bot.get_messages(bf, limit=1)
        if not isdone_msg:
            LOGS.error("Failed to get response from BotFather after sending username.")
            return
        isdone = isdone_msg[0].text
        await ultroid_bot.send_read_acknowledge(bf) # Acknowledge BotFather's messages

        if isdone.startswith("Sorry,"): # Username taken
            ran = randint(1, 100)
            username = "ultroid_" + (str(who.id))[6:] + str(ran) + "_bot"
            await ultroid_bot.send_message(bf, username)
            await asyncio.sleep(1)
            isdone_msg = await ultroid_bot.get_messages(bf, limit=1)
            if not isdone_msg:
                LOGS.error("Failed to get response from BotFather after sending new username.")
                return
            isdone = isdone_msg[0].text

        if isdone.startswith("Done!"):
            try:
                token = isdone.split("`")[1]
                udB.set_key("BOT_TOKEN", token)
                await enable_inline(ultroid_bot, username)
                LOGS.info(
                    "Done. Successfully created @%s to be used as your assistant bot!", username
                )
            except IndexError:
                LOGS.error("Failed to parse token from BotFather's response: %s", isdone)
                sys.exit(1)
        else:
            LOGS.error(
                "Bot creation failed at BotFather with response: %s. "
                "Please delete some of your Telegram bots or set BOT_TOKEN manually.", isdone
            )
            sys.exit(1)
    except UserNotParticipantError: # Or other specific Telethon errors
        LOGS.error("BotFather interaction failed: UserNotParticipantError or similar. Is @BotFather blocked?")
    except Exception as e: # Catch-all for other unexpected errors during bot creation
        LOGS.error("An unexpected error occurred during autobot setup: %s", e, exc_info=True)
        # Consider if sys.exit is needed here or if the bot can continue without assistant.


async def autopilot():
    from .. import asst, udB, ultroid_bot

    channel_id_str = udB.get_key("LOG_CHANNEL")
    new_channel_created = False # Flag to track if we created the channel in this run
    chat = None

    if channel_id_str:
        try:
            # Ensure channel_id_str is correctly formatted for get_entity (int or specific string)
            if isinstance(channel_id_str, str) and (channel_id_str.isdigit() or (channel_id_str.startswith("-") and channel_id_str[1:].isdigit())):
                channel_entity_id = int(channel_id_str)
            else: # Assume it's a username or invite link if not purely numeric string
                channel_entity_id = channel_id_str
            chat = await ultroid_bot.get_entity(channel_entity_id)
            channel_id_str = get_peer_id(chat) # Normalize to peer ID
            udB.set_key("LOG_CHANNEL", str(channel_id_str)) # Save normalized ID
        except ValueError: # If channel_id_str is not a valid entity identifier
            LOGS.error("LOG_CHANNEL value '%s' is not a valid channel/chat ID or username.", channel_id_str)
            udB.del_key("LOG_CHANNEL")
            channel_id_str = None
        except Exception as err: # Catch other specific Telethon errors if possible
            LOGS.error("Error getting entity for LOG_CHANNEL %s: %s", channel_id_str, err, exc_info=False)
            udB.del_key("LOG_CHANNEL") # Invalidate problematic channel ID
            channel_id_str = None

    if not channel_id_str:
        async def _save_pm_fallback(exc_msg):
            # Fallback to PM if channel creation fails
            udB.set_key("LOG_CHANNEL", str(ultroid_bot.me.id)) # Use string for consistency
            await asst.send_message(
                ultroid_bot.me.id, f"Failed to Create/Verify Log Channel due to: {exc_msg}. Logging to PM."
            )

        if ultroid_bot._bot: # Assuming _bot means it's running in BOT_MODE
            msg_ = "'LOG_CHANNEL' not found! Add it in order to use 'BOTMODE'."
            LOGS.error(msg_)
            # In BOT_MODE, perhaps we shouldn't fallback to PM, or make it configurable.
            # For now, let's assume it should not create a channel in BOT_MODE if not set.
            return

        LOGS.info("Creating a Log Channel for You!")
        try:
            r = await ultroid_bot(
                CreateChannelRequest(
                    title="My Ultroid Logs",
                    about="My Ultroid Log Group\n\nJoin @TeamUltroid",
                    megagroup=True, # Creating a supergroup
                ),
            )
            chat = r.chats[0]
            channel_id_str = str(get_peer_id(chat)) # Store as string
            udB.set_key("LOG_CHANNEL", channel_id_str)
            new_channel_created = True
            LOGS.info("Successfully created new log channel: %s", channel_id_str)
        except ChannelsTooMuchError as er:
            LOGS.critical(
                "You are in too many channels & groups. Please leave some and restart the bot."
            )
            await _save_pm_fallback(str(er))
            return
        except Exception as er: # Catch other specific Telethon errors
            LOGS.error("Failed to create log channel: %s", er, exc_info=True)
            await _save_pm_fallback(str(er))
            return

    if not chat and channel_id_str : # If channel_id_str was from DB but chat object wasn't fetched
        try:
            chat = await ultroid_bot.get_entity(int(channel_id_str)) # Assuming it's an int ID by now
        except Exception as e:
            LOGS.error("Failed to get chat entity for existing LOG_CHANNEL %s: %s", channel_id_str, e)
            return # Cannot proceed without chat object

    if not chat:
        LOGS.error("Log channel setup failed, chat object is None.")
        return

    # Assistant invitation and promotion logic
    assistant_can_operate = True
    try:
        # get_permissions requires int channel ID
        await ultroid_bot.get_permissions(int(channel_id_str), asst.me.username)
    except UserNotParticipantError:
        LOGS.info("Assistant not in log channel. Inviting...")
        try:
            await ultroid_bot(InviteToChannelRequest(int(channel_id_str), [asst.me.username]))
        except Exception as er: # Catch specific errors like ChatAdminRequired, UserBlocked, etc.
            LOGS.error("Error inviting assistant to log channel: %s", er)
            assistant_can_operate = False
    except Exception as er:
        LOGS.error("Error checking assistant permissions in log channel: %s", er)
        assistant_can_operate = False

    if assistant_can_operate and new_channel_created: # Only try to promote if we just created it and assistant is in
        LOGS.info("Promoting assistant in newly created log channel...")
        try:
            # Ensure asst client has fetched the channel entity too
            await asst.get_entity(int(channel_id_str))

            rights = ChatAdminRights(
                add_admins=True, invite_users=True, change_info=True,
                ban_users=True, delete_messages=True, pin_messages=True,
                anonymous=False, manage_call=True,
            )
            await ultroid_bot(
                EditAdminRequest(int(channel_id_str), asst.me.username, rights, "Assistant")
            )
            LOGS.info("Successfully promoted assistant in log channel.")
        except ChatAdminRequiredError:
            LOGS.warning(
                "Failed to promote 'Assistant Bot' in 'Log Channel': Bot needs admin rights in the channel."
            )
        except Exception as er:
            LOGS.error("Error promoting assistant in log channel: %s", er, exc_info=True)

    # Set channel photo if it's new or has no photo
    if chat and isinstance(chat.photo, ChatPhotoEmpty):
        photo_path = None
        try:
            photo_url = "https://graph.org/file/27c6812becf6f376cbb10.jpg"
            photo_path, _ = await download_file(photo_url, "channelphoto.jpg")
            uploaded_photo_file = await ultroid_bot.upload_file(photo_path)
            await ultroid_bot(
                EditPhotoRequest(int(channel_id_str), InputChatUploadedPhoto(uploaded_photo_file))
            )
            LOGS.info("Successfully set photo for log channel.")
        except Exception as er: # Catch specific errors for download/upload/editphoto
            LOGS.error("Failed to set photo for log channel: %s", er)
        finally:
            if photo_path and os.path.exists(photo_path):
                os.remove(photo_path)


async def customize():
    from .. import asst, udB, ultroid_bot

    downloaded_profile_pic_path = None
    try:
        log_channel_id_str = udB.get_key("LOG_CHANNEL")
        if not log_channel_id_str:
            LOGS.warning("LOG_CHANNEL not found, cannot send customization status message.")
            # Decide if customization should proceed without a log channel or return.
            # For now, let's allow it to proceed but it won't be able to send status updates.

        if asst.me.photo: # Check if assistant already has a profile photo
            LOGS.info("Assistant bot already has a profile picture. Skipping customization of picture.")
            # Optionally, one could still update description/about text. For now, full skip.
            return

        LOGS.info("Customising Assistant Bot via @BotFather...")
        assistant_username_mention = f"@{asst.me.username}"
        master_mention = ultroid_bot.me.first_name
        if ultroid_bot.me.username:
            master_mention = f"@{ultroid_bot.me.username}"

        # Profile picture selection
        profile_pic_options = [
            "https://graph.org/file/92cd6dbd34b0d1d73a0da.jpg",
            "https://graph.org/file/a97973ee0425b523cdc28.jpg",
            "resources/extras/ultroid_assistant.jpg", # Local fallback
        ]
        chosen_pic_source = random.choice(profile_pic_options)

        if chosen_pic_source.startswith("http"):
            downloaded_profile_pic_path, _ = await download_file(chosen_pic_source, "profile_temp.jpg")
        elif os.path.exists(chosen_pic_source):
            downloaded_profile_pic_path = chosen_pic_source
        else:
            LOGS.warning("Selected profile picture source %s not found or inaccessible.", chosen_pic_source)
            downloaded_profile_pic_path = None # No picture will be set

        status_msg = None
        if log_channel_id_str:
            try:
                status_msg = await asst.send_message(
                    int(log_channel_id_str), "**Auto Customisation** initiated with @BotFather..."
                )
            except Exception as e_log:
                LOGS.warning("Failed to send initial customization status to log channel: %s", e_log)

        bot_father_handle = "BotFather" # Less prone to typos

        # Interaction with BotFather
        await ultroid_bot.send_message(bot_father_handle, "/cancel") # Start clean
        await asyncio.sleep(1)

        if downloaded_profile_pic_path:
            await ultroid_bot.send_message(bot_father_handle, "/setuserpic")
            await asyncio.sleep(1)
            # Add check for BotFather's response here if needed
            await ultroid_bot.send_message(bot_father_handle, assistant_username_mention)
            await asyncio.sleep(1)
            await ultroid_bot.send_file(bot_father_handle, downloaded_profile_pic_path)
            await asyncio.sleep(2) # Allow time for processing
            LOGS.info("Assistant profile picture updated.")

        # Set About Text
        await ultroid_bot.send_message(bot_father_handle, "/setabouttext")
        await asyncio.sleep(1)
        await ultroid_bot.send_message(bot_father_handle, assistant_username_mention)
        await asyncio.sleep(1)
        await ultroid_bot.send_message(
            bot_father_handle, f"✨ Hello ✨!! I'm Assistant Bot of {master_mention}"
        )
        await asyncio.sleep(2)
        LOGS.info("Assistant about text updated.")

        # Set Description
        await ultroid_bot.send_message(bot_father_handle, "/setdescription")
        await asyncio.sleep(1)
        await ultroid_bot.send_message(bot_father_handle, assistant_username_mention)
        await asyncio.sleep(1)
        await ultroid_bot.send_message(
            bot_father_handle,
            f"✨ Powerful Ultroid Assistant Bot ✨\n✨ Master ~ {master_mention} ✨\n\n✨ Powered By ~ @TeamUltroid ✨"
        )
        await asyncio.sleep(2)
        LOGS.info("Assistant description updated.")

        await ultroid_bot.send_read_acknowledge(bot_father_handle)

        if status_msg:
            await status_msg.edit("Completed **Auto Customisation** at @BotFather.")
        LOGS.info("Assistant bot customization complete.")

    except Exception as e: # Catch more specific Telethon errors if they occur often
        LOGS.error("Error during assistant customization: %s", e, exc_info=True)
        if status_msg:
            try:
                await status_msg.edit(f"Customization failed: {e}")
            except: pass # Ignore error editing status message
    finally:
        if downloaded_profile_pic_path and downloaded_profile_pic_path == "profile_temp.jpg" and os.path.exists(downloaded_profile_pic_path):
            os.remove(downloaded_profile_pic_path)


async def plug(plugin_channels):
    from .. import ultroid_bot
    from .utils import load_addons # Assuming this is correctly placed

    if ultroid_bot._bot: # Check if running in BOT_MODE
        LOGS.info("Plugin Channels can't be used in 'BOTMODE'. Skipping plugin loading from channels.")
        return

    # Ensure addons directory exists
    addons_dir = "addons"
    if os.path.exists(addons_dir) and not os.path.isdir(addons_dir):
        LOGS.error("'%s' exists but is not a directory. Cannot load addons.", addons_dir)
        return # Or attempt to remove/rename file and create dir
    if not os.path.exists(addons_dir):
        try:
            os.makedirs(addons_dir)
        except OSError as e:
            LOGS.error("Failed to create addons directory '%s': %s", addons_dir, e)
            return

    # Ensure addons/__init__.py exists
    addons_init_py = os.path.join(addons_dir, "__init__.py")
    if not os.path.exists(addons_init_py):
        try:
            with open(addons_init_py, "w", encoding="utf-8") as f:
                f.write("# This file makes Python treat the 'addons' directory as a package.\n")
                # The original content was "from plugins import *\n\nbot = ultroid_bot"
                # This wildcard import is generally discouraged.
                # If addons need access to `bot` or `plugins`, they should import them directly or be passed context.
                # For now, keeping it minimal. If addons rely on this, it's a deeper refactor.
                f.write("from .. import ultroid_bot as bot\n") # Make bot instance available if needed
                f.write("from ..plugins import *\n") # If addons truly need this, but it's a lot.
        except IOError as e:
            LOGS.error("Failed to create %s: %s", addons_init_py, e)
            # Decide if to proceed without it. Some loading mechanisms might fail.

    LOGS.info("• Loading Plugins from Plugin Channel(s) •")
    for channel_identifier in plugin_channels: # Renamed 'chat' to 'channel_identifier' for clarity
        LOGS.info("• • • • Processing channel: %s", channel_identifier)
        try:
            # Ensure channel_identifier is valid for get_entity
            if isinstance(channel_identifier, str) and (channel_identifier.isdigit() or \
               (channel_identifier.startswith("-") and channel_identifier[1:].isdigit())):
                entity = int(channel_identifier)
            else:
                entity = channel_identifier

            async for message_item in ultroid_bot.iter_messages(
                entity, search=".py", filter=InputMessagesFilterDocument, wait_time=10
            ):
                if not hasattr(message_item, 'file') or not message_item.file or not hasattr(message_item.file, 'name'):
                    LOGS.warning("Skipping message without valid file attribute or name in channel %s", channel_identifier)
                    continue

                # Sanitize plugin filename
                safe_filename = message_item.file.name.replace("_", "-").replace("|", "-").replace("/", "-").replace("\\", "-")
                plugin_path = os.path.join(addons_dir, safe_filename)

                if os.path.exists(plugin_path):
                    LOGS.info("Plugin %s already exists. Skipping download.", plugin_path)
                    continue # Or implement an update mechanism

                await asyncio.sleep(0.6) # Rate limiting?
                if message_item.text and message_item.text.strip() == "#IGNORE":
                    LOGS.info("Ignoring plugin %s as per #IGNORE tag.", safe_filename)
                    continue

                downloaded_path = None
                try:
                    downloaded_path = await message_item.download_media(file=plugin_path)
                    if downloaded_path:
                        LOGS.info("Downloaded plugin: %s", downloaded_path)
                        load_addons(downloaded_path) # Assuming load_addons handles its own exceptions for loading
                    else:
                        LOGS.error("Failed to download plugin %s from %s", safe_filename, channel_identifier)
                except Exception as load_err: # Catch errors from download or load_addons
                    LOGS.error("Error processing plugin %s from %s: %s", safe_filename, channel_identifier, load_err, exc_info=False)
                    if downloaded_path and os.path.exists(downloaded_path):
                        try:
                            os.remove(downloaded_path) # Clean up failed download
                        except OSError as e_rm:
                            LOGS.error("Failed to remove corrupted plugin %s: %s", downloaded_path, e_rm)
        except ValueError as ve:
            LOGS.error("Invalid channel identifier '%s' for plugin loading: %s", channel_identifier, ve)
        except Exception as er: # Catch errors like channel not found, permissions etc.
            LOGS.error("Error iterating messages in plugin channel %s: %s", channel_identifier, er, exc_info=True)


async def ready():
    from .. import asst, udB, ultroid_bot

    log_channel_id_str = udB.get_key("LOG_CHANNEL")
    log_channel_id = None
    if log_channel_id_str:
        try:
            log_channel_id = int(log_channel_id_str)
        except ValueError:
            LOGS.warning("LOG_CHANNEL ID '%s' is not an integer. Cannot send ready message.", log_channel_id_str)
            # Fallback to PM or skip? For now, skip if not valid int.
            log_channel_id = ultroid_bot.me.id # Fallback to self/PM

    spam_sent_msg = None
    photo_to_send = None
    buttons_to_send = None

    if not udB.get_key("INIT_DEPLOY"):  # Detailed Message at Initial Deploy
        msg_text = """🎇 **Thanks for Deploying Ultroid Userbot!**
• Here, are the Some Basic stuff from, where you can Know, about its Usage."""
        photo_to_send = "https://graph.org/file/54a917cc9dbb94733ea5f.jpg"
        buttons_to_send = Button.inline("• Click to Start •", "initft_2")
        udB.set_key("INIT_DEPLOY", "Done")
    else:
        msg_text = (
            f"**Ultroid has been deployed!**\n"
            f"➖➖➖➖➖➖➖➖➖➖\n"
            f"**UserMode**: {inline_mention(ultroid_bot.me)}\n"
            f"**Assistant**: @{asst.me.username}\n"
            f"➖➖➖➖➖➖➖➖➖➖\n"
            f"**Support**: @TeamUltroid\n"
            f"➖➖➖➖➖➖➖➖➖➖"
        )
        prev_spam_id = udB.get_key("LAST_UPDATE_LOG_SPAM")
        if prev_spam_id and log_channel_id:
            try:
                await ultroid_bot.delete_messages(log_channel_id, int(prev_spam_id))
            except Exception as e_del: # Catch specific errors like MessageDeleteForbiddenError
                LOGS.warning("Error deleting previous update message %s: %s", prev_spam_id, e_del)

        update_available = await updater() # Assuming updater() returns a boolean or relevant info
        if update_available: # This might need adjustment based on what updater() returns
            buttons_to_send = Button.inline("Update Available", "updtavail")

    if log_channel_id: # Only try to send if we have a valid log_channel_id
        try:
            spam_sent_msg = await asst.send_message(
                log_channel_id, msg_text, file=photo_to_send, buttons=buttons_to_send
            )
        except (ValueError, TypeError) as ve_te: # Catch errors if log_channel_id is invalid for sending
            LOGS.warning("Failed to send 'ready' message to LOG_CHANNEL %s (ValueError/TypeError): %s. Trying with main client to PM.", log_channel_id, ve_te)
            try: # Fallback to main client sending to self if assistant fails or channel invalid
                spam_sent_msg = await ultroid_bot.send_message(ultroid_bot.me.id, msg_text, file=photo_to_send, buttons=buttons_to_send)
            except Exception as e_fallback:
                LOGS.error("Fallback 'ready' message to PM also failed: %s", e_fallback)
        except Exception as e_send: # Catch other Telethon errors
            LOGS.error("Failed to send 'ready' message to LOG_CHANNEL %s: %s", log_channel_id, e_send)
            # Fallback to PM may also be useful here
            try:
                spam_sent_msg = await ultroid_bot.send_message(ultroid_bot.me.id, msg_text, file=photo_to_send, buttons=buttons_to_send)
            except Exception as e_fallback_pm:
                LOGS.error("Fallback 'ready' message to PM (after general error) also failed: %s", e_fallback_pm)


    if spam_sent_msg and not spam_sent_msg.media: # Only store ID if message sent and no media (or adjust logic)
        udB.set_key("LAST_UPDATE_LOG_SPAM", spam_sent_msg.id)

    try:
        await ultroid_bot(JoinChannelRequest("TheUltroid"))
        LOGS.info("Successfully joined @TheUltroid channel.")
    except Exception as er: # Catch specific errors like UserAlreadyParticipantError, ChannelsTooMuchError
        LOGS.warning("Could not join @TheUltroid channel: %s", er)


async def WasItRestart(udb):
    restart_key = udb.get_key("_RESTART")
    if not restart_key:
        return

    from .. import asst, ultroid_bot
    LOGS.info("Processing restart message confirmation...")
    try:
        data_parts = restart_key.split("_")
        if len(data_parts) < 3:
            LOGS.error("Invalid _RESTART key format: %s", restart_key)
            udb.del_key("_RESTART")
            return

        client_type, chat_id_str, msg_id_str = data_parts[0], data_parts[1], data_parts[2]

        chat_id = int(chat_id_str)
        msg_id = int(msg_id_str)

        target_client = asst if client_type == "bot" else ultroid_bot
        await target_client.edit_message(chat_id, msg_id, "__Restarted Successfully.__")
        LOGS.info("Successfully edited restart confirmation message.")
    except ValueError:
        LOGS.error("Invalid chat_id or msg_id in _RESTART key: %s", restart_key)
    except Exception as er: # Catch specific Telethon errors if possible
        LOGS.error("Failed to edit restart message: %s", er, exc_info=True)
    finally:
        udb.del_key("_RESTART") # Always remove the key


def _version_changes(udb):
    for _ in [
        "BOT_USERS",
        "BOT_BLS",
        "VC_SUDOS",
        "SUDOS",
        "CLEANCHAT",
        "LOGUSERS",
        "PLUGIN_CHANNEL",
        "CH_SOURCE",
        "CH_DESTINATION",
        "BROADCAST",
    ]:
        key = udb.get_key(_)
        if key and str(key)[0] != "[":
            key = udb.get(_)
            new_ = [
                int(z) if z.isdigit() or (z.startswith("-") and z[1:].isdigit()) else z
                for z in key.split()
            ]
            udb.set_key(_, new_)


async def enable_inline(ultroid_bot, username):
    bf = "BotFather"
    await ultroid_bot.send_message(bf, "/setinline")
    await asyncio.sleep(1)
    await ultroid_bot.send_message(bf, f"@{username}")
    await asyncio.sleep(1)
    await ultroid_bot.send_message(bf, "Search")
    await ultroid_bot.send_read_acknowledge(bf)
