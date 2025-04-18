from pyrogram import Client, filters from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton from config import Config from helper.db import (  # Ensure db.py exists in helper folder with these functions save_user_logo, remove_user_logo, cancel_user_task, total_users_count, broadcast_to_users, ban_user, unban_user ) import logging from datetime import datetime from pytz import timezone from aiohttp import web from plugins.web_support import web_server

logging.basicConfig(level=logging.INFO)

class Bot(Client):

def __init__(self):
    super().__init__(
        name="BIG_FiiSH",
        in_memory=True,
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
        plugins={'root': 'plugins'}
    )

async def start(self):
    await super().start()
    me = await self.get_me()
    self.mention = me.mention
    self.username = me.username
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, Config.PORT).start()
    logging.info(f"✅ {me.first_name} started on @{me.username} ✅")
    await self.send_message(Config.ADMIN, f"**__{me.first_name}  Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️__**")

    if Config.LOG_CHANNEL:
        try:
            curr = datetime.now(timezone("Asia/Kolkata"))
            date = curr.strftime('%d %B, %Y')
            time = curr.strftime('%I:%M:%S %p')
            await self.send_message(
                Config.LOG_CHANNEL,
                f"**__{me.mention} Iꜱ Rᴇsᴛᴀʀᴛᴇᴅ !!**\n\n📅 Dᴀᴛᴇ : `{date}`\n⏰ Tɪᴍᴇ : `{time}`\n🌐 Tɪᴍᴇᴢᴏɴᴇ : `Asia/Kolkata`"
            )
        except:
            print("Make sure the bot is admin in your log channel")

async def stop(self, *args):
    await super().stop()
    logging.info("Bot Stopped ⛔")

bot = Bot()

@bot.on_message(filters.command("start")) async def start_cmd(client, message: Message): await message.reply_photo( photo=Config.START_PIC, caption=f"Hello {message.from_user.mention},\n\nI can compress and watermark your videos with your custom settings.", reply_markup=InlineKeyboardMarkup([ [InlineKeyboardButton("Help ❓", callback_data="help")] ]) )

@bot.on_message(filters.command("help")) async def help_cmd(client, message: Message): await message.reply_text( """How to use this bot: /start - Welcome message /help - Show this help message /setwatermark - Reply to a photo to set it as a watermark /removewatermark - Remove your watermark /rename - Send a file or video to rename /encode - Encode/compress a video with watermark /cancel - Cancel the current action /settings - Customize resolution & watermark position

Admin Commands: /stats - Show usage stats /broadcast - Send a message to all users /ban - Ban a user /unban - Unban a user""" )

@bot.on_message(filters.command("setwatermark") & filters.reply) async def set_watermark(client, message: Message): if message.reply_to_message.photo: file = await message.reply_to_message.download() save_user_logo(message.from_user.id, file) await message.reply_text("Custom watermark saved successfully.") else: await message.reply_text("Please reply to a photo to set it as a watermark.")

@bot.on_message(filters.command("removewatermark")) async def remove_watermark(client, message: Message): remove_user_logo(message.from_user.id) await message.reply_text("Watermark removed successfully.")

@bot.on_message(filters.command("rename")) async def rename_handler(client, message: Message): await message.reply_text("Please send the video or file you want to rename.")

@bot.on_message(filters.command("encode")) async def encode_handler(client, message: Message): await message.reply_text("Please send the video to encode with watermark.")

@bot.on_message(filters.command("cancel")) async def cancel_handler(client, message: Message): cancel_user_task(message.from_user.id) await message.reply_text("Cancelled your current operation.")

@bot.on_message(filters.command("settings")) async def settings_handler(client, message: Message): await message.reply_text("Settings panel coming soon.")

@bot.on_message(filters.command("stats")) async def stats_handler(client, message: Message): if message.from_user.id != Config.ADMIN: return await message.reply_text("You're not authorized to use this command.") users = total_users_count() await message.reply_text(f"Bot Stats:\nTotal Users: {users}")

@bot.on_message(filters.command("broadcast")) async def broadcast_handler(client, message: Message): if message.from_user.id != Config.ADMIN: return await message.reply_text("You're not authorized to use this command.") if message.reply_to_message: await broadcast_to_users(message.reply_to_message) await message.reply_text("Broadcast sent.") else: await message.reply_text("Please reply to a message to broadcast.")

@bot.on_message(filters.command("ban")) async def ban_handler(client, message: Message): if message.from_user.id != Config.ADMIN: return if message.reply_to_message: ban_user(message.reply_to_message.from_user.id) await message.reply_text("User banned.")

@bot.on_message(filters.command("unban")) async def unban_handler(client, message: Message): if message.from_user.id != Config.ADMIN: return if message.reply_to_message: unban_user(message.reply_to_message.from_user.id) await message.reply_text("User unbanned.")

bot.run()

