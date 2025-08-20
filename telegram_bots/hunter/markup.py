from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from helpers import json_helpers
from telegram import ReplyKeyboardMarkup, KeyboardButton


def start_markup():
    buttons = [[InlineKeyboardButton('💳 Wallet Tokens', callback_data="wallet_tokens"),
                InlineKeyboardButton('⚙️ Trading Settings', callback_data="trading_settings")]]
    return InlineKeyboardMarkup(buttons)

def trading_settings_markup():
    display_settings = InlineKeyboardButton('🔧 Display Settings', callback_data="display_settings")
    update_settings = InlineKeyboardButton('🔄 Update Settings', callback_data="update_settings")
    back = InlineKeyboardButton('🔙 Back', callback_data="main_menu")
    buttons = [[display_settings, update_settings], [back]]
    return InlineKeyboardMarkup(buttons)

def display_settings_markup():
    buttons = [[InlineKeyboardButton('🔙 Back', callback_data="trading_settings")]]
    return InlineKeyboardMarkup(buttons)

def update_settings_markup():
    trading_params = json_helpers.read_json_file('resources/params/trading_params.json')
    sl = trading_params.get("stopLoss", 0) * 100
    tp = trading_params.get("takeProfit", 0) * 100
    sl_button = InlineKeyboardButton(f'🔴 Stop Loss : -{sl}%', callback_data="update_sl")
    tp_button = InlineKeyboardButton(f'🟢 Take Profit : +{tp}%', callback_data="update_tp")
    back = InlineKeyboardButton('🔙 Back', callback_data="trading_settings")
    buttons = [[sl_button], [tp_button], [back]]
    return InlineKeyboardMarkup(buttons)