import calendar, logging
import matplotlib.pyplot as plt
from datetime import datetime
from database.db_sync import cache_manager
from database.crud.wallet import wallet_history_ops, trading_history_ops
from exchanges.jupiter.price import getJupPrice
from telegram_bots.hunter.messenger import HunterBot
from global_config import WSOL, USDC



def wallet_history_report(start_date: datetime, end_date: datetime):
    # Get wallet histories
    wallet_history_data = wallet_history_ops.get_wallet_history_by_date_range(start_date, end_date)

    # PNL
    first_day_data = wallet_history_data[0]
    last_day_data = wallet_history_data[-1]
    pnl = last_day_data.balance_usdt - first_day_data.balance_usdt
    pnl_pct = (pnl / first_day_data.balance_usdt) * 100 if first_day_data.balance_usdt != 0 else 0

    # Extract data for the chart
    dates = [entry.date for entry in wallet_history_data]
    usdt_balances = [float(entry.balance_usdt) for entry in wallet_history_data]
    s_date = start_date.date().strftime("%d/%m/%Y")
    e_date = end_date.date().strftime("%d/%m/%Y")

    # Plot
    plt.figure(figsize=(10, 5))
    plt.plot(dates, usdt_balances, marker='o')
    plt.title(f"Wallet balance history from {s_date} to {e_date}")
    plt.xlabel("Date")
    plt.ylabel("Balance in USD")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("wallet/history_balance_chart.png")

    return round(pnl, 2), round(pnl_pct, 2)

def trading_history_report(start_date: datetime, end_date: datetime):
    #  Get trading History
    trading_history_data = trading_history_ops.get_trading_history_by_date_range(start_date, end_date)
    win, loss = 0, 0
    for trade in trading_history_data:
        if trade.sell_price > trade.buy_price:
            win += 1
        else:
            loss += 1

    # Rates
    total_trades = len(trading_history_data)
    win_rate = (win / total_trades) * 100
    loss_rate = (loss / total_trades) * 100

    # Graph Data
    labels = [f"Win: {win} ({win_rate:.1f}%)", f"Loss: {loss} ({loss_rate:.1f}%)"]
    sizes = [win, loss]
    colors = ['#4CAF50', '#F44336']

    # Plot
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, startangle=90, colors=colors)

    # Circle to make a "donut" graph
    centre_circle = plt.Circle((0, 0), 0.60, fc='white')
    fig.gca().add_artist(centre_circle)

    # Title
    plt.title("Win/Loss Distribution")
    plt.savefig("wallet/win_rate_chart.png", dpi=300, bbox_inches='tight')

    return round(win_rate, 2)

def wallet_tokens_report():
    wallet_tokens_data = cache_manager.load_wallet_cache()
    if not wallet_tokens_data:
        logging.warning("No data found in wallet cache file.")
        return "❌ No data found."

    data = []
    for token in wallet_tokens_data:
        if token['mint'] in [WSOL, USDC]:
            continue
        token_price = getJupPrice(token["mint"])
        if not token_price:
            continue
        data.append({
            "mint": token['mint'],
            "symbol": token['symbol'],
            "pnl_pct": (token_price - token['buy_price']) / token['buy_price'] * 100
        })
    sorted_data = sorted(data, key=lambda x: x["pnl_pct"], reverse=True)

    msg = '📊 Wallet Report:\n'
    for token in sorted_data:
        moji = "🟢" if token['pnl_pct'] >= 0 else "🔴"
        dex_url = f"https://dexscreener.com/solana/{token['mint']}"
        msg += f"- {moji} <b><a href='{dex_url}'>{token['symbol']}</a></b> : <b>{token['pnl_pct']:.2f}%</b>\n"
    
    if msg == '📊 Wallet Report:\n':
        msg += "❌ No SPL tokens found in the wallet."

    return msg
    

def send_monthly_wallet_report():
    today = datetime.today()
    month_last_day = calendar.monthrange(today.year, today.month)[1]
    if today.day == month_last_day:
        month_name = calendar.month_name[today.month]
        first_day = datetime(today.year, today.month, 1, 0, 0, 0)
        last_day = datetime(today.year, today.month, month_last_day, 23, 59, 59)

        # Generate wallet history report
        pnl, pnl_pct = wallet_history_report(first_day, last_day)

        # Generate trading history report
        win_rate = trading_history_report(first_day, last_day)

        # Send the chart via Telegram
        hunter = HunterBot()
        history_balance_img = "wallet/history_balance_chart.png"
        history_balance_caption = f"Wallet Report for {month_name} {today.year}:\n📈 PNL : <b>{pnl}$</b> ({pnl_pct}%)"
        hunter.send_photo(history_balance_img, history_balance_caption)

        win_rate_img = "wallet/win_rate_chart.png"
        win_rate_caption = f"Win rate for {month_name} {today.year}: <b>{win_rate}%</b>"
        hunter.send_photo(win_rate_img, win_rate_caption)

        logging.info("Wallet history report sent successfully.")
