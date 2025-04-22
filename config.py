import os
import re
from pymongo import MongoClient

class Config:
    # Telegram API & Bot Token
    API_ID = int(os.environ.get("API_ID", 26385571))
    API_HASH = os.environ.get("API_HASH", "aac7a3c3c2f36e72201a6a5a21eb802a")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7747196334:AAE6fjbVnVmDpjMcPSFWayIFK3uyNIRBTPM")

    # Force Subscription Channel
    FORCE_SUB = os.environ.get("FORCE_SUB", "BIDHAANBOTS")
    AUTH_CHANNEL = int(FORCE_SUB) if FORCE_SUB and re.match(r'^.\d+$', FORCE_SUB) else None

    # MongoDB Configuration
    DB_URL = os.environ.get("DB_URL", "mongodb+srv://BIGFIISH:iFyAm2DZqEzo76VW@cluster0.z6bhz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    DB_NAME = os.environ.get("DB_NAME", "EncodeMarkRenameBot")

    # Admins
    ADMINS = list(map(int, os.environ.get("ADMINS", "6169808990").split()))
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL",-1002537610513"))

    # Start image and caption template
    START_PIC = os.environ.get("START_PIC", "https://graph.org/file/15e82d7e665eccc8bd9c5.jpg")
    CAPTION_TEMPLATE = """
**File Name:** {0}
**Original Size:** {1}
**Encoded Size:** {2}
**Compression:** {3}

__Downloaded in:__ {4}  
__Encoded in:__ {5}  
__Uploaded in:__ {6}  
"""

    # Webhook
    WEBHOOK = os.environ.get("WEBHOOK", "True").lower() in ("true", "1", "yes")
    PORT = int(os.environ.get("PORT", 8080))

    # FFmpeg
    FFMPEG_PATH = os.environ.get("FFMPEG_PATH", "/usr/bin/ffmpeg")
    DEFAULT_RESOLUTION = "original"  # Options: "1080p", "720p", "480p", "original"
    WATERMARK_ENABLED = True
    WATERMARK_INTERVAL = int(os.environ.get("WATERMARK_INTERVAL", 60))

    # Watermark Positions Map
    WATERMARK_POSITIONS = {
        "↖": "(0):(0)",
        "↑": "(main_w-overlay_w)/2:(0)",
        "↗": "(main_w-overlay_w):(0)",
        "←": "(0):(main_h-overlay_h)/2",
        "⚪": "(main_w-overlay_w)/2:(main_h-overlay_h)/2",
        "→": "(main_w-overlay_w):(main_h-overlay_h)/2",
        "↙": "(0):(main_h-overlay_h)",
        "↓": "(main_w-overlay_w)/2:(main_h-overlay_h)",
        "↘": "(main_w-overlay_w):(main_h-overlay_h)"
    }

    @staticmethod
    def is_admin(user_id):
        return user_id in Config.ADMINS

    @staticmethod
    def default_watermark_position():
        return "↖"

    @staticmethod
    def build_watermark_filter(user_id, positions):
        interval = Config.WATERMARK_INTERVAL
        overlay_filters = []

        for i, pos in enumerate(positions):
            start = i * interval
            end = (i + 1) * interval
            x, y = Config.WATERMARK_POSITIONS[pos].split(':')
            overlay_filters.append(f"enable='between(t,{start},{end})':x={x}:y={y}")

        filters = "[1:v]scale=iw/6:-1[logo];[0:v][logo]overlay=" + ":".join(overlay_filters)
        return f'-filter_complex "{filters}"'

    @staticmethod
    def build_ffmpeg_cmd(input_file, output_file, logo_path, resolution, wm_filter):
        if not os.path.exists(input_file) or not os.path.exists(logo_path):
            return None

        scale_filter = ""
        if resolution != "original":
            resolutions = {"1080p": "1920:1080", "720p": "1280:720", "480p": "854:480"}
            scale_filter = f"-vf scale={resolutions.get(resolution, '1920:1080')}"

        return f"{Config.FFMPEG_PATH} -i '{input_file}' -i '{logo_path}' {wm_filter} {scale_filter} -preset fast -crf 23 -c:a copy '{output_file}'"

    @staticmethod
    def rename_video(file_path, new_name):
        if not os.path.exists(file_path):
            return None
        new_file = os.path.join(os.path.dirname(file_path), new_name + os.path.splitext(file_path)[1])
        os.rename(file_path, new_file)
        return new_file

    @staticmethod
    def get_user_logo(user_id):
        client = MongoClient(Config.DB_URL)
        db = client[Config.DB_NAME]
        collection = db["user_watermarks"]
        data = collection.find_one({"user_id": user_id})
        return data.get("logo_path") if data else None

    @staticmethod
    def get_user_settings(user_id):
        # Placeholder if you plan to implement per-user settings
        return {}
