import os
import logging
from telegram.ext import Updater
from telegram.ext import MessageHandler
from telegram.ext.filters import Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

CHAT_ID_FROM = int(os.environ["CHAT_ID_FROM"])
CHANNEL_ID_TO = int(os.environ["CHANNEL_ID_TO"])
BOT_TOKEN = os.environ["BOT_TOKEN"]

updater = Updater(token=BOT_TOKEN)
dispatcher = updater.dispatcher


def forward_forum22_message(update, context):
    author = update.message.from_user.name
    text = update.message.text
    full_text = f"""
{author} asks:

{text}
"""
    sent_message = context.bot.send_message(chat_id=CHANNEL_ID_TO, text=full_text)
    new_full_text = f"""
{full_text}

Thread: {sent_message.link}
"""
    context.bot.send_message(chat_id=CHAT_ID_FROM, text=new_full_text)
    update.message.delete()


forum22_message_handler = MessageHandler(Filters.chat(CHAT_ID_FROM) & Filters.regex("#форум"),
                                         forward_forum22_message)
dispatcher.add_handler(forum22_message_handler)

updater.start_polling()
