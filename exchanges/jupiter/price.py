import requests, logging
from helpers import utils
from global_config import USDC


def get_price(mint: str) -> float:
    """
    Retry 3 times to get the price of a token using the Jupiter API
    """
    for i in range(3):
        price = getJupPrice(mint)
        if price:
            return price
        logging.warning(f"Attempt {i + 1} failed")
    return 0


def getJupPrice(mint: str, vs_token: str =USDC) -> float:
    """
    Get the price of a token using the Jupiter API
    - mint: mint address
    - vs_token: The token to compare against (default is USDC)
    :return: The price of the token in USD
    """
        
    url = f'https://lite-api.jup.ag/price/v3?ids={mint}&vsToken={vs_token}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        if response.json():
            price = response.json().get(mint, {}).get("usdPrice", 0)
            return float(price)
        else:
            return 0
    except requests.RequestException as e:
        logging.error(f"JUP API : Error fetching '{mint}' price\n >> {e}")
        return 0


if __name__ == "__main__":
    # Example usage
    from global_config import WSOL
    price = get_price(WSOL)
    print(price)
    
