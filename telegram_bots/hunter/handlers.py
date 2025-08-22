from telegram import Update, CallbackQuery
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram_bots.hunter import markup
from telegram_bots.hunter import messages
from wallet import report
from helpers import json_helpers


# Temporary storage of user choice
user_data = {}


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
    
    elif query.data == "top_trading_tokens":
        user_data[query.from_user.id] = "topTokens"
        await query.edit_message_text("✏️ Enter an interval :\n   👉 Ex: 5 - 10")

    elif query.data == "trading_settings":
        await query.edit_message_text("⚙️ Trading Settings :", reply_markup=markup.trading_settings_markup())
    
    else:
        if query.data in ["display_settings", "update_settings", "start_menu"]:
            await settings_handler(query)
        
        elif query.data in ["update_sl", "update_tp"]:
            await trade_settings_handler(query)


async def settings_handler(query: CallbackQuery):
    if query.data == "display_settings":
        msg = messages.display_trade_settings()
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Back', callback_data="trading_settings")]])
        await query.edit_message_text(msg, reply_markup=back_markup)

    elif query.data == "update_settings":
        msg = "🔄 which one do you want to update :"
        await query.edit_message_text(msg, reply_markup=markup.update_settings_markup())
    
    elif query.data == "start_menu":
        msg = "🤔 What would you like to do ?"
        await query.edit_message_text(msg, reply_markup=markup.start_markup())


async def trade_settings_handler(query: CallbackQuery):
    if query.data == "update_sl":
        user_data[query.from_user.id] = "stopLoss"
        await query.edit_message_text("✏️ Enter your new stop loss :\n   👉 Ex: 0.25 = -25%")

    elif query.data == "update_tp":
        user_data[query.from_user.id] = "takeProfit"
        await query.edit_message_text("✏️ Enter your new take profit :\n   👉 Ex: 0.5 = +50%")


# Handle message
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the message entered by the user"""
    user_id = update.message.from_user.id
    msg = update.message.text
    choice = user_data[user_id]

    if msg == "/start":
        await start(update, context)

    if choice in ["stopLoss", "takeProfit"]:
        try:
            value = float(msg)
            if 0 < value <= 1:
                result = json_helpers.update_json_record('resources/params/trading_params.json', choice, value)
                if result and choice == "stopLoss":
                    await update.message.reply_text(f"✅ New Stop Loss : -{round(value * 100, 2)}%")
                elif result and choice == "takeProfit":
                    await update.message.reply_text(f"✅ New Take Profit : +{round(value * 100, 2)}%")
                else:
                    await update.message.reply_text("❌ Failed to update settings. Please try again.")
                del user_data[user_id]
            else:
                await update.message.reply_text("❌ Invalid value. Enter a number between 0 and 1.")
        except ValueError:
            await update.message.reply_text("⚠️ Please enter a valid number.")
    
    elif choice == "topTokens":
        inf, sup = msg.replace(" ", "").split('-')
        try:
            inf, sup = int(inf), int(sup)
            if 0 < inf < sup <= 100:
                msg = messages.top_trading_tokens_msg(inf, sup)
                await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
                del user_data[user_id]
            else:
                await update.message.reply_text("❌ Invalid interval. Ensure that the interval is between 0 and 100.")
        except ValueError:
            await update.message.reply_text("⚠️ Please enter a valid interval, EX: 10 - 20")
