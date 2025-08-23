from helpers import json_helpers, utils


def display_trade_settings() -> str:
    trading_params = json_helpers.read_json_file('resources/params/trading_params.json')
    if not trading_params:
        return "⚠️ No trading settings found."
    sl = trading_params.get("stopLoss", 0) * 100
    tp = trading_params.get("takeProfit", 0) * 100
    return f"🔧 Actual Trading Settings :\n\n🔴 Stop Loss : -{sl}%\n🟢 Take Profit : +{tp}%"

def top_trading_tokens_msg(top_tokens, start: int = 1, end: int = 100, mcp_type: str = None) -> str:
    if not top_tokens:
        return "⚠️ No data found. Retry later."
    
    if mcp_type:
        mcp_filter = {'low_mcap': (0, 5_000_000), 
                      'moyen_mcap': (5_000_000, 50_000_000), 
                      'high_mcap': (50_000_000, float('inf'))}
        top_tokens = [token for token in top_tokens if mcp_filter[mcp_type][0] < token["mcp"] <= mcp_filter[mcp_type][1]]

    top_tokens = sorted(top_tokens, key=lambda d: d["appearance"], reverse=True)
    msg = f"🔥​ TOP TRADING TOKENS from the position {start} to {end}:\n\n"
    i = start
    for token in top_tokens[start-1:end]:
        jup_url = f"https://jup.ag/tokens/{token['mint']}"
        dex_url = f"https://dexscreener.com/solana/{token['mint']}"
        urls = f"🔗 <a href='{dex_url}'>DEX</a> | <a href='{jup_url}'>JUP</a>"
        msg += f"<b>{i} - {token['symbol']}</b> : {token['appearance']} times\n"
        msg += f"💰 Mc : <b>{utils.format_number(token['mcap'])}$</b>     {urls}\n\n"
        i += 1
    return msg
