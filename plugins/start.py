import asyncio
import shutil
import humanize
from time import sleep
from config import Config
from script import Txt
from helper.database import db
from pyrogram.errors import FloodWait
from pyrogram import Client, filters, enums
from .check_user_status import handle_user_status
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

@Client.on_message((filters.private | filters.group))
async def _(bot: Client, cmd: Message):
    await handle_user_status(bot, cmd)

@Client.on_message((filters.private | filters.group) & filters.command('start'))
async def Handle_StartMsg(bot: Client, msg: Message):
    Snowdev = await msg.reply_text(text='**Please Wait...**', reply_to_message_id=msg.id)

    if msg.chat.type == enums.ChatType.SUPERGROUP and not await db.is_user_exist(msg.from_user.id):
        btn = [
            [InlineKeyboardButton(text='⚡ BOT PM', url='https://t.me/EncodeMarkRenameBot')],
            [InlineKeyboardButton(text='💻 Dᴇᴠᴇʟᴏᴘᴇʀ', url='https://t.me/BIG_FiiSH')]
        ]
        await Snowdev.edit(text=Txt.GROUP_START_MSG.format(msg.from_user.mention), reply_markup=InlineKeyboardMarkup(btn))
    else:
        btn = [
            [InlineKeyboardButton(text='❗ Hᴇʟᴘ', callback_data='help'), InlineKeyboardButton(text='ℹ️ Aʙᴏᴜᴛ', callback_data='about')],
            [InlineKeyboardButton(text='📢 Uᴘᴅᴀᴛᴇs', url='https://t.me/BIDHAANBOTS'), InlineKeyboardButton(text='💻 Dᴇᴠᴇʟᴏᴘᴇʀ', url='https://t.me/BIG_FiiSH')]
        ]
        await Snowdev.delete()
        if Config.START_PIC:
            await msg.reply_photo(
                photo=Config.START_PIC,
                caption=Txt.PRIVATE_START_MSG.format(msg.from_user.mention),
                reply_markup=InlineKeyboardMarkup(btn),
                reply_to_message_id=msg.id
            )
        else:
            await msg.reply_text(
                text=Txt.PRIVATE_START_MSG.format(msg.from_user.mention),
                reply_markup=InlineKeyboardMarkup(btn),
                reply_to_message_id=msg.id
            )

@Client.on_message((filters.private | filters.group) & (filters.document | filters.audio | filters.video))
async def Files_Option(bot: Client, message: Message):
    SnowDev = await message.reply_text(text='**Please Wait**', reply_to_message_id=message.id)

    if message.chat.type == enums.ChatType.SUPERGROUP and not await db.is_user_exist(message.from_user.id):
        btn = [
            [InlineKeyboardButton(text='⚡ BOT PM', url='https://t.me/EncodeMarkRenameBot')],
            [InlineKeyboardButton(text='💻 Dᴇᴠᴇʟᴏᴘᴇʀ', url='https://t.me/BIG_FiiSH')]
        ]
        return await SnowDev.edit(text=Txt.GROUP_START_MSG.format(message.from_user.mention), reply_markup=InlineKeyboardMarkup(btn))

    file = getattr(message, message.media.value)
    filename = file.file_name
    filesize = humanize.naturalsize(file.file_size)

    try:
        text = f"**__What do you want me to do with this file?__**\n\n**File Name:** `{filename}`\n**File Size:** `{filesize}`"
        buttons = [
            [InlineKeyboardButton("✏️ Rename", callback_data=f"rename-{message.from_user.id}")],
            [InlineKeyboardButton("🗜️ Compress", callback_data=f"compress-{message.from_user.id}")]
        ]
        await SnowDev.edit(text=text, reply_markup=InlineKeyboardMarkup(buttons))
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await SnowDev.delete()
        await Files_Option(bot, message)  # Retry gracefully
    except Exception as e:
        print(f"[ERROR] {e}")

@Client.on_message((filters.private | filters.group) & filters.command('cancel'))
async def cancel_process(bot: Client, message: Message):
    try:
        shutil.rmtree(f"encode/{message.from_user.id}", ignore_errors=True)
        shutil.rmtree(f"ffmpeg/{message.from_user.id}", ignore_errors=True)
        shutil.rmtree(f"Renames/{message.from_user.id}", ignore_errors=True)
        shutil.rmtree(f"Metadata/{message.from_user.id}", ignore_errors=True)
        shutil.rmtree(f"Screenshot_Generation/{message.from_user.id}", ignore_errors=True)
        return await message.reply_text(text="**Canceled All On Going Processes ✅**")
    except Exception as e:
        print(f"[CANCEL ERROR] {e}")
