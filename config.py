import os
import re
from pymongo import MongoClient

class Config:
    # API Configuration
    API_ID = int(os.environ.get("API_ID", 26385571))
    API_HASH = os.environ.get("API_HASH", "aac7a3c3c2f36e72201a6a5a21eb802a")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7747196334:AAE6fjbVnVmDpjMcPSFWayIFK3uyNIRBTPM")
    FORCE_SUB = os.environ.get("FORCE_SUB", "BIDHAANBOTS")
    AUTH_CHANNEL = int(FORCE_SUB) if FORCE_SUB and re.match(r'^.\d+$', FORCE_SUB) else None

    # MongoDB Configuration
    DB_URL = os.environ.get("DB_URL", "mongodb+srv://telegramguy21:tnkIwvbNkJ5U3fZ7@botsuse.bpgag.mongodb.net/?retryWrites=true&w=majority&appName=Botsuse")
    DB_NAME = os.environ.get("DB_NAME", "EncodeMarkRenameBot")
    ADMIN = int(os.environ.get("ADMIN", 6169808990))
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", -1002586992832))

    # Starting image and caption template
    START_PIC = os.environ.get("START_PIC", "https://graph.org/file/15e82d7e665eccc8bd9c5.jpg")
    caption = """
    **File Name:** {0}
    **Original Size:** {1}
    **Encoded Size:** {2}
    **Compression:** {3}
    
    __Downloaded in:__ {4}  
    __Encoded in:__ {5}  
    __Uploaded in:__ {6}  
    """

    # Webhook & Port
    WEBHOOK = os.environ.get("WEBHOOK", "True").lower() in ("true", "1", "yes")
    PORT = int(os.environ.get("PORT", 8080))

    # FFmpeg and Watermarking
    FFMPEG_PATH = os.environ.get("FFMPEG_PATH", "/usr/bin/ffmpeg")
    default_resolution = "original"  # "1080p", "720p", "480p", "original"
    watermark_enabled = True

    # Watermark Position Map
    WATERMARK_POSITIONS = {
        "↖": "(0):(0)", "↑": "(main_w-overlay_w)/2:(0)", "↗": "(main_w-overlay_w):(0)",
        "←": "(0):(main_h-overlay_h)/2", "⚪": "(main_w-overlay_w)/2:(main_h-overlay_h)/2",
        "→": "(main_w-overlay_w):(main_h-overlay_h)/2", "↙": "(0):(main_h-overlay_h)",
        "↓": "(main_w-overlay_w)/2:(main_h-overlay_h)", "↘": "(main_w-overlay_w):(main_h-overlay_h)"
    }

    @staticmethod
    def is_admin(user_id):
        return user_id == Config.ADMIN

    @staticmethod
    def default_watermark_command(message):
        return "↖"

    @staticmethod
    def build_watermark_filter(user_id, positions):
        interval = 60
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

        return f"{Config.FFMPEG_PATH} -i '{input_file}' -i '{logo_path}' {wm_filter} -preset fast -crf 23 -c:a copy '{output_file}'"

    @staticmethod
    def rename_video(file_path, new_name):
        if not os.path.exists(file_path):
            return None
        new_file = os.path.join(os.path.dirname(file_path), new_name + os.path.splitext(file_path)[1])
        os.rename(file_path, new_file)
        return new_file

    @staticmethod
    def get_user_settings(user_id):
        return {}

    @staticmethod
    def get_user_logo(user_id):
        client = MongoClient(Config.DB_URL)
        db = client[Config.DB_NAME]
        collection = db["user_watermarks"]
        data = collection.find_one({"user_id": user_id})
        return data["logo_path"] if data and "logo_path" in data else None
