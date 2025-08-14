import asyncio, logging, sys
from telegram_bots.hunter.messenger import HunterBot
from wallet.manager import WalletManager
from helpers.wallet_helpers import get_swap_data
from helpers.utils import setup_logging
from database.db_sync import cache_manager
from database.crud.wallet.wallet_tokens_ops import get_all_wallet_tokens
from database.crud.wallet.trading_history_ops import create_trading_history
from exchanges.jupiter.price import getJupPrice
from global_config import WALLET_PRIV_KEY, WALLET_PUB_KEY, WSOL, USDC


# Init logging
setup_logging('logs/trading.log')
# Reduce Solana RPC logs
logging.getLogger("httpx").setLevel(logging.WARNING)

sol_price = getJupPrice(WSOL)
if not sol_price:
    logging.error("JUP API : Solana price not found")
    sys.exit(1)

async def main():
    # Load the wallet cache
    wallet_cache = cache_manager.load_wallet_cache()
    if not wallet_cache:
        db_wallet_tokens = get_all_wallet_tokens()
        for token in db_wallet_tokens:
            wallet_cache.append({
                "mint": token.mint,
                "symbol": token.symbol,
                "purchase_price": float(token.purchase_price),
                "usdt_value": float(token.usdt_value)
            })

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
        token_actual_price = getJupPrice(token["mint"])
        if not token_actual_price:
            logging.warning(f"JUP API : '{token['symbol']}' price not found ({token['mint']})")
            continue
        token_usd_value = token_actual_price * (token.get("balance", 0) / 10 ** token.get("decimals", 0))

        # New tokens 
        if token["mint"] not in cache_mints:
            # Add token to the cache
            wallet_cache.append({
                "mint": token["mint"],
                "symbol": token["symbol"],
                "purchase_price": token_actual_price,
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

                threshold_upper = 1.8 * float(cache_token["purchase_price"])
                threshold_lower = 0.5 * float(cache_token["purchase_price"])

                if token_actual_price >= threshold_upper or token_actual_price <= threshold_lower:
                    result = await my_wallet.swap_token(in_mint=token["mint"], out_mint=WSOL, pct_amount=100)
                    swap_info ={
                        "status": result.get("status"),
                        "transactionId": result.get("tx_signature"),
                        "symbol": token["symbol"],
                        "swapData": None,
                        "usdValue": 0
                    }
                    if result.get("status"):
                        # Get the swap data
                        swap_data = get_swap_data(result.get("tx_signature"))
                        if swap_data:
                            swap_info["swapData"] = swap_data
                            swap_info["buy_price"] = float(cache_token["purchase_price"])
                            swap_info["sell_price"] = token_actual_price
                            try:
                                swap_sol_value = swap_data['tokenOutput']['amount'] / 10 ** swap_data['tokenOutput']['decimals']
                                swap_info["usdValue"] = round(swap_sol_value * sol_price, 3)
                            except Exception as e:
                                logging.error(f"Error calculating swap value:\n {e}")
                                swap_info["usdValue"] = token_usd_value

                            create_trading_history(
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

    # Update the database
    cache_manager.sync_wallet_with_db()


asyncio.run(main())
