import os
import re

class Config:
    # API Configuration
    API_ID = int(os.environ.get("API_ID", 26385571))
    API_HASH = os.environ.get("API_HASH", "aac7a3c3c2f36e72201a6a5a21eb802a")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7932656660:AAFqwho7Al8_TcB3ff6nJkJxvEtmXfZLHZ0")
    FORCE_SUB = os.environ.get("FORCE_SUB", "BIDHAANBOTS")
    AUTH_CHANNEL = int(FORCE_SUB) if FORCE_SUB and re.match(r'^.\d+$', FORCE_SUB) else None

    # MongoDB Configuration
    DB_URL = os.environ.get("DB_URL", "mongodb+srv://telegramguy21:tnkIwvbNkJ5U3fZ7@botsuse.bpgag.mongodb.net/?retryWrites=true&w=majority&appName=Botsuse")
    DB_NAME = os.environ.get("DB_NAME", "EncodeMarkRenameBot")
    ADMIN = int(os.environ.get("ADMIN", 6169808990))
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", -1002586992832))

    # Starting image and caption
    START_PIC = os.environ.get("START_PIC", "https://graph.org/file/15e82d7e665eccc8bd9c5.jpg")
    caption = """
    **File Name**: {0}
    **Original File Size:** {1}
    **Encoded File Size:** {2}
    **Compression Percentage:** {3}
    __Downloaded in {4}__
    __Encoded in {5}__
    __Uploaded in {6}__
    """

    # Webhook and port
    WEBHOOK = os.environ.get("WEBHOOK", "True").lower() in ("true", "1", "yes")
    PORT = int(os.environ.get("PORT", 8080))

    # Watermark Positions
    WATERMARK_POSITIONS = {
        "↖": "(0):(0)", "↑": "(main_w-overlay_w)/2:(0)", "↗": "(main_w-overlay_w):(0)",
        "←": "(0):(main_h-overlay_h)/2", "⚪": "(main_w-overlay_w)/2:(main_h-overlay_h)/2",
        "→": "(main_w-overlay_w):(main_h-overlay_h)/2", "↙": "(0):(main_h-overlay_h)",
        "↓": "(main_w-overlay_w)/2:(main_h-overlay_h)", "↘": "(main_w-overlay_w):(main_h-overlay_h)"
    }

    # FFMpeg options
    FFMPEG_PATH = os.environ.get("FFMPEG_PATH", "/usr/bin/ffmpeg")

    # Default options for watermarking and renaming
    default_resolution = "original"  # Options: "1080p", "720p", "480p", "original"
    watermark_enabled = True  # Toggle watermark on/off

    # Helper function to check if user is admin
    @staticmethod
    def is_admin(user_id):
        return user_id == Config.ADMIN

    # Watermark Filter Generator for FFmpeg
    @staticmethod
    def build_watermark_filter(user_id, positions):
        interval = 60  # Customize interval as required
        overlay_filters = []

        for i, pos in enumerate(positions):
            start = i * interval
            end = (i + 1) * interval
            overlay_filters.append(
                f"enable='between(t,{start},{end})':x={Config.WATERMARK_POSITIONS[pos].split(':')[0]}:y={Config.WATERMARK_POSITIONS[pos].split(':')[1]}"
            )
        filter_complex = "[1:v]scale=iw/6:-1[logo];[0:v][logo]overlay=" + ":".join(overlay_filters)
        return f'-filter_complex "{filter_complex}"'

    # FFmpeg command generator
    @staticmethod
    def build_ffmpeg_cmd(input_file, output_file, logo_path, resolution, wm_filter):
        if not all(os.path.exists(f) for f in [input_file, logo_path]):
            return None

        scale_filter = ""
        if resolution != "original":
            res_map = {"1080p": "1920:1080", "720p": "1280:720", "480p": "854:480"}
            scale_filter = f",scale={res_map.get(resolution, '1920:1080')}"
        
        cmd = f"ffmpeg -i {input_file} -i {logo_path} {scale_filter} {wm_filter} -c:v libx264 -preset fast -crf 23 -c:a copy {output_file}"
        return cmd

    # Helper function for renaming videos
    @staticmethod
    def rename_video(file_path, new_name):
        if not os.path.exists(file_path):
            return None
        new_file_path = os.path.join(os.path.dirname(file_path), new_name + os.path.splitext(file_path)[1])
        os.rename(file_path, new_file_path)
        return new_file_path

    # MongoDB settings for user preferences
    @staticmethod
    def get_user_settings(user_id):
        # Here you can retrieve user-specific settings from the database
        # Example:
        # db = MongoClient(Config.DB_URL)[Config.DB_NAME]
        # user_settings_col = db["user_settings"]
        # settings = user_settings_col.find_one({"user_id": user_id})
        return {}

    # Default Watermark Command
    @staticmethod
    def default_watermark_command(message):
        return "↖"  # Default position, can be customized per user
