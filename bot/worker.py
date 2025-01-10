#    This file is part of the CompressorQueue distribution.
#    Copyright (c) 2021 Danish_00
#    Script Improved by Anshusharma

import hashlib
from .FastTelethon import download_file, upload_file
from .funcn import *
from .config import *


async def stats(e):
    try:
        wah = e.pattern_match.group(1).decode("UTF-8")
        wh = decode(wah)
        out, dl, id = wh.split(";")
        ot = hbs(int(Path(out).stat().st_size))
        ov = hbs(int(Path(dl).stat().st_size))
        processing_file_name = dl.replace(f"downloads/", "").replace(f"_", " ")
        ans = f"Processing Media:\n{processing_file_name}\n\nDownloaded:\n{ov}\n\nCompressed:\n{ot}"
        await e.answer(ans, cache_time=0, alert=True)
    except Exception as er:
        LOGS.info(er)
        await e.answer(
            "Someting Went Wrong.\nSend Media Again.", cache_time=0, alert=True
        )


async def dl_link(event):
    if not event.is_private:
        return
    if str(event.sender_id) not in OWNER and event.sender_id !=DEV:
        return
    link, name = "", ""
    try:
        link = event.text.split()[1]
        name = event.text.split()[2]
    except BaseException:
        pass
    if not link:
        return
    if WORKING or QUEUE:
        QUEUE.update({link: name})
        return await event.reply(f"** Added {link} in QUEUE**")
    WORKING.append(1)
    s = dt.now()
    xxx = await event.reply("** Downloading...**")
    try:
        dl = await fast_download(xxx, link, name)
    except Exception as er:
        WORKING.clear()
        LOGS.info(er)
        return
    es = dt.now()
    kk = dl.split("/")[-1]
    aa = kk.split(".")[-1]
    newFile = dl.replace(f"downloads/", "").replace(f"_", " ")
    rr = "encode"
    bb = kk.replace(f".{aa}", ".mkv")
    out = f"{rr}/{bb}"
    thum = "thumb.jpg"
    dtime = ts(int((es - s).seconds) * 1000)
    hehe = f"{out};{dl};0"
    wah = code(hehe)
    nn = await xxx.edit(
        "**🗜 Compressing...\nPlease wait...**"
    )
    processing_file_name = newFile
    
    async def update_status():
        last_msg = ""
        while True:
            try:
                # Check for download file first
                if Path(dl).exists():
                    ov = hbs(int(Path(dl).stat().st_size))
                    cur_msg = f"**🗜 Compressing...**\n\nFile: {processing_file_name}\nDownloaded Size: {ov}\nCompressed: 0 B"
                    
                    # Then check for output file
                    if Path(out).exists():
                        ot = hbs(int(Path(out).stat().st_size))
                        ov = hbs(int(Path(dl).stat().st_size))
                        percentage = round((float(int(Path(out).stat().st_size)) / float(int(Path(dl).stat().st_size))) * 100, 2)
                        cur_msg = (
                            f"**🗜 Compressing: {percentage}%**\n\n"
                            f"File: {processing_file_name}\n"
                            f"Downloaded Size: {ov}\n"
                            f"Compressed Size: {ot}"
                        )
                    
                    # Only edit if message content has changed
                    if cur_msg != last_msg:
                        try:
                            await nn.edit(cur_msg)
                            last_msg = cur_msg
                        except Exception as e:
                            LOGS.info(f"Edit error: {str(e)}")
                    
                await asyncio.sleep(3)  # Increase sleep time to 3 seconds
                
            except Exception as e:
                LOGS.info(f"Update status error: {str(e)}")
                await asyncio.sleep(3)

    status_task = asyncio.create_task(update_status())
    
    cmd = f"""ffmpeg -i "{dl}" {ffmpegcode[0]} "{out}" -y"""
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    er = stderr.decode()
    try:
        status_task.cancel()  # Stop the status updates
    except:
        pass
    try:
        if er:
            await xxx.edit(str(er) + "\n\n**ERROR**")
            WORKING.clear()
            os.remove(dl)
            return os.remove(out)
    except BaseException:
        pass
    ees = dt.now()
    ttt = time.time()
    await nn.delete()
    nnn = await xxx.client.send_message(xxx.chat_id, "** Uploading...**")
    with open(out, "rb") as f:
        ok = await upload_file(
            client=xxx.client,
            file=f,
            name=out,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(d, t, nnn, ttt, "** Uploading...**")
            ),
        )
    await nnn.delete()
    org = int(Path(dl).stat().st_size)
    com = int(Path(out).stat().st_size)
    pe = 100 - ((com / org) * 100)
    per = str(f"{pe:.2f}") + "%"
    eees = dt.now()
    x = dtime
    xx = ts(int((ees - es).seconds) * 1000)
    xxx = ts(int((eees - ees).seconds) * 1000)
    dk = f"<b>File Name:</b> {newFile}\n\n<b>Original File Size:</b> {hbs(org)}\n<b>Encoded File Size:</b> {hbs(com)}\n<b>Encoded Percentage:</b> {per}\n\n<i>Downloaded in {x}\nEncoded in {xx}\nUploaded in {xxx}</i>"
    ds = await event.client.send_file(
        event.chat_id, 
        file=ok, 
        force_document=True, 
        caption=dk, 
        link_preview=False, 
        thumb=thum, 
        parse_mode="html"
    )
    os.remove(dl)
    os.remove(out)
    WORKING.clear()

async def apply_watermark(input_file, watermark_file, output_file):
    cmd = f"""ffmpeg -i "{input_file}" -i "{watermark_file}" -filter_complex "overlay=W-w-10:H-h-10" "{output_file}" -y"""
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()
    return output_file

async def encode_multiple(input_file, output_prefix, update_msg):
    results = []
    for quality, preset in FFMPEG_PRESETS.items():
        out_file = f"{output_prefix}_{quality}.mkv"
        cmd = f"""ffmpeg -i "{input_file}" {preset} "{out_file}" -y"""
        
        process = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        if os.path.exists(out_file):
            results.append((quality, out_file))
            
        await update_msg.edit(f"Encoded {len(results)}/{len(FFMPEG_PRESETS)} qualities")
    
    return results

async def get_ffmpeg_progress(process, total_duration, nn, filename):
    """Extract progress info from FFmpeg stderr and update the message"""
    last_edit = 0
    while True:
        try:
            if process.stderr is None:
                break
            
            line = await process.stderr.readline()
            if not line:
                break
                
            line = line.decode('utf-8')
            
            # Extract time
            if "time=" in line:
                time_in_line = line.split("time=")[1].split()[0]
                # Convert time to seconds
                try:
                    if ":" in time_in_line:
                        current_time = sum(float(x) * 60 ** i for i, x in enumerate(reversed(time_in_line.split(":"))))
                    else:
                        current_time = float(time_in_line)
                        
                    # Calculate progress percentage
                    progress = (current_time / total_duration) * 100
                    speed = line.split("speed=")[1].strip().split()[0]
                    
                    # Update message every 2 seconds to avoid flood
                    if time.time() - last_edit > 2:
                        await nn.edit(
                            f"**🗜 Encoding Progress**\n\n"
                            f"**File:** `{filename}`\n"
                            f"**Progress:** {progress:.2f}%\n"
                            f"**Speed:** {speed}\n"
                            f"**ETA:** {line.split('time=')[1].split('bitrate=')[0].strip()}"
                        )
                        last_edit = time.time()
                except:
                    continue
        except Exception as e:
            LOGS.info(f"Progress update error: {str(e)}")
            await asyncio.sleep(2)

async def get_video_duration(file_path):
    """Get video duration using FFprobe"""
    cmd = [
        "ffprobe", 
        "-v", 
        "error", 
        "-show_entries", 
        "format=duration", 
        "-of", 
        "default=noprint_wrappers=1:nokey=1", 
        file_path
    ]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, _ = await process.communicate()
    return float(stdout.decode('utf-8').strip())

async def encod(event):
    try:
        if not event.is_private:
            return
        event.sender
        if str(event.sender_id) not in OWNER and event.sender_id !=DEV:
            return await event.reply("**Sorry You're not An Authorised User!**")
        if not event.media:
            return
        if hasattr(event.media, "document"):
            if not event.media.document.mime_type.startswith(
                ("video", "application/octet-stream")
            ):
                return
        else:
            return
        if WORKING or QUEUE:
            xxx = await event.reply("**Adding To Queue...**")
            # id = pack_bot_file_id(event.media)
            doc = event.media.document
            if doc.id in list(QUEUE.keys()):
                return await xxx.edit("**This File is Already Added in Queue**")
            name = event.file.name
            if not name:
                name = "video_" + dt.now().isoformat("_", "seconds") + ".mp4"
            QUEUE.update({doc.id: [name, doc]})
            return await xxx.edit(
                "**Added This File in Queue**"
            )
        WORKING.append(1)
        xxx = await event.reply("** Downloading...**")
        s = dt.now()
        ttt = time.time()
        dir = f"downloads/"
        try:
            if hasattr(event.media, "document"):
                file = event.media.document
                filename = event.file.name
                if not filename:
                    filename = "video_" + dt.now().isoformat("_", "seconds") + ".mp4"
                dl = dir + filename
                with open(dl, "wb") as f:
                    ok = await download_file(
                        client=event.client,
                        location=file,
                        out=f,
                        progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                            progress(
                                d,
                                t,
                                xxx,
                                ttt,
                                f"** Downloading**\n__{filename}__",
                            )
                        ),
                    )
            else:
                dl = await event.client.download_media(
                    event.media,
                    dir,
                    progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                        progress(d, t, xxx, ttt, f"** Downloading**\n__{filename}__")
                    ),
                )
        except Exception as er:
            WORKING.clear()
            LOGS.info(er)
            return os.remove(dl)
        es = dt.now()
        kk = dl.split("/")[-1]
        aa = kk.split(".")[-1]
        rr = f"encode"
        bb = kk.replace(f".{aa}", ".mkv")
        newFile = dl.replace(f"downloads/", "").replace(f"_", " ")
        out = f"{rr}/{bb}"
        thum = "thumb.jpg"
        dtime = ts(int((es - s).seconds) * 1000)
        e = xxx
        hehe = f"{out};{dl};0"
        wah = code(hehe)
        nn = await e.edit(
            "**🗜 Compressing...\nPlease wait...**"
        )
        processing_file_name = newFile
        
        async def update_status():
            last_msg = ""
            while True:
                try:
                    # Check for download file first
                    if Path(dl).exists():
                        ov = hbs(int(Path(dl).stat().st_size))
                        cur_msg = f"**🗜 Compressing...**\n\nFile: {processing_file_name}\nDownloaded Size: {ov}\nCompressed: 0 B"
                        
                        # Then check for output file
                        if Path(out).exists():
                            ot = hbs(int(Path(out).stat().st_size))
                            ov = hbs(int(Path(dl).stat().st_size))
                            percentage = round((float(int(Path(out).stat().st_size)) / float(int(Path(dl).stat().st_size))) * 100, 2)
                            cur_msg = (
                                f"**🗜 Compressing: {percentage}%**\n\n"
                                f"File: {processing_file_name}\n"
                                f"Downloaded Size: {ov}\n"
                                f"Compressed Size: {ot}"
                            )
                        
                        # Only edit if message content has changed
                        if cur_msg != last_msg:
                            try:
                                await nn.edit(cur_msg)
                                last_msg = cur_msg
                            except Exception as e:
                                LOGS.info(f"Edit error: {str(e)}")
                        
                    await asyncio.sleep(3)  # Increase sleep time to 3 seconds
                    
                except Exception as e:
                    LOGS.info(f"Update status error: {str(e)}")
                    await asyncio.sleep(3)

        status_task = asyncio.create_task(update_status())
        
        # Calculate MD5 hash of downloaded file
        file_hash = hashlib.md5(open(dl,'rb').read()).hexdigest()
        cache_path = os.path.join(CACHE_DIR, file_hash)
        
        if os.path.exists(cache_path):
            # If file exists in cache, use cached version
            await xxx.edit("Found in cache! Using cached version...")
            dl = cache_path
        else:
            # If not in cache, save current file to cache
            os.makedirs(CACHE_DIR, exist_ok=True)
            shutil.copy2(dl, cache_path)
            await xxx.edit("File cached for future use...")

        nn = await e.edit("**🗜 Getting video information...**")
    
        # Get video duration
        total_duration = await get_video_duration(dl)
    
        # Modified FFmpeg command to show progress
        cmd = f"""ffmpeg -i "{dl}" {ffmpegcode[0]} "{out}" -y -progress pipe:1"""
    
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    
        # Start progress tracking
        progress_task = asyncio.create_task(
            get_ffmpeg_progress(process, total_duration, nn, newFile)
        )
    
        # Wait for encoding to complete
        stdout, stderr = await process.communicate()
    
        try:
            progress_task.cancel()
        except:
            pass

        try:
            status_task.cancel()  # Stop the status updates
        except:
            pass
        try:
            if er:
                await e.edit(str(er) + "\n\n**ERROR**")
                WORKING.clear()
                os.remove(dl)
                return os.remove(out)
        except BaseException:
            pass
        ees = dt.now()
        ttt = time.time()
        await nn.delete()
        nnn = await e.client.send_message(e.chat_id, "** Uploading...**")
        
        # Optimize upload parameters
        upload_chunk_size = 1024 * 1024 * 8  # 8MB chunks
        with open(out, "rb") as f:
            ok = await upload_file(
                client=e.client,
                file=f,
                name=out,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, nnn, ttt, f"** Uploading**\n__{out.replace(f'encode/', '')}__")
                ),
            )
        await nnn.delete()
        org = int(Path(dl).stat().st_size)
        com = int(Path(out).stat().st_size)
        pe = 100 - ((com / org) * 100)
        per = str(f"{pe:.2f}") + "%"
        eees = dt.now()
        x = dtime
        xx = ts(int((ees - es).seconds) * 1000)
        xxx = ts(int((eees - ees).seconds) * 1000)
        dk = f"<b>File Name:</b> {newFile}\n\n<b>Original File Size:</b> {hbs(org)}\n<b>Encoded File Size:</b> {hbs(com)}\n<b>Encoded Percentage:</b> {per}\n\n<i>Downloaded in {x}\nEncoded in {xx}\nUploaded in {xxx}</i>"
        ds = await e.client.send_file(
            e.chat_id, file=ok, force_document=True, caption=dk, link_preview=False, thumb=thum, parse_mode="html"
        )
        os.remove(dl)
        os.remove(out)
        WORKING.clear()
    except BaseException as er:
        LOGS.info(er)
        WORKING.clear()

# Add new command handler for watermark
async def set_watermark(event):
    if not event.photo:
        return await event.reply("Please send an image to set as watermark")
    
    try:
        await event.client.download_media(event.media, file=WATERMARK_FILE)
        await event.reply("Watermark set successfully!")
    except Exception as e:
        await event.reply(f"Error setting watermark: {str(e)}")
