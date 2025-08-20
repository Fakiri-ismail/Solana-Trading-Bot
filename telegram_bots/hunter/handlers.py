from telegram_bots.hunter import markup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
from wallet import report
from telegram_bots.hunter import messages


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

    elif query.data == "trading_settings":
        await query.edit_message_text("⚙️ Trading Settings :", reply_markup=markup.trading_settings_markup())
    
    elif query.data == "display_settings":
        msg = messages.trading_settings_msg()
        await query.edit_message_text(msg, reply_markup=markup.display_settings_markup())
    
    elif query.data == "update_settings":
        msg = "🔄 Update Trading Settings:"
        await query.edit_message_text(msg, reply_markup=markup.update_settings_markup())

    elif query.data == "update_sl":
        await query.edit_message_text("Enter your new stop loss\n👉 Example: 0.25 == -25%")
        context.user_data["new_sl"] = True

    elif query.data == "update_tp":
        await query.edit_message_text("Enter your new take profit\n👉 Example: 0.5 == +50%")
        context.user_data["new_tp"] = True

    elif query.data == "main_menu":
        msg = "🤔 What would you like to do ?"
        await query.edit_message_text(msg, reply_markup=markup.start_markup())

# Handle messages
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "/display":
        await start(update, context)

    # elif text == "/refresh":
    #     result = 'get_wallet_token_data()'
    #     await update.message.reply_text(result)

async def number_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("new_sl"):
        try:
            number = float(update.message.text)
            if 0 <= number <= 1:
                await update.message.reply_text(f"✅ New Stop Loss : {number}")
            else:
                await update.message.reply_text("❌ Please enter a number between 0 and 1.")
        except ValueError:
            await update.message.reply_text("❌ Please enter a valid number.")
        finally:
            context.user_data["new_sl"] = False
    elif context.user_data.get("new_tp"):
        try:
            number = float(update.message.text)
            if 0 <= number <= 1:
                await update.message.reply_text(f"✅ New Take Profit : {number}")
            else:
                await update.message.reply_text("❌ Please enter a number between 0 and 1.")
        except ValueError:
            await update.message.reply_text("❌ Please enter a valid number.")
        finally:
            context.user_data["new_tp"] = False
