import requests, logging


base_url = "https://datapi.jup.ag/v1/pools"

def get_toptrending(timeframe: str='24h', params: dict = {}) -> dict:
    """
    Get the top trending pools from Jupiter API ().
        :timeframe: Value can be '5m', '1h', '6h' or '24h'
        **Sort params**
        :params -> limit: Number of pools to return, default is 10.
        :params -> sortBy: 'usdPrice', 'priceChange', 'mcap', 'volume', 'netVolume', 'liquidity', 'holderCount', 'holderChange'.
        :params -> sortDir: Value can be 'desc' or 'asc'.
        **Metrics params**
        :params -> minLiquidity/maxLiquidity: Minimum/Maximum liquidity of the pool ($)
        :params -> minMcap/maxMcap: Minimum/Maximum market cap of the pool ($)
        :params -> minHolderCount/maxHolderCount: Minimum/Maximum number of holders in the pool (Integer)
        **Audit params**
        :params -> minTopHoldersPercentage/maxTopHoldersPercentage: Minimum/Maximum percentage of top holders (Integer e.g. 10)
        :params -> minDevBalancePct/maxDevBalancePct: Minimum/Maximum developer balance percentage (Integer)
        :params -> minTokenAge/maxTokenAge: Minimum/Maximum age of the token in mins
        :return: A dictionary containing the top trending pools.
    """
    params = {**params, 'mintAuthorityDisabled': 'true', 'freezeAuthorityDisabled': 'true'}
    url = f'{base_url}/toptrending/{timeframe}?'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) Python Requests'
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"JUP API : Error fetching top trending pools\n >> {e}")
        return {}


if __name__ == "__main__":
    # Example usage
    params = {
        'limit': 2,
        'minNumNetBuyers1h': 200,
        'minMcap': 800_000,
        'maxMcap': 500_000_000
    }
    toptrading = get_toptrending(timeframe='1h', params=params)
    print(toptrading)