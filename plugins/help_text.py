import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os

from config import Config
# the Strings used for this "thing"
from translation import Translation

from pyrogram import filters
from database.adduser import AddUser
from pyrogram import Client as Clinton
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


@Clinton.on_message(filters.private & filters.command(["help"]))
async def help_user(bot, update):
    # logger.info(update)
    await AddUser(bot, update)
    try:
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.HELP_USER,
            parse_mode="html",
            disable_web_page_preview=True,
            reply_to_message_id=update.message_id
        )
    except AttributeError as e:
         logger.error(f"Failed to get translation string: {e}")
         await bot.send_message(
            chat_id=update.chat.id,
            text="Failed to get translation string",
            reply_to_message_id=update.message_id
        )


@Clinton.on_message(filters.private & filters.command(["start"]))
async def start(bot, update):
    # logger.info(update)
    await AddUser(bot, update)
    try:
         await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.START_TEXT.format(update.from_user.mention),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Fork Repo ⚡", url="https://github.com/LazyDeveloperr/MissPerfect-URL-BOT"
                        ),
                        InlineKeyboardButton("Dev Channel 👨🏻‍💻", url="https://telegram.me/LazyDeveloper"),
                    ],
                    [InlineKeyboardButton("LazyDeveloper 👨‍⚖️", url="https://t.me/mRiderDM")],
                ]
            ),
            reply_to_message_id=update.message_id
        )
    except AttributeError as e:
         logger.error(f"Failed to get translation string: {e}")
         await bot.send_message(
            chat_id=update.chat.id,
            text="Failed to get translation string",
            reply_to_message_id=update.message_id
        )