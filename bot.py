from pyrogram import Client
from pyrogram.raw.all import layer
from config import Config
import logging
import pyrogram
from datetime import datetime
import logging.config, os
from pytz import timezone
from aiohttp import web
from plugins.web_support import web_server
import pyromod

# Logging Configuration
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="SnowEncoderBot",
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

        # Start the web server for webhook if needed
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, Config.PORT).start()

        logging.info(f"✅ {me.first_name} with Pyrogram v{pyrogram.__version__} (Layer {layer}) started on @{me.username}. ✅")

        # Notify all admins
        for admin in Config.ADMINS:
            try:
                await self.send_message(admin, f"{me.first_name}  Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️")
            except Exception as e:
                logging.warning(f"Failed to send start message to admin {admin}: {e}")

        # Log to channel if enabled
        if Config.LOG_CHANNEL:
            try:
                curr = datetime.now(timezone("Asia/Kolkata"))
                date = curr.strftime('%d %B, %Y')
                time = curr.strftime('%I:%M:%S %p')
                await self.send_message(
                    Config.LOG_CHANNEL,
                    f"__{me.mention} Iꜱ Rᴇsᴛᴀʀᴛᴇᴅ !!__\n\n"
                    f"📅 Dᴀᴛᴇ : {date}\n⏰ Tɪᴍᴇ : {time}\n"
                    f"🌐 Tɪᴍᴇᴢᴏɴᴇ : Asia/Kolkata\n\n"
                    f"🉐 Vᴇʀsɪᴏɴ : v{pyrogram.__version__} (Layer {layer})"
                )
            except Exception as e:
                logging.warning("⚠️ Failed to log restart message. Is the bot admin in LOG_CHANNEL?")

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot Stopped ⛔")

bot = Bot()
bot.run()
