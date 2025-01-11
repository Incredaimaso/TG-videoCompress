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
    format='[%(levelname)s] %(asctime)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

LOGS = logging.getLogger(__name__)

# Simplified retry logic
MAX_RETRIES = 2
CHUNK_SIZE = 1024 * 1024  # 1MB chunks

class RetryingMTProtoSender(MTProtoSender):
    async def _send(self, *args, **kwargs):
        for retry in range(MAX_RETRIES):
            try:
                return await super()._send(*args, **kwargs)
            except (errors.FloodWaitError, errors.ServerError) as e:
                if retry == MAX_RETRIES - 1:
                    raise
                await asyncio.sleep(1)
                continue

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
