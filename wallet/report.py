import calendar
import matplotlib.pyplot as plt
from datetime import datetime
from telegram.hunter_bot import HunterBot
from database.crud.wallet import wallet_history_ops


def send_wallet_history_report():
    today = datetime.today()
    month_last_day = calendar.monthrange(today.year, today.month)[1]
    if today.day == month_last_day:
        # Get wallet histories
        first_day = datetime(today.year, today.month, 1, 0, 0, 0)
        last_day = datetime(today.year, today.month, month_last_day, 23, 59, 59)
        wallet_history_data = wallet_history_ops.get_wallet_history_by_date_range(first_day, last_day)

        # PNL
        first_day_data = wallet_history_data[0]
        last_day_data = wallet_history_data[-1]
        pnl = last_day_data.balance_usdt - first_day_data.balance_usdt
        pnl_pct = (pnl / first_day_data.balance_usdt) * 100 if first_day_data.balance_usdt != 0 else 0
        # Extract data for the chart
        dates = [entry.date for entry in wallet_history_data]
        usdt_balances = [float(entry.balance_usdt) for entry in wallet_history_data]

        # Chart
        month_name = calendar.month_name[today.month]
        plt.figure(figsize=(10, 5))
        plt.plot(dates, usdt_balances, marker='o')
        plt.title(f"Wallet Balance - {month_name} {today.year}")
        plt.xlabel("Date")
        plt.ylabel("Wallet Balance (in $)")
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("wallet/wallet_balance_chart.png")

        # Send the chart via Telegram
        hunter = HunterBot()
        photo_path = "wallet/wallet_balance_chart.png"
        caption = f"Wallet Report for {month_name} {today.year}:\n📈 PNL : {pnl:.2f}$ ({pnl_pct:.2f}%)"
        hunter.send_photo(photo_path, caption)
        print("Wallet history report sent successfully.")
