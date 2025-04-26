import os import re import logging import subprocess from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update from telegram.ext import ( Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext ) from pymongo import MongoClient

----------------------------------------------------------------------------

Configuration class (filled with your bot info)

----------------------------------------------------------------------------

class Config: # Telegram API & Bot Token API_ID        = int(os.environ.get("API_ID", 26385571)) API_HASH      = os.environ.get("API_HASH", "aac7a3c3c2f36e72201a6a5a21eb802a") BOT_TOKEN     = os.environ.get("BOT_TOKEN", "7747196334:AAE6fjbVnVmDpjMcPSFWayIFK3uyNIRBTPM")

# Force Subscription Channel
FORCE_SUB     = os.environ.get("FORCE_SUB", "BIDHAANBOTS")
AUTH_CHANNEL  = int(FORCE_SUB) if FORCE_SUB and re.match(r'^-?\d+$', FORCE_SUB) else None

# MongoDB Configuration
DB_URL        = os.environ.get("DB_URL",
                    "mongodb+srv://BIGFIISH:iFyAm2DZqEzo76VW@cluster0.z6bhz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME       = os.environ.get("DB_NAME", "EncodeMarkRenameBot")

# Admins
ADMINS        = list(map(int, os.environ.get("ADMINS", "6169808990").split()))
LOG_CHANNEL   = int(os.environ.get("LOG_CHANNEL", -1002537610513))

# Webhook
WEBHOOK       = os.environ.get("WEBHOOK", "True").lower() in ("true","1","yes")
PORT          = int(os.environ.get("PORT", 8080))

# FFmpeg & watermark timing
FFMPEG_PATH        = os.environ.get("FFMPEG_PATH", "/usr/bin/ffmpeg")
WATERMARK_INTERVAL = int(os.environ.get("WATERMARK_INTERVAL", 60))  # seconds per slot
WATERMARK_VISIBLE  = int(os.environ.get("WATERMARK_VISIBLE", 5))   # visible seconds per slot

# 9-grid positions map
WATERMARK_POSITIONS = {
    "↖": "0:0",                           # top-left
    "↑": "(main_w-overlay_w)/2:0",       # top-center
    "↗": "main_w-overlay_w:0",           # top-right
    "←": "0:(main_h-overlay_h)/2",       # center-left
    "⚪": "(main_w-overlay_w)/2:(main_h-overlay_h)/2",  # center
    "→": "main_w-overlay_w:(main_h-overlay_h)/2",      # center-right
    "↙": "0:main_h-overlay_h",           # bottom-left
    "↓": "(main_w-overlay_w)/2:main_h-overlay_h",     # bottom-center
    "↘": "main_w-overlay_w:main_h-overlay_h"          # bottom-right
}

@staticmethod
def get_user_logo(user_id: int) -> str:
    client = MongoClient(Config.DB_URL)
    rec = client[Config.DB_NAME].user_watermarks.find_one({"user_id": user_id})
    return rec.get("logo_path") if rec else None

@staticmethod
def save_user_logo(user_id: int, logo_path: str):
    client = MongoClient(Config.DB_URL)
    client[Config.DB_NAME].user_watermarks.update_one(
        {"user_id": user_id}, {"$set": {"logo_path": logo_path}}, upsert=True
    )

@staticmethod
def build_watermark_filter(positions: list) -> str:
    """
    Build FFmpeg filter_complex for smooth motion through the 9-grid positions.
    """
    interval = Config.WATERMARK_INTERVAL
    visible  = Config.WATERMARK_VISIBLE
    num_slots = len(positions)
    slot = interval / num_slots

    # extract coordinate expressions per symbol
    xs = [Config.WATERMARK_POSITIONS[s].split(':')[0] for s in positions]
    ys = [Config.WATERMARK_POSITIONS[s].split(':')[1] for s in positions]

    # nested linear interpolation builder
    def nest(arr):
        def expr(i):
            if i >= num_slots:
                return "NAN"
            start = i * slot
            end   = start + slot
            cur   = arr[i]
            nxt   = arr[(i + 1) % num_slots]
            # linear ramp from cur to nxt over slot duration
            return (
                f"if(between(mod(t\\,{interval})\\,{start:.3f}\\,{end:.3f})\\,"  \
                f"{cur} + ({nxt}-{cur})*(mod(t\\,{interval})-{start:.3f})/{slot:.3f}\\,"  \
                f"{expr(i+1)})"
            )
        return expr(0)

    x_expr = nest(xs)
    y_expr = nest(ys)

    filter_str = (
        "[1:v]scale=iw/6:-1[logo];"
        "[0:v][logo]overlay="
        f"x='{x_expr}':y='{y_expr}'"
    )
    return f"-filter_complex \"{filter_str}\""

@staticmethod
def build_ffmpeg_cmd(input_file: str, output_file: str,
                     logo_path: str, wm_filter: str,
                     resolution: str) -> list:
    cmd = [Config.FFMPEG_PATH, '-i', input_file, '-i', logo_path]
    cmd += wm_filter.split()
    # add scaling for resolution
    if resolution != 'original':
        sizes = {'480p':'854:480','720p':'1280:720','1080p':'1920:1080','4k':'3840:2160'}
        if resolution in sizes:
            cmd += ['-vf', f"scale={sizes[resolution]}"]
    # encoding flags
    cmd += ['-preset', 'fast', '-crf', '23', '-c:a', 'copy', output_file]
    return cmd

----------------------------------------------------------------------------

Bot logic and handlers

----------------------------------------------------------------------------

default positions sequence

DEFAULT_POS  = ['↖','↑','↗','←','⚪','→','↙','↓','↘'] RES_OPTIONS  = ['480p','720p','1080p','4k']

build the initial menu

def build_menu(): return InlineKeyboardMarkup([ [InlineKeyboardButton("📁 Upload Logo", callback_data="upload_logo")], [InlineKeyboardButton("✅ Apply Watermark", callback_data="apply_watermark")] ])

build the encoding menu

def build_encode_menu(user_data): buttons = [] row = [] for res in RES_OPTIONS: mark = "✅ " if user_data.get('resolution') == res else "" row.append(InlineKeyboardButton(f"{mark}{res}", callback_data=f"set_res|{res}")) buttons.append(row) buttons.append([InlineKeyboardButton("🔧 Custom Encoding 🎛", callback_data="custom_res")]) buttons.append([ InlineKeyboardButton("❌ Close", callback_data="close"), InlineKeyboardButton("◀️ Back", callback_data="back_to_menu") ]) return InlineKeyboardMarkup(buttons)

/start command

def start_cmd(update: Update, context: CallbackContext): update.message.reply_text("Welcome! Use /watermark to start watermarking your video.")

/watermark command

def watermark_cmd(update: Update, context: CallbackContext): context.user_data.clear() update.message.reply_text("Choose an action:", reply_markup=build_menu())

callback query handler

def on_callback(update: Update, context: CallbackContext): q   = update.callback_query q.answer() data= q.data uid = q.from_user.id ud  = context.user_data

if data == 'upload_logo':
    ud['awaiting_logo'] = True
    q.bot.send_message(q.message.chat.id, "📤 Please send your logo now (photo or image file).")
    return

if data == 'apply_watermark':
    # proceed to encoding choices
    ud['resolution'] = 'original'
    q.edit_message_text(
        "Select the Compression Method Below 👇",
        reply_markup=build_encode_menu(ud)
    )
    return

if data.startswith('set_res'):
    _, res = data.split('|', 1)
    ud['resolution'] = res
    # fetch user's logo or fallback
    logo = Config.get_user_logo(uid) or 'logo.png'
    if not os.path.exists(logo):
        q.edit_message_text("❌ No logo found. Please upload first.")
        return
    # build ffmpeg command
    infile  = 'input.mp4'
    outfile = f'output_{uid}.mp4'
    wm_filt = Config.build_watermark_filter(DEFAULT_POS)
    cmd     = Config.build_ffmpeg_cmd(infile, outfile, logo, wm_filt, res)

    q.edit_message_text("🔄 Processing, please wait…")
    try:
        subprocess.run(cmd, check=True)
        q.bot.send_video(q.message.chat.id, video=open(outfile, 'rb'))
        os.remove(outfile)
    except Exception as e:
        logging.error(f"FFmpeg failed: {e}")
        q.bot.send_message(q.message.chat.id, "❌ Video processing failed.")
    return

if data == 'custom_res':
    q.edit_message_text("⚙️ Custom encoding settings not implemented yet.")
    return

if data == 'back_to_menu':
    q.edit_message_text("Choose an action:", reply_markup=build_menu())
    return

if data == 'close':
    q.edit_message_text("Menu closed.")
    return

# fallback
q.edit_message_text("⚠️ Unknown action.")

handler for logo uploads

def logo_handler(update: Update, context: CallbackContext): ud = context.user_data if not ud.get('awaiting_logo'): return msg = update.message uid = msg.from_user.id file_obj = None

if msg.photo:
    file_obj = msg.photo[-1].get_file()
elif msg.document and msg.document.mime_type.startswith('image/'):
    file_obj = msg.document.get_file()
else:
    return

os.makedirs('logos', exist_ok=True)
path = f"logos/logo_{uid}.png"
file_obj.download(path)
Config.save_user_logo(uid, path)
ud['awaiting_logo'] = False

msg.reply_text(
    "✅ Logo uploaded successfully! Tap 'Apply Watermark' to continue.",
    reply_markup=build_menu()
)

main entrypoint

if name == 'main': logging.basicConfig(level=logging.INFO) updater = Updater(Config.BOT_TOKEN) dp = updater.dispatcher

dp.add_handler(CommandHandler('start', start_cmd))
dp.add_handler(CommandHandler('watermark', watermark_cmd))
dp.add_handler(CallbackQueryHandler(on_callback))
dp.add_handler(MessageHandler(Filters.photo | Filters.document.image, logo_handler))

updater.start_polling()
updater.idle()

