import os, dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram_bots.hunter import handlers


dotenv.load_dotenv()
HUNTER_BOT_TOKEN = os.getenv('HUNTER_BOT_TOKEN')

if __name__ == "__main__":
    app = Application.builder().token(HUNTER_BOT_TOKEN).build()
    app.add_handler(CommandHandler("display", handlers.start))
    app.add_handler(CallbackQueryHandler(handlers.button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.text_handler))
    app.run_polling()
    