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

LOG_FILE_NAME = "TG-videoCompress@Log.txt"

if os.path.exists(LOG_FILE_NAME):
    with open(LOG_FILE_NAME, "r+") as f_d:
        f_d.truncate(0)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=2097152000,
            backupCount=10
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

class RetryingMTProtoSender(MTProtoSender):
    async def _send(self, *args, **kwargs):
        for retry in range(MAX_RETRIES):
            try:
                return await super()._send(*args, **kwargs)
            except (errors.FloodWaitError, errors.ServerError) as e:
                if retry == MAX_RETRIES - 1:
                    raise
                wait_time = getattr(e, 'seconds', RETRY_DELAY)
                await asyncio.sleep(wait_time)
                continue

# Use the custom sender
MTProtoSender = RetryingMTProtoSender

try:
    bot = TelegramClient(None, APP_ID, API_HASH)
except Exception as e:
    LOGS.info("Environment vars are missing! Kindly recheck.")
    LOGS.info("Bot is quiting...")
    LOGS.info(str(e))
    exit()
