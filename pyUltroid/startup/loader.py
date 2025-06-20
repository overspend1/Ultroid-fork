# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import os
import subprocess
import sys
from shutil import rmtree

from decouple import config
from git import Repo

from .. import *
from ..dB._core import HELP
from ..loader import Loader
from . import *
from .utils import load_addons


def _after_load(loader, module, plugin_name=""):
    if not module or plugin_name.startswith("_"):
        return
    from strings import get_help

    if doc_ := get_help(plugin_name) or module.__doc__:
        try:
            doc = doc_.format(i=HNDLR)
        except Exception as er: # Formatting can raise various errors, Exception is okay here.
            loader._logger.exception(er)
            loader._logger.info("Error in %s: %s", plugin_name, module)
            return
        if loader.key in HELP.keys():
            update_cmd = HELP[loader.key]
            try:
                update_cmd.update({plugin_name: doc})
            except Exception as er: # Changed from BaseException
                loader._logger.exception(er)
        else:
            try:
                HELP.update({loader.key: {plugin_name: doc}})
            except Exception as em: # Changed from BaseException
                loader._logger.exception(em)


def load_other_plugins(addons=None, pmbot=None, manager=None, vcbot=None):
    # for official
    _exclude = udB.get_key("EXCLUDE_OFFICIAL") or config("EXCLUDE_OFFICIAL", None)
    _exclude = _exclude.split() if _exclude else []

    # "INCLUDE_ONLY" was added to reduce Big List in "EXCLUDE_OFFICIAL" Plugin
    _in_only = udB.get_key("INCLUDE_ONLY") or config("INCLUDE_ONLY", None)
    _in_only = _in_only.split() if _in_only else []
    Loader().load(include=_in_only, exclude=_exclude, after_load=_after_load)

    # for assistant
    if not USER_MODE and not udB.get_key("DISABLE_AST_PLUGINS"):
        _ast_exc = ["pmbot"]
        if _in_only and "games" not in _in_only:
            _ast_exc.append("games")
        Loader(path="assistant").load(
            log=False, exclude=_ast_exc, after_load=_after_load
        )

    # for addons
    if addons:
        if url := udB.get_key("ADDONS_URL"):
            subprocess.run(f"git clone -q {url} addons", shell=True, check=True)
        if os.path.exists("addons") and not os.path.exists("addons/.git"):
            rmtree("addons") # This is a forceful removal, ensure it's intended.
        if not os.path.exists("addons"):
            try:
                branch_name = Repo().active_branch.name
                subprocess.run(
                    f"git clone -q -b {branch_name} https://github.com/TeamUltroid/UltroidAddons.git addons",
                    shell=True, check=True,
                )
            except Exception as e_git_clone: # Catch if Repo() or active_branch fails
                LOGS.warning("Could not determine active branch for cloning UltroidAddons, defaulting to main/master: %s", e_git_clone)
                subprocess.run(
                    "git clone -q https://github.com/TeamUltroid/UltroidAddons.git addons",
                    shell=True, check=True, # Default clone if specific branch fails
                )
        else: # addons directory exists
            if os.path.isdir("addons/.git"): # Only pull if it's a git repo
                subprocess.run("cd addons && git pull -q && cd ..", shell=True, check=True)
            else:
                LOGS.info("'addons' directory exists but is not a git repository. Skipping pull.")


        if not os.path.exists("addons"): # Should be created by one of the clones above if logic is right
             # This might be redundant if check=True causes exit on failure for previous commands.
            LOGS.info("Cloning default UltroidAddons as addons directory still not found.")
            subprocess.run(
                "git clone -q https://github.com/TeamUltroid/UltroidAddons.git addons",
                shell=True, check=True,
            )
        if os.path.exists("addons/addons.txt"):
            # generally addons req already there so it won't take much time
            LOGS.info("Installing requirements from addons/addons.txt")
            subprocess.run(
                f"{sys.executable} -m pip install --no-cache-dir -q -r ./addons/addons.txt",
                shell=True, check=True, # Added check=True
            )

        _exclude = udB.get_key("EXCLUDE_ADDONS")
        _exclude = _exclude.split() if _exclude else []
        _in_only = udB.get_key("INCLUDE_ADDONS")
        _in_only = _in_only.split() if _in_only else []

        Loader(path="addons", key="Addons").load(
            func=load_addons,
            include=_in_only,
            exclude=_exclude,
            after_load=_after_load,
            load_all=True,
        )

    if not USER_MODE:
        # group manager
        if manager:
            Loader(path="assistant/manager", key="Group Manager").load()

        # chat via assistant
        if pmbot:
            Loader(path="assistant/pmbot.py").load(log=False)

    # vc bot
    if vcbot and (vcClient and not vcClient.me.bot):
        try:
            import pytgcalls  # ignore: pylint

            if os.path.exists("vcbot"):
                if os.path.exists("vcbot/.git"):
                subprocess.run("cd vcbot && git pull -q", shell=True, check=True)
                else:
                rmtree("vcbot") # Forceful removal
            if not os.path.exists("vcbot"):
                subprocess.run(
                "git clone -q https://github.com/TeamUltroid/VcBot vcbot", shell=True, check=True
                )
            try:
                if not os.path.exists("vcbot/downloads"):
                os.makedirs("vcbot/downloads", exist_ok=True)
                Loader(path="vcbot", key="VCBot").load(after_load=_after_load)
            except FileNotFoundError as e:
            LOGS.error("%s Skipping VCBot Installation.", e)
        except ModuleNotFoundError:
            LOGS.error("'pytgcalls' not installed!\nSkipping loading of VCBOT.")
