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
    
    # Sol wallet
    my_wallet = WalletManager(WALLET_PUB_KEY, WALLET_PRIV_KEY)
    wallet_assets = my_wallet.get_assets()
    wallet_mints = [token.get("mint", "") for token in wallet_assets]

    # Update the wallet cache
    # Remove tokens that are not in the wallet anymore
    for token in wallet_cache:
        if token["mint"] not in wallet_mints:
            wallet_cache.remove(token)

    cache_mints = [t["mint"] for t in wallet_cache]
    for token in wallet_assets:
        actual_price = getJupPrice(token["mint"])
        if not actual_price:
            continue
        token_usd_value = actual_price * (token.get("balance", 0) / 10 ** token.get("decimals", 0))

        # New tokens 
        if token["mint"] not in cache_mints:
            # Add token to the cache
            wallet_cache.append({
                "mint": token["mint"],
                "symbol": token["symbol"],
                "buy_price": actual_price,
                "usdt_value": token_usd_value
            })

        # Old tokens  
        else:            
            cache_token = next((t for t in wallet_cache if t["mint"] == token["mint"]), None)
            if cache_token:
                if token["mint"] in [WSOL, USDC]:
                    # Update USDC/WSOL value
                    cache_token['usdt_value'] = token_usd_value
                    continue
                
                # Check if the price is above take profit or below stop loss
                buy_price = float(cache_token["buy_price"])
                take_profit_price = buy_price * (1 + trading_params["takeProfit"])
                stop_loss_price = buy_price * (1 - trading_params["stopLoss"])

                if actual_price >= take_profit_price or actual_price <= stop_loss_price:
                    result = await my_wallet.swap_token(in_mint=token["mint"], out_mint=WSOL, pct_amount=100)
                    swap_info = generate_swap_info(result, buy_price, actual_price, token["symbol"], token_usd_value)
                    if swap_info['swapData']:
                        trading_history_ops.create_trading_history(
                            mint=token["mint"],
                            symbol=token["symbol"], 
                            usdt_value=swap_info["usdValue"],
                            buy_price=swap_info["buy_price"],
                            sell_price=swap_info["sell_price"]
                        )

                    # Send telegram message
                    hunter = HunterBot()
                    hunter.send_swap_message(swap_info)

    # Save wallet cache
    cache_manager.save_wallet_cache(wallet_cache)

    # sync cache with database every hour
    cache_manager.sync_wallet_with_db()


def generate_swap_info(swap_result, buy_price, actual_price, symbol, token_usd_value):
    swap_info ={
        "status": swap_result.get("status"),
        "transactionId": swap_result.get("tx_signature"),
        "symbol": symbol,
        "swapData": None,
    }
    if swap_result.get("status"):
        # Get the swap data
        swap_data = wallet_helpers.get_swap_data(swap_result.get("tx_signature"))
        if swap_data:
            swap_info["swapData"] = swap_data
            swap_info["buy_price"] = buy_price
            swap_info["sell_price"] = actual_price
            try:
                swap_sol_value = swap_data['tokenOutput']['amount'] / 10 ** swap_data['tokenOutput']['decimals']
                swap_info["usdValue"] = round(swap_sol_value * sol_price, 3)
            except Exception as e:
                logging.error(f"Error calculating swap value:\n {e}")
                swap_info["usdValue"] = token_usd_value
    
    return swap_info


# Script runs every 2 minutes using crontab
asyncio.run(trading_bot())
