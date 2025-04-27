# bot.py

import os
import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config

app = Client(
    "EncodeMarkRenameBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

DOWNLOADS = "downloads/"
os.makedirs(DOWNLOADS, exist_ok=True)


@app.on_message(filters.command("start"))
async def start(client, message):
    if Config.AUTH_CHANNEL:
        try:
            user = await client.get_chat_member(Config.AUTH_CHANNEL, message.from_user.id)
            if user.status not in ("member", "administrator", "creator"):
                raise Exception("Not a member")
        except Exception:
            invite_link = f"https://t.me/{Config.FORCE_SUB}"
            await message.reply_text(
                f"**Please join the channel first** to use this bot!",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Join Channel", url=invite_link)]]
                )
            )
            return

    await message.reply_photo(
        photo=Config.START_PIC,
        caption=f"Hi {message.from_user.first_name}!\n\nSend me a video to watermark, compress and rename it!",
    )


@app.on_message(filters.video)
async def video_handler(client, message):
    sent = await message.reply_text("Downloading your video...")
    video = await message.download(file_name=DOWNLOADS)

    await sent.edit("Checking your watermark settings...")
    user_logo = Config.get_user_logo(message.from_user.id)

    if not user_logo:
        await sent.edit("You have no custom watermark set. Please set one first.")
        return

    wm_positions = ["↖", "↘", "↙", "↗"]  # Default positions if user has no settings
    user_settings = Config.get_user_settings(message.from_user.id)
    if user_settings and user_settings.get("positions"):
        wm_positions = user_settings["positions"]

    wm_filter = Config.build_watermark_filter(message.from_user.id, wm_positions)
    output = os.path.join(DOWNLOADS, f"watermarked_{int(time.time())}.mp4")

    await sent.edit("Encoding your video with watermark...")

    ffmpeg_cmd = Config.build_ffmpeg_cmd(video, output, user_logo, Config.DEFAULT_RESOLUTION, wm_filter)
    if not ffmpeg_cmd:
        await sent.edit("Error building ffmpeg command. Try again later.")
        return

    process = await asyncio.create_subprocess_shell(ffmpeg_cmd)
    await process.communicate()

    if not os.path.exists(output):
        await sent.edit("Encoding failed. Something went wrong.")
        return

    # File size before/after
    original_size = round(os.path.getsize(video) / (1024 * 1024), 2)
    encoded_size = round(os.path.getsize(output) / (1024 * 1024), 2)
    compression = round((encoded_size/original_size)*100, 2)

    await sent.edit("Uploading your watermarked video...")

    start_time = time.time()
    await message.reply_video(
        video=output,
        caption=Config.CAPTION_TEMPLATE.format(
            os.path.basename(output),
            f"{original_size} MB",
            f"{encoded_size} MB",
            f"{compression}%",
            "N/A",
            f"{round(time.time() - start_time)} sec",
            "N/A"
        ),
        supports_streaming=True
    )
    await sent.delete()

    # Clean files
    try:
        os.remove(video)
        os.remove(output)
    except Exception as e:
        print(f"Error cleaning files: {e}")


@app.on_message(filters.command("setlogo") & filters.private)
async def set_logo(client, message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply_text("Reply to a logo image with /setlogo to set your watermark.")
        return

    file = await message.reply_to_message.download(file_name=DOWNLOADS)
    collection = Config.mongo_db["user_watermarks"]

    collection.update_one(
        {"user_id": message.from_user.id},
        {"$set": {"logo_path": file}},
        upsert=True
    )

    await message.reply_text("Your custom watermark logo has been saved!")

@app.on_message(filters.command("settings") & filters.private)
async def settings_menu(client, message):
    await message.reply_text(
        "Settings feature is under development.\n\nYou can currently set your watermark logo by replying to an image with /setlogo.",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Update Coming Soon", callback_data="none")]]
        )
    )

@app.on_message(filters.command("help"))
async def help_command(client, message):
    await message.reply_text("Send a video, and I will add your watermark automatically!\n\n"
                              "/setlogo - Set your custom watermark\n"
                              "/settings - Settings menu (Coming soon)")

# Run the bot
app.run()
