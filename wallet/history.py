import logging
from wallet import report
from wallet.manager import WalletManager
from database.crud.wallet.wallet_history_ops import create_wallet_history
from exchanges.jupiter.price import getJupPrice
from helpers.utils import setup_logging
from global_config import WALLET_PRIV_KEY, WALLET_PUB_KEY, WSOL


# Init logging
setup_logging('logs/wallet_history.log')

if __name__ == "__main__":

    my_wallet = WalletManager(WALLET_PUB_KEY, WALLET_PRIV_KEY)
    wallet_assets = my_wallet.get_assets()
    
    wallet_usd_value = 0
    for token in wallet_assets:
        # Toekn Info
        token_balance = token.get("balance", 0) / 10 ** token.get("decimals", 0)
        token_mint = token.get("mint", "")

        # Token USD Value
        token_price = getJupPrice(token_mint)
        if not token_price:
            token_symbol = token.get("symbol", "")
            logging.warning(f"JUP API : '{token_symbol}' price not found ({token_mint})")
        token_usd_value = token_price * token_balance

        # Wallet USD Value
        wallet_usd_value += token_usd_value
    
    sol_price = getJupPrice(WSOL)
    if not sol_price:
        logging.warning("JUP API : Solana price not found")
    wallet_sol_value = wallet_usd_value / sol_price
    create_wallet_history(
        balance_usdt=round(wallet_usd_value,3),
        balance_sol=round(wallet_sol_value,5)
    )

    # Send the wallet report at the end of the month
    report.send_monthly_wallet_report()
