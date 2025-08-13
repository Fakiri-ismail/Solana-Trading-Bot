from telegram_bots.hunter import markup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
from wallet import report


# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "🤔 What would you like to do ?"
    await update.message.reply_text(msg, reply_markup=markup.start_markup())

# Handle button presses
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "wallet_tokens":
        msg = report.wallet_tokens_report()
        await query.edit_message_text(text=msg, parse_mode=ParseMode.HTML)

    # elif query.data == "option_menu":
    #     await query.edit_message_text("Menu Options :", reply_markup=markup.option_menu_markup())

    # elif query.data == "stats":
    #     await query.edit_message_text("📊 Statistiques:\n- Users: 120\n- Transactions: 45")

    # elif query.data == "back_to_menu":
    #     await start(update, context)

# Handle messages
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "/display":
        await start(update, context)

    # elif text == "/refresh":
    #     result = 'get_wallet_token_data()'
    #     await update.message.reply_text(result)
