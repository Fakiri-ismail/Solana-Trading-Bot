from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def start_markup():
    wallet_tokens = InlineKeyboardButton('💳 Wallet Tokens Report', callback_data="wallet_tokens")
    trading_settings = InlineKeyboardButton('⚙️ Trading Settings', callback_data="trading_settings")
    buttons = [[wallet_tokens], [trading_settings]]
    return InlineKeyboardMarkup(buttons)

def trading_settings_markup():
    display_settings = InlineKeyboardButton('🔧 Display Settings', callback_data="display_settings")
    update_settings = InlineKeyboardButton('🔄 Update Settings', callback_data="update_settings")
    back = InlineKeyboardButton('🔙 Back', callback_data="start_menu")
    buttons = [[display_settings, update_settings], [back]]
    return InlineKeyboardMarkup(buttons)

def update_settings_markup():
    sl_button = InlineKeyboardButton(f'🔴 Stop Loss', callback_data="update_sl")
    tp_button = InlineKeyboardButton(f'🟢 Take Profit', callback_data="update_tp")
    back = InlineKeyboardButton('🔙 Back', callback_data="trading_settings")
    buttons = [[sl_button, tp_button], [back]]
    return InlineKeyboardMarkup(buttons)
