from pyrogram import filters from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup from main import bot from config import Config from helpers.database import save_user_logo, remove_user_logo

@bot.on_message(filters.command("start")) async def start_handler(_, message: Message): await message.reply_photo( photo=Config.START_PIC, caption=f"👋 Hello {message.from_user.mention},\nWelcome to {Config.BOT_NAME}!\n\nUse /help to see available features.", )

@bot.on_message(filters.command("help")) async def help_handler(_, message: Message): help_text = """ <b>✨ Bot Usage Help:</b>

/start ➡️ Welcome message /help ❓ Show help on how to use the bot /setwatermark 🖼️ Set your custom watermark (reply to a photo) /removewatermark 🚫 Remove your custom watermark /rename ✏️ Rename a file (send a video or file) /encode 🔄 Encode/compress a video with watermark /cancel ❌ Cancel the current operation /settings ⚙️ Customize resolution and watermark position /stats 📊 Show bot usage stats (admin only) /broadcast 📢 Send a message to all users (admin only) /ban 🚫 Ban a user (admin only) /unban ✅ Unban a user (admin only) """ await message.reply_text(help_text, quote=True)

@bot.on_message(filters.command("setwatermark") & filters.reply) async def set_user_watermark(_, message: Message): if message.reply_to_message.photo: file = await message.reply_to_message.download() save_user_logo(message.from_user.id, file) await message.reply_text("✅ Custom watermark saved.") else: await message.reply_text("❌ Please reply to a photo.")

@bot.on_message(filters.command("removewatermark")) async def remove_user_watermark(_, message: Message): remove_user_logo(message.from_user.id) await message.reply_text("✅ Watermark removed.")

@bot.on_message(filters.command("settings")) async def settings_handler(_, message: Message): buttons = [ [ InlineKeyboardButton("1080p", callback_data="res_1080"), InlineKeyboardButton("720p", callback_data="res_720"), InlineKeyboardButton("480p", callback_data="res_480") ], [ InlineKeyboardButton("Top-Left", callback_data="wm_tl"), InlineKeyboardButton("Center", callback_data="wm_center"), InlineKeyboardButton("Bottom-Right", callback_data="wm_br") ] ] await message.reply("⚙️ Choose settings:", reply_markup=InlineKeyboardMarkup(buttons))

