#    This file is part of the Compressor distribution.
#    Copyright (c) 2021 Danish_00
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3.
#
#    This program is distributed in the hope that it will be useful, but
#    WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#    General Public License for more details.
#
# License can be found in <
# https://github.com/1Danish-00/CompressorQueue/blob/main/License> .

from decouple import config
import logging

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                   level=logging.INFO)
LOGS = logging.getLogger(__name__)

try:
    APP_ID = config("APP_ID", cast=int)
    API_HASH = config("API_HASH")
    BOT_TOKEN = config("BOT_TOKEN")
    DEV = 1287276743
    OWNER = config("OWNER")
    ffmpegcode = ["-preset faster -c:v libx265 -s 854x480 -x265-params 'bframes=8:psy-rd=1:ref=3:aq-mode=3:aq-strength=0.8:deblock=1,1' -metadata 'title=Encoded By AnshuSharma (https://github.com/Anshusharma75/TG-videoCompress)' -pix_fmt yuv420p -crf 30 -c:a libopus -b:a 32k -c:s copy -map 0 -ac 2 -ab 32k -vbr 2 -level 3.1 -threads 1"]
    THUMB = config("THUMBNAIL")
    FFMPEG_PRESETS = {
        "480p": "-preset fast -c:v libx265 -s 854x480 -x265-params 'bframes=2:ref=2:aq-mode=1:aq-strength=0.6:deblock=-1,-1' -metadata title='Encoded By @Anime_Piras' -pix_fmt yuv420p -crf 35 -c:a aac -b:a 96k -c:s copy -map 0 -ac 2 -level 3.1 -threads 4",
        "720p": "-preset fast -c:v libx265 -s 1280x720 -x265-params 'bframes=3:ref=2:aq-mode=1:aq-strength=0.7:deblock=-1,-1' -metadata title='Encoded By @Anime_Piras' -pix_fmt yuv420p -crf 32 -c:a aac -b:a 128k -c:s copy -map 0 -ac 2 -level 4.0 -threads 4",
        "1080p": "-preset fast -c:v libx265 -s 1920x1080 -x265-params 'bframes=4:ref=3:aq-mode=1:aq-strength=0.8:deblock=-1,-1' -metadata title='Encoded By @Anime_Piras' -pix_fmt yuv420p -crf 30 -c:a aac -b:a 160k -c:s copy -map 0 -ac 2 -level 4.1 -threads 4"
    }
    DEFAULT_PRESET = "-c:v libx265 -preset medium -crf 28 -c:a copy -c:s copy"
    CACHE_DIR = "downloads/cache"
    WATERMARK_FILE = "watermark.png"  # Add your watermark image in bot directory
except Exception as e:
    LOGS.info("Environment vars Missing")
    LOGS.info("something went wrong")
    LOGS.info(str(e))
    exit(1)
