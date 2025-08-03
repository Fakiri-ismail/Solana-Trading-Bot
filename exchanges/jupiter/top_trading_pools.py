from exchanges.jupiter import pro
from telegram.hunter_bot import HunterBot

if __name__ == "__main__":

    # hunter = HunterBot()
    top_pools_cache = []
    mints_cache = [pool['mint'] for pool in top_pools_cache]
    
    params = {
        'minNetVolume1h': 100,
        'minNumNetBuyers1h': 0,
        'minMcap': 800_000,
        'maxMcap': 500_000_000
    }
    pools = pro.get_toptrending(timeframe='1h', params=params).get('pools', {})

    top_trading_pools = []
    for pool in pools:
        token_info = pool.get('baseAsset', {})
        mint = token_info.get('id')
        if mint:
            if mint in mints_cache:
                result = next((token for token in top_pools_cache if token["mint"] == mint), None)
                # Update Token data
                result['holderCount'] = token_info.get('holderCount'),
                result['mcap'] = token_info.get('mcap'),
                result['appearance'] +=1
                top_trading_pools.append(result)
            else:
                # Add New Token
                top_trading_pools.append(
                    {
                        'mint': mint,
                        'symbol': token_info.get('symbol'),
                        'decimals': token_info.get('decimals'),
                        'holderCount': token_info.get('holderCount'),
                        'mcap': token_info.get('mcap'),
                        'appearance': 1
                    }
                )

    print(top_trading_pools)