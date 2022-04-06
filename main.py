import os
import logging
import time
import json
from telegram.ext import Updater
from telegram.ext import MessageHandler
from telegram.ext.filters import Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

FORWARD_MAPPING = json.loads(os.environ["FORWARD_MAPPING"])
BOT_TOKEN = os.environ["BOT_TOKEN"]
COMMENT_CHAT_IDS = [c["channel_comments"] for c in FORWARD_MAPPING]

updater = Updater(token=BOT_TOKEN)
dispatcher = updater.dispatcher

FORWARD_CACHE = {}


def get_forward_callback(chat_from, channel_to):
    def callback(update, context):
        author = update.message.from_user.name
        post_message = context.bot.forward_message(channel_to, chat_from, update.message.message_id)
        new_full_text = f"Thread: {post_message.link}"
        context.bot.send_message(chat_id=chat_from, text=new_full_text, reply_to_message_id=update.message.message_id)
        FORWARD_CACHE[f"{channel_to}_{post_message.forward_date}"] = author
    return callback


def comments_callback(update, context):
    comments_chat = update.message.chat.id
    if comments_chat not in COMMENT_CHAT_IDS:
        return
    channel_id = update.message.sender_chat.id
    channel_message_id = update.message.forward_date
    key = f"{channel_id}_{channel_message_id}"
    while key not in FORWARD_CACHE:
        time.sleep(1)
    text = f"shared by {FORWARD_CACHE[key]}"
    del FORWARD_CACHE[key]
    context.bot.send_message(chat_id=comments_chat, text=text, reply_to_message_id=update.message.message_id)


for config in FORWARD_MAPPING:
    callback = get_forward_callback(config["chat_from"], config["channel_to"])
    filters = Filters.chat(config["chat_from"])
    filter_tags = None
    tags = config.get("tags")
    if tags is not None:
        filter_tags = Filters.regex(tags[0])
        for tag in tags[1:]:
            filter_tags = filter_tags | Filters.regex(tag)
    if filter_tags is not None:
        filters = filters & filter_tags
    handler = MessageHandler(filters, callback)
    dispatcher.add_handler(handler)

comments_filter = Filters.chat()
comments_filter.add_chat_ids(COMMENT_CHAT_IDS)
handler = MessageHandler(comments_filter, comments_callback)
dispatcher.add_handler(handler)

updater.start_polling()
