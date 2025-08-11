import requests, logging
from global_config import USDC


def getJupPrice(mint: str, vs_token: str =USDC) -> float:
    """
    Get the price of a token using the Jupiter API
    - mint: all mint address separated by a comma
    - vs_token: The token to compare against (default is USDC)
    :return: The price of the token in USD
    """
        
    url = f'https://lite-api.jup.ag/price/v2?ids={mint}&vsToken={vs_token}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        price = response.json().get("data", {}).get(mint, {}).get("price", 0) 
        return float(price)
    except requests.RequestException as e:
        logging.error(f"JUP API : Error fetching '{mint}' price\n >> {e}")
        return 0


if __name__ == "__main__":
    # Example usage
    from global_config import WSOL
    price = getJupPrice(WSOL)
    print(price)
    