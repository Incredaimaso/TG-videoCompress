#    This file is part of the CompressorQueue distribution.
#    Copyright (c) 2021 Danish_00
#    Script Improved by Anshusharma


from . import *
from .config import *
from .worker import *
from asyncio import create_subprocess_shell as asyncrunapp
from asyncio.subprocess import PIPE as asyncPIPE
import psutil, os, signal
from bot import ffmpegcode, LOG_FILE_NAME

WORKING = []
QUEUE = {}
OK = {}
uptime = dt.now()

# Create required directories
for directory in ["downloads", "encode", "thumb"]:
    if not os.path.isdir(directory):
        os.makedirs(directory)

# Initialize default thumbnail
def init_thumbnail():
    try:
        # Check if thumbnail exists
        if not os.path.exists("thumb.jpg"):
            # Try downloading from URL
            if THUMB and THUMB.strip():
                os.system(f"wget {THUMB} -O thumb.jpg")
            
            # If download fails or no URL, create blank thumbnail
            if not os.path.exists("thumb.jpg") or os.path.getsize("thumb.jpg") == 0:
                # Create a 1x1 pixel black image as fallback
                os.system("convert -size 1x1 xc:black thumb.jpg")
                LOGS.warning("Created blank thumbnail as fallback")
    except Exception as e:
        LOGS.error(f"Thumbnail initialization error: {str(e)}")
        # Ensure a blank thumbnail exists
        if not os.path.exists("thumb.jpg"):
            os.system("convert -size 1x1 xc:black thumb.jpg")

# Initialize thumbnail
init_thumbnail()


def stdr(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if len(str(minutes)) == 1:
        minutes = "0" + str(minutes)
    if len(str(hours)) == 1:
        hours = "0" + str(hours)
    if len(str(seconds)) == 1:
        seconds = "0" + str(seconds)
    dur = (
        ((str(hours) + ":") if hours else "00:")
        + ((str(minutes) + ":") if minutes else "00:")
        + ((str(seconds)) if seconds else "")
    )
    return dur


def ts(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + "d, ") if days else "")
        + ((str(hours) + "h, ") if hours else "")
        + ((str(minutes) + "m, ") if minutes else "")
        + ((str(seconds) + "s, ") if seconds else "")
        + ((str(milliseconds) + "ms, ") if milliseconds else "")
    )
    return tmp[:-2]


def hbs(size):
    if not size:
        return ""
    power = 2 ** 10
    raised_to_pow = 0
    dict_power_n = {0: "B", 1: "K", 2: "M", 3: "G", 4: "T", 5: "P"}
    while size > power:
        size /= power
        raised_to_pow += 1
    return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"


async def progress(current, total, event, start, type_of_ps, file=None):
    now = time.time()
    diff = now - start
    if round(diff % 2.00) == 0 or current == total:  # Changed from 4.00 to 2.00 seconds
        percentage = current * 100 / total
        speed = current / diff
        time_to_completion = round((total - current) / speed) * 1000
        progress_str = "{0}{1}** {2}%**\n\n".format(
            "".join(["●" for i in range(math.floor(percentage / 10))]),
            "".join(["○" for i in range(10 - math.floor(percentage / 10))]),
            round(percentage, 2),
        )
        tmp = (
            progress_str
            + "** Progress:** {0} \n\n** Total Size:** {1}\n\n** Speed:** {2}/s\n\n** Time Left:** {3}\n".format(
                hbs(current),
                hbs(total),
                hbs(speed),
                ts(time_to_completion),
            )
        )
        try:
            if file:
                await event.edit(
                    "{}\n\nFile Name: {}\n\n{}".format(type_of_ps, file, tmp)
                )
            else:
                await event.edit("{}\n\n{}".format(type_of_ps, tmp))
        except Exception as e:
            LOGS.info(str(e))


async def test(event):
    try:
        zylern = "speedtest --simple"
        fetch = await asyncrunapp(
            zylern,
            stdout=asyncPIPE,
            stderr=asyncPIPE,
        )
        stdout, stderr = await fetch.communicate()
        result = str(stdout.decode().strip()) \
            + str(stderr.decode().strip())
        await event.reply("**" + result + "**")
    except FileNotFoundError:
        await event.reply("**Install speedtest-cli**")


async def sysinfo(event):
    try:
        # Use a more basic system info command since neofetch might not be available
        cmd = "uname -a && df -h && free -h"
        fetch = await asyncrunapp(
            cmd,
            stdout=asyncPIPE,
            stderr=asyncPIPE,
            shell=True
        )
        stdout, stderr = await fetch.communicate()
        result = str(stdout.decode().strip()) \
            + str(stderr.decode().strip())
        await event.reply("**System Information:**\n\n" + result)
    except Exception as e:
        await event.reply(f"**Error:**\n`{str(e)}`")


# Remove the info function since we won't be using mediainfo
# async def info(file, event):
#     ...


def code(data):
    OK.update({len(OK): data})
    return str(len(OK) - 1)


def decode(key):
    if OK.get(int(key)):
        return OK[int(key)]
    return


async def skip(e):
    wah = e.pattern_match.group(1).decode("UTF-8")
    wh = decode(wah)
    out, dl, id = wh.split(";")
    try:
        if QUEUE.get(int(id)):
            WORKING.clear()
            QUEUE.pop(int(id))
        await e.delete()
        os.system("rm -rf downloads/*")
        os.system("rm -rf encode/*")
        for proc in psutil.process_iter():
            processName = proc.name()
            processID = proc.pid
            print(processName , ' - ', processID)
            if(processName == "ffmpeg"):
             os.kill(processID,signal.SIGKILL)
    except BaseException:
        pass
    return


async def renew(e):
    if str(e.sender_id) not in OWNER and e.sender_id !=DEV:
        return
    await e.reply("**Cleared Queued, Working Files and Cached Downloads!**")
    WORKING.clear()
    QUEUE.clear()
    os.system("rm -rf downloads/*")
    os.system("rm -rf encode/*")
    for proc in psutil.process_iter():
        processName = proc.name()
        processID = proc.pid
        print(processName , ' - ', processID)
        if (processName == "ffmpeg"):
         os.kill (processID,signal.SIGKILL)
    return


async def coding(e):
    if str(e.sender_id) not in OWNER and e.sender_id !=DEV:
        return
    ffmpeg = e.text.split(" ", maxsplit=1)[1]
    ffmpegcode.clear()
    ffmpegcode.insert(0, f"""{ffmpeg}""")
    await e.reply(f"**Changed FFMPEG Code to**\n\n`{ffmpeg}`")
    return


async def getlogs(e):
    if str(e.sender_id) not in OWNER and e.sender_id != DEV:
        return
    try:
        with open(LOG_FILE_NAME, 'r') as file:
            log_content = file.read()
            if len(log_content) > 4000:
                # If log is too long, send as file
                with open(LOG_FILE_NAME, 'rb') as doc:
                    await e.client.send_file(
                        e.chat_id,
                        doc,
                        caption="**Bot Logs**",
                        force_document=True
                    )
            else:
                await e.reply(f"**Bot Logs:**\n\n```{log_content}```")
    except Exception as er:
        await e.reply(f"**Error getting logs:**\n\n`{str(er)}`")


async def getthumb(e):
    if str(e.sender_id) not in OWNER and e.sender_id !=DEV:
        return
    try:
        if os.path.exists("thumb.jpg"):
            await e.client.send_file(
                e.chat_id, 
                file="thumb.jpg",
                force_document=False, 
                caption="**Your Current Thumbnail.**"
            )
        else:
            await e.reply("**No thumbnail found. Send a photo to set it.**")
    except Exception as er:
        LOGS.info(f"Error sending thumbnail: {str(er)}")
        await e.reply(f"**Error getting thumbnail:**\n\n`{str(er)}`")


async def getcode(e):
    if str(e.sender_id) not in OWNER and e.sender_id !=DEV:
        return
    await e.reply(f"**Your Current FFMPEG Code is**\n\n`{ffmpegcode[0]}`")
    return


async def clearqueue(e):
    if str(e.sender_id) not in OWNER and e.sender_id !=DEV:
        return
    await e.reply("**Cleared Queued Files!**")
    QUEUE.clear()
    return


async def fast_download(e, download_url, filename=None):
    def progress_callback(d, t):
        return (
            asyncio.get_event_loop().create_task(
                progress(
                    d,
                    t,
                    e,
                    time.time(),
                    f"** Downloading video from {download_url}**",
                )
            ),
        )


    async def _maybe_await(value):
        if inspect.isawaitable(value):
            return await value
        else:
            return value


    async with aiohttp.ClientSession() as session:
        async with session.get(download_url, timeout=None) as response:
            if not filename:
                filename = download_url.rpartition("/")[-1]
            filename = os.path.join("downloads", filename)
            total_size = int(response.headers.get("content-length", 0)) or None
            downloaded_size = 0
            with open(filename, "wb") as f:
                async for chunk in response.content.iter_chunked(1024):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        await _maybe_await(
                            progress_callback(downloaded_size, total_size)
                        )
            return filename
