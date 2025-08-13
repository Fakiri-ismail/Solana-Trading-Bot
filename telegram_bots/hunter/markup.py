from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import ReplyKeyboardMarkup, KeyboardButton


def start_markup():
    buttons = [[InlineKeyboardButton('💳 Wallet Tokens', callback_data="wallet_tokens")]]
    return InlineKeyboardMarkup(buttons)

# def option_menu_markup():
#     stats = InlineKeyboardButton('📊 Statistiques', callback_data="stats")
#     back = InlineKeyboardButton('🔙 Retour', callback_data="main_menu")
#     buttons = [[stats, back]]
#     return InlineKeyboardMarkup(buttons)
