import os
import json
import logging
from telegram.ext import Updater
from telegram.ext import MessageHandler
from telegram.ext.filters import Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

FORWARD_MAPPING = json.loads(os.environ["FORWARD_MAPPING"])
BOT_TOKEN = os.environ["BOT_TOKEN"]

updater = Updater(token=BOT_TOKEN)
dispatcher = updater.dispatcher


def get_forward_callback(chat_from, channel_to):
    def callback(update, context):
        author = update.message.from_user.name
        text = update.message.text
        full_text = f"""
{author} shares:

{text}
"""
        sent_message = context.bot.send_message(chat_id=channel_to, text=full_text)
        new_full_text = f"""
{full_text}

Thread: {sent_message.link}
"""
        context.bot.send_message(chat_id=chat_from, text=new_full_text)
        update.message.delete()
    return callback


for config in FORWARD_MAPPING:
    callback = get_forward_callback(config["chat_from"], config["channel_to"])
    filters = Filters.chat(config["chat_from"])
    filter_tags = None
    tags =  config.get("tags")
    if tags is not None:
        filter_tags = Filters.regex(tags[0])
        for tag in tags[1:]:
            filter_tags = filter_tags | Filters.regex(tag)
    if filter_tags is not None:
        filters = filters & filter_tags
    handler = MessageHandler(filters, callback)
    dispatcher.add_handler(handler)

updater.start_polling()
