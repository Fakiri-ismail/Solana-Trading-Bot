from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def start_markup():
    wallet_tokens = InlineKeyboardButton('💳 Wallet Tokens Report', callback_data="wallet_tokens")
    top_trading_tokens = InlineKeyboardButton('🚀 Top Trading Tokens', callback_data="top_trading_tokens")
    trading_settings = InlineKeyboardButton('⚙️ Trading Settings', callback_data="trading_settings")
    buttons = [[wallet_tokens], [top_trading_tokens], [trading_settings]]
    return InlineKeyboardMarkup(buttons)

def top_trading_tokens_markup():
    low_mcap = InlineKeyboardButton('🟡 Low MC', callback_data="low_mcap")
    moyen_mcap = InlineKeyboardButton('🔵 Moyen MC', callback_data="moyen_mcap")
    high_mcap = InlineKeyboardButton('🟢 High MC', callback_data="high_mcap")
    back = InlineKeyboardButton('🔙 Back', callback_data="start_menu")
    buttons = [[low_mcap, moyen_mcap, high_mcap], [back]]
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

