import asyncio
from wallet.manager import WalletManager
from wallet.helpers import get_swap_data
from exchanges.jupiter.price import getJupPrice
from database.crud.wallet.wallet_tokens_ops import get_all_wallet_tokens
from database.crud.wallet.trading_history_ops import create_trading_history
from database.db_sync.cache_manager import load_wallet_cache, save_wallet_cache, sync_with_db
from telegram.hunter_bot import HunterBot
from global_config import WALLET_PRIV_KEY, WALLET_PUB_KEY, WSOL, USDC


hunter = HunterBot()
sol_price = float(getJupPrice(WSOL).get(WSOL, {}).get("price", 0))
if not sol_price:
    raise Exception(f"Price not found for {WSOL}")

async def main():
    # Load the wallet cache
    wallet_cache = load_wallet_cache()
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
        mint_price = getJupPrice(token["mint"]).get(token["mint"], {}).get("price", 0)
        if not mint_price:
            print(f"Price not found for {token['symbol']}")
            continue
        token_actual_price = float(mint_price)
        token_usd_value = token_actual_price * (token.get("balance", 0) / 10 ** token.get("decimals", 0))
        # Check if token already exists in cache
        if token["mint"] not in cache_mints:
            # Add new tokens to the cache
            wallet_cache.append({
                "mint": token["mint"],
                "symbol": token["symbol"],
                "purchase_price": token_actual_price,
                "usdt_value": token_usd_value
            })

        # Old tokens  
        else:
            if token["mint"] in [WSOL, USDC]:
                continue
            
            cache_token = next((t for t in wallet_cache if t["mint"] == token["mint"]), None)
            if cache_token:
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
                        swap_usdt_value = token_usd_value
                        if swap_data:
                            swap_info["swapData"] = swap_data
                            try:
                                swap_sol_value = swap_data['tokenOutput']['amount'] / 10 ** swap_data['tokenOutput']['decimals']
                                swap_usdt_value = round(swap_sol_value * sol_price, 3)
                                swap_info["usdValue"] = swap_usdt_value
                            except Exception as e:
                                print(f"Error calculating swap value:\n {e}")
                                swap_info["usdValue"] = token_usd_value

                            create_trading_history(
                                mint=token["mint"],
                                symbol=token["symbol"], 
                                usdt_value=swap_usdt_value,
                                buy_price=float(cache_token["purchase_price"]),
                                sell_price=token_actual_price
                            )

                    # Send telegram message
                    hunter.send_swap_message(swap_info)

    save_wallet_cache(wallet_cache)

    # Update the database
    sync_with_db()


asyncio.run(main())