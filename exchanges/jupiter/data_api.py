import requests, logging
from helpers import utils
from global_config import WALLET_PUB_KEY


base_url = "https://datapi.jup.ag/v1"

def get_toptrending(timeframe: str='24h', params: dict = {}) -> list:
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
    url = f'{base_url}/assets/toptrending/{timeframe}?'
    headers = {'User-Agent': utils.get_random_user_agent()}
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"JUP API : Error fetching top trending pools\n >> {e}")
        return []

def search(query: str) -> list:
    """
    Search for a token using the Jupiter API.
        :query: The search query (token symbol or name).
        :return: A dictionary containing the search results.
    """
    params = {'query': query}
    url = f'{base_url}/assets/search?'
    headers = {'User-Agent': utils.get_random_user_agent()}
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()[0] if len(response.json()) != 0 else {}
    except requests.RequestException as e:
        logging.error(f"JUP API : Error searching for token '{query}'\n >> {e}")
        return {}

def get_wallet_data(wallet_pub_key: str=WALLET_PUB_KEY) -> dict:
    """
    Get the wallet data from Jupiter API.
        :wallet_pub_key: The public key of the wallet.
        :return: A dictionary containing the wallet data.
    """
    params = {'addresses': wallet_pub_key, 'includeClosed': 'false'}
    url = f'{base_url}/pnl?'
    headers = {'User-Agent': utils.get_random_user_agent()}
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json().get(wallet_pub_key, {})
    except requests.RequestException as e:
        logging.error(f"JUP API : Error fetching wallet data\n >> {e}")
        return {}

if __name__ == "__main__":
    # Example usage

    # Get top trending pools
    # params = {
    #     'limit': 2,
    #     'minNumNetBuyers1h': 200,
    #     'minMcap': 800_000,
    #     'maxMcap': 500_000_000
    # }
    # toptrading = get_toptrending(timeframe='1h', params=params)
    # print(toptrading)

    # Get wallet PnL
    # wallet_pnl = get_wallet_data()
    # print(wallet_pnl['So11111111111111111111111111111111111111111'])

    # Search for a token
    print(search("B32hGG9q55tcik9gNBPuoSHTnqFtpKYLpsApFyvCpump"))
    