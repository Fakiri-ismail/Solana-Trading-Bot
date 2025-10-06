import logging
from database.cache import cache_manager
from exchanges.jupiter.price import get_price
from helpers import wallet_helpers

def old_wallet_tokens_report():
    wallet_tokens_data = cache_manager.load_wallet_cache()
    if not wallet_tokens_data:
        logging.warning("No data found in wallet cache file.")
        return "❌ No data found."

    data = []
    wallet_value = 0
    for token in wallet_tokens_data:
        token_price = get_price(token["mint"])
        if not token_price:
            continue

        token_decimals = wallet_helpers.get_token_info(token["mint"]).decimals
        token_value = token_price * (token["balance"] / 10 ** token_decimals)
        data.append({
            "mint": token['mint'],
            "symbol": token['symbol'],
            "value": token_value,
            "pnl_pct": (token_price - token['buy_price']) / token['buy_price'] * 100
        })
        wallet_value += token_value
    sorted_data = sorted(data, key=lambda x: x["pnl_pct"], reverse=True)

    msg = f'📊 Wallet Report\n'
    for token in sorted_data:
        emoji = "🟢" if token['pnl_pct'] >= 0 else "🔴"
        sign = "+" if token['pnl_pct'] >= 0 else ""
        dex_url = f"https://dexscreener.com/solana/{token['mint']}"
        msg += f"- {emoji} <b><a href='{dex_url}'>{token['symbol']}</a></b> : {token['value']:.2f}$  ({sign}{token['pnl_pct']:.1f}%)\n"

    msg += f"💰 Total: <b>{wallet_value:.2f}$</b>\n"
    return msg
