# https://github.com/1Danish-00/CompressorQueue/blob/main/License> .

import logging
import asyncio
import glob
import inspect
import io
import itertools
import json
import math
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import traceback
from datetime import datetime as dt
from logging import DEBUG, INFO, basicConfig, getLogger, warning
from logging.handlers import RotatingFileHandler
from pathlib import Path
import aiohttp
import psutil
from telethon import Button, TelegramClient, errors, events, functions, types
from telethon.sessions import StringSession
from telethon.utils import pack_bot_file_id
from telethon.network import MTProtoSender
from .config import *
import socket

# Enable tracemalloc for better error tracking
import tracemalloc
tracemalloc.start()

# Optimize socket buffer size
socket.SO_RCVBUF = 1024 * 1024 * 2  # 2MB receive buffer
socket.SO_SNDBUF = 1024 * 1024 * 2  # 2MB send buffer

# Enable TCP keep-alive
socket_options = [
    (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
    (socket.SOL_TCP, socket.TCP_NODELAY, 1),
]

try:
    import uvloop
    uvloop.install()
    LOGS.info("uvloop installed successfully")
except ImportError:
    LOGS.info("uvloop not available")

# Setup logging with absolute path
LOG_FILE_NAME = os.path.join(os.getcwd(), "TG-videoCompress@Log.txt")

# Initialize log file
if not os.path.exists(LOG_FILE_NAME):
    with open(LOG_FILE_NAME, "w") as f:
        f.write("")
elif os.path.exists(LOG_FILE_NAME):
    with open(LOG_FILE_NAME, "r+") as f_d:
        f_d.truncate(0)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=1024 * 1024 * 2,  # 2 MB
            backupCount=5,
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)

logging.getLogger("FastTelethon").setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.INFO)
LOGS = logging.getLogger(__name__)

# Add connection retry logic
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Add download retry configuration
DOWNLOAD_RETRIES = 3
CHUNK_SIZE = 524288  # 512KB chunks

class RetryingMTProtoSender(MTProtoSender):
    async def _send(self, *args, **kwargs):
        last_error = None
        for retry in range(DOWNLOAD_RETRIES):
            try:
                return await super()._send(*args, **kwargs)
            except (errors.FloodWaitError, errors.ServerError) as e:
                last_error = e
                if retry == DOWNLOAD_RETRIES - 1:
                    raise last_error
                wait_time = getattr(e, 'seconds', 1)
                await asyncio.sleep(wait_time)
                continue
            except Exception as e:
                raise e

# Use the custom sender
MTProtoSender = RetryingMTProtoSender

# Initialize bot
try:
    bot = TelegramClient(None, APP_ID, API_HASH)
except Exception as e:
    LOGS.info("Environment vars are missing! Kindly recheck.")
    LOGS.info("Bot is quiting...")
    LOGS.info(str(e))
    exit()

# Add error handler
@bot.on(events.MessageEdited)
async def handle_edited_message(event):
    try:
        await event.respond(event.text)
    except Exception as e:
        LOGS.error(f"Edit handler error: {str(e)}")

# Improve coroutine handling
async def safe_reply(event, text):
    try:
        return await event.reply(text)
    except Exception as e:
        LOGS.error(f"Reply error: {str(e)}")
        return None

try:
    bot = TelegramClient(None, APP_ID, API_HASH)
except Exception as e:
    LOGS.info("Environment vars are missing! Kindly recheck.")
    LOGS.info("Bot is quiting...")
    LOGS.info(str(e))
    exit()
