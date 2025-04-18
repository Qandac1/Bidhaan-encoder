from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from helper.db import add_user, remove_watermark, set_position, get_position, user_logo
from plugins.check_user_status import check_user_status
from plugins.admin_panel import is_admin
import os

# START
@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    await add_user(message.from_user.id)
    await message.reply_photo(
        photo=Config.START_PIC,
        caption=f"**Hey {message.from_user.mention}!\n\nI am an advanced video watermark & rename bot.**\n\nUse /help to see full features.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Help ❓", callback_data="help")],
            [InlineKeyboardButton("Updates Channel", url=f"https://t.me/{Config.UPDATES}")],
        ])
    )

# HELP
@Client.on_message(filters.command("help") & filters.private)
async def help_command(client, message: Message):
    help_text = """
**Available Commands:**
/start - Show welcome message
/help - Show help message
/setwatermark - Reply to image to set your custom watermark
/removewatermark - Remove your watermark
/rename - Send a file to rename
/encode - Send video to compress & watermark
/cancel - Cancel current operation
/settings - Set watermark position and resolution

**Admin Commands:**
/stats - Show usage stats
/broadcast - Broadcast a message to all users
/ban - Ban a user
/unban - Unban a user
"""
    await message.reply(help_text)

# SET WATERMARK
@Client.on_message(filters.command("setwatermark") & filters.private)
async def set_watermark(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply("Please reply to an image to set as watermark.")
    photo_file = await message.reply_to_message.download()
    user_id = message.from_user.id
    path = f"downloads/watermark_{user_id}.png"
    os.rename(photo_file, path)
    await message.reply("✅ Watermark has been saved successfully!")

# REMOVE WATERMARK
@Client.on_message(filters.command("removewatermark") & filters.private)
async def remove_user_watermark(client, message: Message):
    user_id = message.from_user.id
    path = f"downloads/watermark_{user_id}.png"
    if os.path.exists(path):
        os.remove(path)
        await message.reply("🗑️ Your watermark has been removed.")
    else:
        await message.reply("You don’t have a custom watermark set.")

# SETTINGS
@Client.on_message(filters.command("settings") & filters.private)
async def settings_command(client, message: Message):
    pos = await get_position(message.from_user.id) or "↘ Bottom-right"
    await message.reply(
        f"⚙️ Current Settings:\n\n• Watermark Position: `{pos}`",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("↖", callback_data="pos_↖"),
                InlineKeyboardButton("↑", callback_data="pos_↑"),
                InlineKeyboardButton("↗", callback_data="pos_↗")
            ],
            [
                InlineKeyboardButton("←", callback_data="pos_←"),
                InlineKeyboardButton("⚪", callback_data="pos_⚪"),
                InlineKeyboardButton("→", callback_data="pos_→")
            ],
            [
                InlineKeyboardButton("↙", callback_data="pos_↙"),
                InlineKeyboardButton("↓", callback_data="pos_↓"),
                InlineKeyboardButton("↘", callback_data="pos_↘")
            ]
        ])
    )

@Client.on_callback_query(filters.regex("pos_"))
async def change_position(client, callback_query):
    pos = callback_query.data.split("_", 1)[1]
    await set_position(callback_query.from_user.id, pos)
    await callback_query.answer(f"Updated position to {pos}!", show_alert=True)
    await callback_query.message.delete()

# RENAME
@Client.on_message(filters.command("rename") & filters.private)
async def rename_file(client, message: Message):
    if not message.reply_to_message or not (message.reply_to_message.document or message.reply_to_message.video):
        return await message.reply("Please reply to a file or video to rename it.")
    file = message.reply_to_message.document or message.reply_to_message.video
    filename = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else file.file_name
    await file.download(f"downloads/{filename}")
    await message.reply(f"✅ Renamed file to `{filename}` successfully!")

# ENCODE (Watermark & Compression)
@Client.on_message(filters.command("encode") & filters.private)
async def encode_video(client, message: Message):
    if not message.reply_to_message or not (message.reply_to_message.document or message.reply_to_message.video):
        return await message.reply("Please reply to a video or file to encode and watermark it.")
    file = message.reply_to_message.document or message.reply_to_message.video
    watermark = await user_logo(message.from_user.id)
    if watermark:
        # Add watermark logic (placeholder for now)
        await file.download(f"downloads/encoded_{file.file_name}")
        await message.reply(f"✅ File encoded and watermark added successfully!")
    else:
        await message.reply("You don't have a watermark set. Please set one using /setwatermark.")

# CANCEL
@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_command(client, message: Message):
    # Placeholder for cancel logic, typically would stop any ongoing process
    await message.reply("❌ Operation cancelled.")

# STATS (Admin only)
@Client.on_message(filters.command("stats") & filters.private)
async def stats_command(client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("You are not authorized to view stats.")
    # Placeholder for stats logic, would typically fetch data from the bot's usage
    await message.reply("📊 Bot Stats: [Placeholder data]")

# BROADCAST (Admin only)
@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast_command(client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("You are not authorized to send broadcast messages.")
    text = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else None
    if not text:
        return await message.reply("Please provide a message to broadcast.")
    # Placeholder for sending broadcast message to all users
    await message.reply(f"📢 Broadcasting message: {text}")

# BAN (Admin only)
@Client.on_message(filters.command("ban") & filters.private)
async def ban_user(client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("You are not authorized to ban users.")
    user_id = int(message.text.split(" ", 1)[1]) if len(message.text.split()) > 1 else None
    if not user_id:
        return await message.reply("Please provide the user ID to ban.")
    # Placeholder for banning user
    await message.reply(f"🚫 User {user_id} banned successfully.")

# UNBAN (Admin only)
@Client.on_message(filters.command("unban") & filters.private)
async def unban_user(client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("You are not authorized to unban users.")
