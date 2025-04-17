import os
import time
import re

id_pattern = re.compile(r'^.\d+$')

class Config(object):
    # Pyrogram API credentials
    API_ID = int(os.environ.get("API_ID", 26385571))
    API_HASH = os.environ.get("API_HASH", "aac7a3c3c2f36e72201a6a5a21eb802a")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7747196334:AAE6fjbVnVmDpjMcPSFWayIFK3uyNIRBTPM")

    # Force subscription / auth channel
    FORCE_SUB = os.environ.get("FORCE_SUB", "BIDHAANBOTS")
    AUTH_CHANNEL = int(FORCE_SUB) if FORCE_SUB and id_pattern.search(FORCE_SUB) else None

    # MongoDB config
    DB_URL = os.environ.get("DB_URL", "mongodb+srv://telegramguy21:tnkIwvbNkJ5U3fZ7@botsuse.bpgag.mongodb.net/?retryWrites=true&w=majority&appName=Botsuse")
    DB_NAME = os.environ.get("DB_NAME", "EncodeMarkRenameBot")

    # Admin & Logs
    ADMIN = int(os.environ.get("ADMIN", 6169808990))
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", -1002586992832))

    # Runtime info
    BOT_UPTIME = time.time()
    START_PIC = os.environ.get("START_PIC", "https://graph.org/file/15e82d7e665eccc8bd9c5.jpg")

    # Webhook & server
    WEBHOOK = os.environ.get("WEBHOOK", "True").lower() in ("true", "1", "yes")
    PORT = int(os.environ.get("PORT", 8080))

    # Caption template
    caption = """
**File Name**: {0}

**Original File Size:** {1}
**Encoded File Size:** {2}
**Compression Percentage:** {3}

__Downloaded in {4}__
__Encoded in {5}__
__Uploaded in {6}__
"""
