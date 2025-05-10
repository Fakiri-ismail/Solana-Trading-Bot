import asyncio
from wallet.manager import WalletManager
from exchanges.jupiter.price import getJupPrice
from database.crud.wallet.wallet_tokens_ops import get_all_wallet_tokens
from database.crud.wallet.trading_history_ops import create_trading_history
from database.db_sync.cache_manager import load_wallet_cache, save_wallet_cache, sync_with_db
from global_config import WALLET_PRIV_KEY, WALLET_PUB_KEY, WSOL, USDC


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
                    result = await my_wallet.sell_token(mint=token["mint"], pct_amount=100)
                    if result.get("status"):
                        create_trading_history(
                            mint=token["mint"],
                            symbol=token["symbol"], 
                            usdt_value=token_usd_value,
                            buy_price=float(cache_token["purchase_price"]),
                            sell_price=token_actual_price
                        )
                        print(token["symbol"], "sold!")
                    else:
                        print(token["symbol"], ": Transaction failed!")

    save_wallet_cache(wallet_cache)

    # Update the database
    sync_with_db()


asyncio.run(main())