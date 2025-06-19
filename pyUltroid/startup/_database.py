# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import ast
import os
import sys

from .. import run_as_module
from . import *

if run_as_module:
    from ..configs import Var


Redis = MongoClient = psycopg2 = Database = None
if Var.REDIS_URI or Var.REDISHOST:
    try:
        from redis import Redis
    except ImportError:
        LOGS.info("Installing 'redis' for database.")
        os.system(f"{sys.executable} -m pip install -q redis hiredis")
        from redis import Redis
elif Var.MONGO_URI:
    try:
        from pymongo import MongoClient
    except ImportError:
        LOGS.info("Installing 'pymongo' for database.")
        os.system(f"{sys.executable} -m pip install -q pymongo[srv]")
        from pymongo import MongoClient
elif Var.DATABASE_URL:
    try:
        import psycopg2
    except ImportError:
        LOGS.info("Installing 'pyscopg2' for database.")
        os.system(f"{sys.executable} -m pip install -q psycopg2-binary")
        import psycopg2
else:
    try:
        from localdb import Database
    except ImportError:
        LOGS.info("Using local file as database.")
        os.system(f"{sys.executable} -m pip install -q localdb.json")
        from localdb import Database

# --------------------------------------------------------------------------------------------- #


class _BaseDatabase:
    def __init__(self): # Removed *args, **kwargs as they are not used by super() calls in subclasses
        self._cache = {}

    def get_key(self, key):
        if key in self._cache:
            return self._cache[key]
        value = self._get_data(key)
        self._cache.update({key: value})
        return value

    def re_cache(self):
        self._cache.clear()
        for key in self.keys():
            self._cache.update({key: self.get_key(key)})

    def ping(self):
        return 1

    @property
    def usage(self):
        return 0

    def keys(self):
        return []

    def del_key(self, key):
        if key in self._cache:
            del self._cache[key]
        self.delete(str(key)) # pylint: disable=no-member # Implemented in subclasses
        return True

    def _get_data(self, key=None, data=None):
        if key:
            data = self.get(str(key)) # pylint: disable=no-member # Implemented in subclasses
        if data and isinstance(data, str):
            try:
                data = ast.literal_eval(data)
            except (ValueError, SyntaxError, TypeError): # More specific exceptions for literal_eval
                pass # Keep data as string if eval fails
        return data

    def set_key(self, key, value, cache_only=False):
        value = self._get_data(data=value) # Process value first
        self._cache[key] = value
        if cache_only:
            return True # Return True for consistency
        return self.set(str(key), str(value)) # pylint: disable=no-member # Implemented in subclasses

    def rename(self, key1, key2):
        _ = self.get_key(key1) # Relies on get_key which uses self.get
        if _:
            self.del_key(key1)
            self.set_key(key2, _)
            return 0
        return 1


class MongoDB(_BaseDatabase):
    def __init__(self, key, dbname="UltroidDB"):
        self.dB = MongoClient(key, serverSelectionTimeoutMS=5000)
        self.db = self.dB[dbname]
        super().__init__()

    def __repr__(self):
        return f"<Ultroid.MonGoDB\n -total_keys: {len(self.keys())}\n>"

    @property
    def name(self):
        return "Mongo"

    @property
    def usage(self):
        return self.db.command("dbstats")["dataSize"]

    def ping(self):
        if self.dB.server_info():
            return True

    def keys(self):
        return self.db.list_collection_names()

    def set(self, key, value):
        if key in self.keys():
            self.db[key].replace_one({"_id": key}, {"value": str(value)})
        else:
            self.db[key].insert_one({"_id": key, "value": str(value)})
        return True

    def delete(self, key):
        self.db.drop_collection(key)

    def get(self, key):
        if x := self.db[key].find_one({"_id": key}):
            return x["value"]

    def flushall(self):
        self.dB.drop_database("UltroidDB")
        self._cache.clear()
        return True


# --------------------------------------------------------------------------------------------- #

# Thanks to "Akash Pattnaik" / @BLUE-DEVIL1134
# for SQL Implementation in Ultroid.
#
# Please use https://elephantsql.com/ !


class SqlDB(_BaseDatabase):
    def __init__(self, url):
        self._url = url
        self._connection = None
        self._cursor = None
        try:
            self._connection = psycopg2.connect(dsn=url)
            self._connection.autocommit = True
            self._cursor = self._connection.cursor()
            self._cursor.execute(
                "CREATE TABLE IF NOT EXISTS Ultroid (ultroidCli varchar(70))"
            )
        except psycopg2.Error as error: # Use specific psycopg2 base error
            LOGS.error("SQL Database connection error: %s", error, exc_info=True)
            LOGS.info("Invalid SQL Database configuration.")
            if self._connection:
                self._connection.close()
            sys.exit()
        super().__init__()

    @property
    def name(self):
        return "SQL"

    @property
    def usage(self):
        self._cursor.execute(
            "SELECT pg_size_pretty(pg_relation_size('Ultroid')) AS size"
        )
        data = self._cursor.fetchall()
        return int(data[0][0].split()[0])

    def keys(self):
        self._cursor.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name  = 'ultroid'"
        )  # case sensitive
        data = self._cursor.fetchall()
        return [_[0] for _ in data]

    def get(self, variable):
        try:
            self._cursor.execute(f"SELECT {variable} FROM Ultroid") # Ensure variable is sanitized if it comes from user input
        except psycopg2.errors.UndefinedColumn: # pylint: disable=no-member
            return None
        data = self._cursor.fetchall()
        if not data:
            return None
        if len(data) >= 1:
            for i in data:
                if i[0]:
                    return i[0]

    def set(self, key, value):
        try:
            # Check if column exists before trying to drop, to avoid error if it doesn't
            self._cursor.execute(f"ALTER TABLE Ultroid DROP COLUMN IF EXISTS {key}")
        except psycopg2.errors.UndefinedColumn: # pylint: disable=no-member
            # Column doesn't exist, which is fine for ensuring it's dropped.
            pass
        except psycopg2.Error as er: # Catch specific psycopg2 errors
            LOGS.error("Error dropping column %s: %s", key, er, exc_info=True)
            # Depending on policy, may want to return False or raise
        # except psycopg2.errors.SyntaxError: # pylint: disable=no-member
        #     # This might indicate an issue with the key name (e.g. SQL injection if not careful)
        #     LOGS.error("Syntax error while trying to drop column %s.", key, exc_info=True)
        #     pass

        self._cache.update({key: value})
        self._cursor.execute(f"ALTER TABLE Ultroid ADD {key} TEXT")
        self._cursor.execute(f"INSERT INTO Ultroid ({key}) values (%s)", (str(value),))
        return True

    def delete(self, key):
        try:
            self._cursor.execute(f"ALTER TABLE Ultroid DROP COLUMN {key}")
        except psycopg2.errors.UndefinedColumn: # pylint: disable=no-member
            return False # Column didn't exist
        except psycopg2.Error as e_drop: # Other SQL errors
            LOGS.error("Error dropping column %s during delete: %s", key, e_drop)
            return False
        return True

    def flushall(self):
        self._cache.clear()
        self._cursor.execute("DROP TABLE Ultroid")
        self._cursor.execute(
            "CREATE TABLE IF NOT EXISTS Ultroid (ultroidCli varchar(70))"
        )
        return True


# --------------------------------------------------------------------------------------------- #


class RedisDB(_BaseDatabase):
    def __init__(
        self,
        host,
        port,
        password,
        *args, # Moved *args before keyword-only arguments
        platform="",
        logger=LOGS,
        **kwargs,
    ):
        effective_host = host
        effective_port = port
        effective_password = password

        if effective_host and ":" in effective_host:
            spli_ = effective_host.split(":")
            effective_host = spli_[0]
            try:
                effective_port = int(spli_[-1])
            except ValueError:
                logger.error("Invalid port in REDIS_URI: %s", spli_[-1])
                sys.exit(1)

            if effective_host.startswith("http"): # http(s) scheme is not for direct Redis connection string
                logger.error("Your REDIS_URI (host part) should not start with http(s)://. Use only hostname/IP.")
                sys.exit(1)
        elif not effective_host or not effective_port: # Port might be part of URI or separate
             # If REDIS_URI is `redis://user:pass@host:port` then host, port, password are parsed by redis-py itself if full URI is passed.
             # This logic seems to be for when they are passed as separate Var components.
            pass # Allow redis-py to handle it if full URI is passed to Redis() later

        # Qovery specific logic
        # The `and not host` condition in original code for Qovery block seems problematic if host was already parsed from REDIS_URI.
        # This block should ideally run if platform is qovery AND specific Qovery ENV vars are present, potentially overriding others.
        if platform.lower() == "qovery": # Simpler condition: if on Qovery, try to use Qovery vars.
            qovery_redis_host = None
            qovery_hash = ""
            for var_name in os.environ:
                if var_name.startswith("QOVERY_REDIS_") and var_name.endswith("_HOST"):
                    qovery_hash = var_name.split("_", maxsplit=2)[1].split("_")[0] # Extract HASH part
                    qovery_redis_host = os.environ.get(var_name)
                    break # Found one, assume it's the one to use

            if qovery_redis_host and qovery_hash:
                logger.info("Qovery environment detected, using Qovery Redis ENV vars.")
                effective_host = qovery_redis_host
                effective_port = int(os.environ.get(f"QOVERY_REDIS_{qovery_hash}_PORT", effective_port)) # Keep original if not found
                effective_password = os.environ.get(f"QOVERY_REDIS_{qovery_hash}_PASSWORD", effective_password)
            # Removed `if True:` block as it was unconditional. Logic now driven by qovery_redis_host and qovery_hash.

        # Construct connection_kwargs for Redis
        connection_kwargs = kwargs # Start with user-passed kwargs
        if effective_host: # Only override if we have a host (from Var or Qovery)
            connection_kwargs["host"] = effective_host
        if effective_port:
            connection_kwargs["port"] = int(effective_port) # Ensure port is int
        if effective_password: # Only override if we have a password
            connection_kwargs["password"] = effective_password

        # If Var.REDIS_URI is a full URI string, redis-py can parse it directly.
        # This logic assumes separate host/port/pass might be primary, or Qovery overrides.
        # If Var.REDIS_URI is the primary source and is a full URI, this might be simpler.
        # For now, respecting the structure that seems to prioritize individual components or Qovery.

        self.db = Redis(**connection_kwargs) # Pass all collected kwargs
        # Alias methods
        self.set = self.db.set # type: ignore
        self.get = self.db.get
        self.keys = self.db.keys
        self.delete = self.db.delete
        super().__init__()

    @property
    def name(self):
        return "Redis"

    @property
    def usage(self):
        return sum(self.db.memory_usage(x) for x in self.keys())


# --------------------------------------------------------------------------------------------- #


class LocalDB(_BaseDatabase):
    def __init__(self):
        self.db = Database("ultroid")
        self.get = self.db.get
        self.set = self.db.set
        self.delete = self.db.delete
        super().__init__()

    @property
    def name(self):
        return "LocalDB"

    def keys(self):
        return self._cache.keys()

    def __repr__(self):
        return f"<Ultroid.LocalDB\n -total_keys: {len(self.keys())}\n>"


def UltroidDB():
    _er = False
    from .. import HOSTED_ON

    try:
        if Redis:
            return RedisDB(
                host=Var.REDIS_URI or Var.REDISHOST,
                password=Var.REDIS_PASSWORD or Var.REDISPASSWORD,
                port=Var.REDISPORT,
                platform=HOSTED_ON,
                decode_responses=True,
                socket_timeout=5,
                retry_on_timeout=True,
            )
        elif MongoClient:
            return MongoDB(Var.MONGO_URI)
        elif psycopg2:
            return SqlDB(Var.DATABASE_URL)
        else:
            LOGS.critical(
                "No DB requirement fullfilled!\nPlease install redis, mongo or sql dependencies...\nTill then using local file as database."
            )
            return LocalDB()
    except Exception as err: # Changed from BaseException
        LOGS.error("Failed to initialize database: %s", err, exc_info=True)
    # exit() here is problematic as it will stop the bot if any DB init fails.
    # Consider returning None or raising a specific custom error to be handled by main.
    # For now, keeping original exit() behavior.
    sys.exit("Database initialization failed.")


# --------------------------------------------------------------------------------------------- #
