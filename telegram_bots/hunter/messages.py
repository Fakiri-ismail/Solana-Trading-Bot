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
    
    type_name = ""
    if mcp_type:
        mcp_filter = {'low_mcap': (0, 10_000_000, "LOW MCP - "), 
                      'moyen_mcap': (10_000_000, 100_000_000, "MOYEN MCP - "), 
                      'high_mcap': (100_000_000, float('inf'), "HIGH MCP - ")}
        top_tokens = [token for token in top_tokens if mcp_filter[mcp_type][0] < token["mcap"] <= mcp_filter[mcp_type][1]]
        type_name = mcp_filter[mcp_type][2]

    top_tokens = sorted(top_tokens, key=lambda d: d["appearance"], reverse=True)
    msg = f"🔥​ <b>{type_name}TOP TRADING TOKENS</b>\nFrom the position <b>{start}</b> to <b>{end}</b>:\n\n"
    i = start
    for token in top_tokens[start-1:end]:
        jup_url = f"https://jup.ag/tokens/{token['mint']}"
        dex_url = f"https://dexscreener.com/solana/{token['mint']}"
        urls = f"🔗 <a href='{dex_url}'>DEX</a> | <a href='{jup_url}'>JUP</a>"
        msg += f"<b>{i} - {token['symbol']}</b> : {token['appearance']} times\n"
        msg += f"💰 Mc : <b>{utils.format_number(token['mcap'])}$</b>     {urls}\n"
        i += 1
    return msg
