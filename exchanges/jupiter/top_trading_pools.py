import logging
from datetime import datetime
from exchanges.jupiter import data_api
from database.db_sync import cache_manager
from telegram_bots.hunter.messenger import HunterBot
from telegram_bots.hunter import messages
from helpers import utils


# Init logging
utils.setup_logging('logs/top_trading.log')

# Script runs every 15 minutes using crontab
if __name__ == "__main__":

    # Load top trading pools data
    top_pools_cache = cache_manager.load_top_trading_pools_cache()
    mints_cache = [pool['mint'] for pool in top_pools_cache]

    # Get top trading pools
    params = {
        'minNetVolume1h': 100,
        'minNumNetBuyers1h': 10,
        'minMcap': 800_000,
        'maxMcap': 500_000_000,
        'minHolderCount': 1_000
    }

    # Retry fetching data
    for i in range(3):
        pools = data_api.get_toptrending(timeframe='1h', params=params).get('pools', {})
        if pools:
            break
        logging.warning(f"No pools found : Retry {i + 1} ")

    # Filter and Update Data
    for pool in pools:
        token_info = pool.get('baseAsset', {})
        mint = token_info.get('id')
        if mint:
            if mint in mints_cache:
                result = next((token for token in top_pools_cache if token["mint"] == mint), None)
                # Update Token data
                result['holderCount'] = token_info.get('holderCount')
                result['mcap'] = token_info.get('mcap')
                result['appearance'] +=1
            else:
                # Add New Token
                top_pools_cache.append(
                    {
                        'mint': mint,
                        'symbol': token_info.get('symbol'),
                        'decimals': token_info.get('decimals'),
                        'holderCount': token_info.get('holderCount'),
                        'mcap': token_info.get('mcap'),
                        'appearance': 1
                    }
                )
    # Save top trading poools data
    cache_manager.save_top_trading_pools_cache(top_pools_cache)

    # Send a Telegram message every 3 hours
    last_send_time = cache_manager.get_last_sync_time('top_trading_telegram')
    if last_send_time:
        now = datetime.now()
        delta = (now - last_send_time).total_seconds() > 3600 * 3
        if delta:
            hunter = HunterBot()
            msg = messages.top_trading_tokens_msg(top_pools_cache, start=1, end=10)
            hunter.send_message(msg)
            cache_manager.update_last_sync_time('top_trading_telegram')
    else:
        cache_manager.update_last_sync_time('top_trading_telegram')

    # Synchronize the database and clear the cache every day
    cache_manager.sync_top_trading_pools_with_db(top_pools_cache)
