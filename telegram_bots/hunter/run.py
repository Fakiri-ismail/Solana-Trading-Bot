import os, dotenv
from helpers import utils
from telegram_bots.hunter import handlers
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, filters


dotenv.load_dotenv()
HUNTER_BOT_TOKEN = os.getenv('HUNTER_BOT_TOKEN')

# Init logging
utils.setup_logging('logs/hunter.log')

if __name__ == "__main__":
    app = Application.builder().token(HUNTER_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CallbackQueryHandler(handlers.button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.text_handler))
    app.run_polling()
    