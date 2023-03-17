import os
import json
import logging
from telegram.ext import ApplicationBuilder, MessageHandler, filters


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


class Forward22Bot:
    def __init__(self):
        self.forward_mapping = json.loads(os.environ["FORWARD_MAPPING"])
        bot_token = os.environ["BOT_TOKEN"]
        self.app = ApplicationBuilder().token(bot_token).build()
        self.init_handlers()

    def run(self):
        self.app.run_polling()

    def init_handlers(self):
        for config in self.forward_mapping:
            callback = self.get_forward_callback(config["chat_from"], config["channel_to"])
            one_filters = filters.Chat(chat_id=config["chat_from"])
            filter_tags = None
            tags = config.get("tags")
            if tags is not None:
                filter_tags = filters.Regex(tags[0])
                for tag in tags[1:]:
                    filter_tags = filter_tags | filters.Regex(tag)
            if filter_tags is not None:
                one_filters = one_filters & filter_tags
            handler = MessageHandler(one_filters, callback)
            self.app.add_handler(handler)

    @staticmethod
    def get_forward_callback(chat_from, channel_to):
        async def callback(update, context):
            author = update.message.from_user.name
            text = update.message.text
            full_text = f"""
    {author} shares:

    {text}
    """
            sent_message = await context.bot.send_message(chat_id=channel_to, text=full_text)
            new_full_text = f"""
    {full_text}

    Thread: {sent_message.link}
    """
            await context.bot.send_message(chat_id=chat_from, text=new_full_text)
            await update.message.delete()
        return callback


if __name__ == "__main__":
    _bot = Forward22Bot()
    _bot.run()
