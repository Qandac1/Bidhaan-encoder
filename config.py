import os
import re
import logging
from pymongo import MongoClient

class Config:
    # Telegram
    API_ID = int(os.environ.get("API_ID", 26385571))
    API_HASH = os.environ.get("API_HASH", "aac7a3c3c2f36e72201a6a5a21eb802a")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7747196334:AAE6fjbVnVmDpjMcPSFWayIFK3uyNIRBTPM")
    
    # Database
    DB_URL = os.environ.get("DB_URL", "mongodb+srv://BIGFIISH:iFyAm2DZqEzo76VW@cluster0.z6bhz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    DB_NAME = os.environ.get("DB_NAME", "EncodeMarkRenameBot")
    
    # Watermark
    WATERMARK_MODES = ["position", "fill", "random", "corners"]
    SPEED_VALUES = [5, 15, 30, 50, 100]
    DEFAULT_SPEED = 30
    WATERMARK_VISIBLE = 5  # Seconds per position
    
    # Encoding
    MAX_FILE_SIZE = 4 * 1024 * 1024 * 1024  # 4GB
    RESOLUTIONS = ['480p', '720p', '1080p', '4k', 'original']
    
    # Other
    ADMINS = list(map(int, os.environ.get("ADMINS", "6169808990").split()))
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", -1002537610513))

    @staticmethod
    def get_user_settings(user_id: int):
        client = MongoClient(Config.DB_URL)
        return client[Config.DB_NAME].users.find_one({"user_id": user_id}) or {}
