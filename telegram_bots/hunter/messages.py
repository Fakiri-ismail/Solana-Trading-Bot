from helpers import json_helpers, utils
from database.db_sync import cache_manager


def display_trade_settings() -> str:
    trading_params = json_helpers.read_json_file('resources/params/trading_params.json')
    if not trading_params:
        return "⚠️ No trading settings found."
    sl = trading_params.get("stopLoss", 0) * 100
    tp = trading_params.get("takeProfit", 0) * 100
    return f"🔧 Actual Trading Settings :\n\n🔴 Stop Loss : -{sl}%\n🟢 Take Profit : +{tp}%"

def top_trading_tokens_msg(start: int, end: int) -> str:
    top_trading_tokens = cache_manager.load_top_trading_pools_cache()
    if not top_trading_tokens:
        return "⚠️ No data found. Retry later."
    msg = f"🔥​ TOP TRADING TOKENS from the position {start} to {end}:\n\n"
    for token in top_trading_tokens[start-1:end]:
        jup_url = f"https://jup.ag/tokens/{token['mint']}"
        dex_url = f"https://dexscreener.com/solana/{token['mint']}"
        urls = f"🔗 <a href='{dex_url}'>DEX</a> | <a href='{jup_url}'>JUP</a>"
        msg += f"💎 <b>{token['symbol']}</b> : {token['appearance']} times\n"
        msg += f"💰 Mc : <b>{utils.format_number(token['mcap'])}$</b>     {urls}\n\n"
    return msg
