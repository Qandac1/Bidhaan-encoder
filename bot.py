import os
import re
import logging
import subprocess
from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

# ================= CONFIGURATION =================
class Config:
    # Telegram Credentials
    API_ID = int(os.environ.get("API_ID", 26385571))
    API_HASH = os.environ.get("API_HASH", "aac7a3c3c2f36e72201a6a5a21eb802a")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7747196334:AAE6fjbVnVmDpjMcPSFWayIFK3uyNIRBTPM")

    # MongoDB Configuration
    DB_URL = os.environ.get("DB_URL", "mongodb+srv://BIGFIISH:iFyAm2DZqEzo76VW@cluster0.z6bhz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    DB_NAME = os.environ.get("DB_NAME", "EncodeMarkRenameBot")

    # Watermark Settings
    WATERMARK_POSITIONS = {
        "↖": "0:0",
        "↑": "(main_w-overlay_w)/2:0",
        "↗": "main_w-overlay_w:0",
        "←": "0:(main_h-overlay_h)/2",
        "⚪": "(main_w-overlay_w)/2:(main_h-overlay_h)/2",
        "→": "main_w-overlay_w:(main_h-overlay_h)/2",
        "↙": "0:main_h-overlay_h",
        "↓": "(main_w-overlay_w)/2:main_h-overlay_h",
        "↘": "main_w-overlay_w:main_h-overlay_h"
    }
    WATERMARK_MODES = ["position", "fill", "random", "corners"]
    SPEED_VALUES = [5, 15, 30, 50, 100]

    # Encoding Presets
    RESOLUTIONS = {
        '480p': '854:480',
        '720p': '1280:720', 
        '1080p': '1920:1080',
        '4k': '3840:2160',
        'original': None
    }

    @staticmethod
    def get_db():
        client = MongoClient(Config.DB_URL)
        return client[Config.DB_NAME]

# ================= WATERMARK ENGINE =================
class WatermarkHandler:
    @staticmethod
    def generate_filter(user_id: int):
        db = Config.get_db()
        user = db.users.find_one({"user_id": user_id}) or {}
        
        mode = user.get("wm_mode", "position")
        speed = user.get("speed", 30)
        positions = user.get("positions", ["↖", "↑", "↗", "←", "⚪", "→", "↙", "↓", "↘"])

        # Calculate interval based on speed (higher speed = slower movement)
        interval = (100 - speed) * 2

        if mode == "fill":
            return "-vf tile=5x5:overlap=0.2"
        
        elif mode == "random":
            return "-vf overlay=x='if(eq(mod(n,30),0),random(0)*W,overlay_x)':y='if(eq(mod(n,30),0),random(0)*H,overlay_y)'"
        
        elif mode == "corners":
            corner_positions = ["0:0", "main_w-overlay_w:0", 
                              "0:main_h-overlay_h", "main_w-overlay_w:main_h-overlay_h"]
            return f"-filter_complex overlay={':'.join(corner_positions)} -loop 1"
        
        else:  # Position mode
            pos = user.get("position", "↖")
            return f"-filter_complex overlay={Config.WATERMARK_POSITIONS.get(pos, '0:0')}"

# ================= BOT HANDLERS =================
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🚀 Welcome to Advanced Encoder Bot!\n"
        "📌 Features:\n"
        "- 4GB File Support\n"
        "- Moving/Static Watermarks\n"
        "- Multi-mode Encoding\n\n"
        "Use /encode to start!",
        reply_markup=main_menu()
    )

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ Watermark Settings", callback_data="wm_settings"),
         InlineKeyboardButton("🎥 Encode Video", callback_data="encode_menu")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast"),
         InlineKeyboardButton("❌ Close", callback_data="close")]
    ])

def handle_video(update: Update, context: CallbackContext):
    video = update.message.video
    user_id = update.message.from_user.id
    
    if video.file_size > 4 * 1024 * 1024 * 1024:  # 4GB limit
        update.message.reply_text("❌ File exceeds 4GB limit!")
        return

    # Download video
    file = video.get_file()
    file.download("input.mp4")
    
    # Process with watermark
    output = f"output_{user_id}.mp4"
    cmd = [
        "ffmpeg", "-i", "input.mp4",
        *WatermarkHandler.generate_filter(user_id).split(),
        "-c:v", "libx264", "-preset", "fast",
        output
    ]
    
    try:
        subprocess.run(cmd, check=True)
        update.message.reply_video(video=open(output, "rb"))
        os.remove(output)
    except Exception as e:
        logging.error(f"Encoding failed: {str(e)}")
        update.message.reply_text("❌ Processing failed!")

# ================= RUN BOT =================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    updater = Updater(Config.BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.video, handle_video))
    dp.add_handler(CallbackQueryHandler(lambda update, ctx: update.callback_query.answer()))

    updater.start_polling()
    updater.idle()
