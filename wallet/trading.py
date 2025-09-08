import asyncio, logging, sys
from telegram_bots.hunter.messenger import HunterBot
from wallet.manager import WalletManager
from database.db_sync import cache_manager
from database.crud.wallet import trading_history_ops
from exchanges.jupiter.price import getJupPrice
from helpers import json_helpers, utils, wallet_helpers
from global_config import WALLET_PRIV_KEY, WALLET_PUB_KEY, WSOL, USDC


# Init logging
utils.setup_logging('logs/trading.log')
logging.getLogger("httpx").setLevel(logging.WARNING)    # Reduce Solana RPC logs

# Trading Parameters
trading_params = json_helpers.read_json_file('resources/params/trading_params.json')
if not trading_params:
    logging.warning("Trading parameters not found. Please set them in 'resources/params/trading_params.json'")
    trading_params = {"stopLoss": 0.5, "takeProfit": 0.8}  # Default values


sol_price = getJupPrice(WSOL)
if not sol_price:
    logging.error("JUP API : Solana price not found")
    sys.exit(1)


async def trading_bot():
    # Load the wallet cache
    wallet_cache = cache_manager.load_wallet_cache()

    # Update the wallet cache
    wallet_cache = cache_manager.update_wallet_cache(wallet_cache)

    for token in wallet_cache:
        # Skip USDC/WSOL
        if token["mint"] in [WSOL, USDC]:
            continue

        # Trading Parameters
        buy_price = float(token["buy_price"])
        take_profit_price = buy_price * (1 + trading_params["takeProfit"])
        stop_loss_price = buy_price * (1 - trading_params["stopLoss"])

        token_price = getJupPrice(token["mint"])
        if not token_price:
            continue

        if token_price >= take_profit_price or token_price <= stop_loss_price:
            my_wallet = WalletManager(WALLET_PUB_KEY, WALLET_PRIV_KEY)
            # Swap the token
            result = await my_wallet.swap_token(in_mint=token["mint"], out_mint=WSOL, pct_amount=100)
            # Generate swap info
            token_info = {**token, "sell_price": token_price}
            swap_info = generate_swap_info(result, token_info)
            if swap_info['swapData']:
                trading_history_ops.create_trading_history(
                    mint=token["mint"],
                    symbol=token["symbol"], 
                    buy_price=swap_info["buy_price"],
                    sell_price=swap_info["sell_price"],
                    usdt_value=swap_info["usdValue"]
                )

            # Send telegram message
            hunter = HunterBot()
            hunter.send_swap_message(swap_info)

    # sync cache with database every 3 hours
    cache_manager.sync_wallet_with_db(wallet_cache, iteration_time=10800)


def generate_swap_info(swap_result, token_info):
    swap_info ={
        "status": swap_result.get("status"),
        "transactionId": swap_result.get("tx_signature"),
        "symbol": token_info["symbol"],
        "buy_price": token_info["buy_price"],
        "sell_price": token_info["sell_price"],
        "swapData": None,
        "usdValue": 0
    }
    if swap_info["status"]:
        # Get the swap data
        swap_data = wallet_helpers.get_swap_data(swap_result.get("tx_signature"))
        if swap_data:
            swap_info["swapData"] = swap_data
            try:
                token_decimals = wallet_helpers.get_token_info(token_info["mint"]).decimals
                swap_info["usdValue"]  = token_info["sell_price"] * (token_info["balance"] / 10 ** token_decimals)
            except Exception as e:
                logging.error(f"Error calculating swap value:\n {e}")
    
    return swap_info


# Script runs every 2 minutes using crontab
asyncio.run(trading_bot())
