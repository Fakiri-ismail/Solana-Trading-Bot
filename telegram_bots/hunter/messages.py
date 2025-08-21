from helpers import json_helpers


def display_trade_settings() -> str:
    trading_params = json_helpers.read_json_file('resources/params/trading_params.json')
    if not trading_params:
        return "⚠️ No trading settings found."
    sl = trading_params.get("stopLoss", 0) * 100
    tp = trading_params.get("takeProfit", 0) * 100
    return f"🔧 Actual Trading Settings :\n\n🔴 Stop Loss : -{sl}%\n🟢 Take Profit : +{tp}%"
