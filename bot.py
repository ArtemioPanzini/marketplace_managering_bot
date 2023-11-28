import os
from dotenv import load_dotenv

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    exit('TELEGRAM_BOT_TOKEN is not set in .env file')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning('No effective chat')
        return
    await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="I'm a bot, please talk to me!")


if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    application.run_polling()
