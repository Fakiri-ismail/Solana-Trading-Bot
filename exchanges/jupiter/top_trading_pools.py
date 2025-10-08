import logging
from datetime import datetime
from exchanges.jupiter import data_api
from database.cache import cache_manager
from telegram_bots.hunter.messenger import HunterBot
from telegram_bots.hunter import messages
from helpers import utils


# Init logging
utils.setup_logging('logs/top_trading.log')

# Script runs every 15 minutes using crontab
if __name__ == "__main__":

    # Load top trading assets data
    top_assets_cache = cache_manager.load_top_trading_assets_cache()
    mints_cache = [asset['mint'] for asset in top_assets_cache]

    # Get top trading assets
    params = {
        'minNetVolume1h': 100,
        'minNumNetBuyers1h': 10,
        'minMcap': 700_000,
        'maxMcap': 500_000_000,
        'minHolderCount': 1_000
    }

    # Retry fetching data
    for i in range(3):
        assets = data_api.get_toptrending(timeframe='1h', params=params)
        if assets:
            break
        logging.warning(f"No assets found : Retry {i + 1} ")

    # Filter and Update Data
    for asset in assets:
        #token_info = asset.get('baseAsset', {})
        mint = asset.get('id')
        if mint:
            if mint in mints_cache:
                result = next((token for token in top_assets_cache if token["mint"] == mint), None)
                # Update Token data
                result['holderCount'] = asset.get('holderCount')
                result['mcap'] = asset.get('mcap')
                result['appearance'] +=1
            else:
                # Add New Token
                top_assets_cache.append(
                    {
                        'mint': mint,
                        'symbol': asset.get('symbol'),
                        'decimals': asset.get('decimals'),
                        'holderCount': asset.get('holderCount'),
                        'mcap': asset.get('mcap'),
                        'appearance': 1
                    }
                )
    # Save top trading assets data
    cache_manager.save_top_trading_assets_cache(top_assets_cache)

    # Send a Telegram message every 6 hours
    last_send_time = cache_manager.get_last_sync_time('top_trading_telegram')
    if last_send_time:
        now = datetime.now()
        delta = (now - last_send_time).total_seconds() > 3600 * 6
        if delta:
            hunter = HunterBot()
            high_mcap_msg = messages.top_trading_tokens_msg(top_assets_cache, end=5, mcp_type='high_mcap')
            moyen_mcap_msg = messages.top_trading_tokens_msg(top_assets_cache, end=5, mcp_type='moyen_mcap')
            low_mcap_msg = messages.top_trading_tokens_msg(top_assets_cache, end=5, mcp_type='low_mcap')
            msg = high_mcap_msg + "\n" + moyen_mcap_msg + "\n" + low_mcap_msg
            hunter.send_message(msg)
            cache_manager.update_last_sync_time('top_trading_telegram')
    else:
        cache_manager.update_last_sync_time('top_trading_telegram')

    # Synchronize the database and clear the cache every day
    cache_manager.sync_top_trading_assets_with_db(top_assets_cache)
