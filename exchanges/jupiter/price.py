import requests
from global_config import USDC

def getJupPrice(mints: str, vs_token: str =USDC) -> dict:
    """
    Get the price of a token using the Jupiter API
    - mint: all mint address separated by a comma
    - vs_token: The token to compare against (default is USDC)
    :return: The price of the token in USD
    """
        
    url = f'https://lite-api.jup.ag/price/v2?ids={mints}&vsToken={vs_token}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("data", {})
    except requests.RequestException as e:
        print(f"JUP API : Error fetching '{mints}' price\n >> {e}")
        return {}


if __name__ == "__main__":
    # Example usage
    from global_config import WSOL
    price = float(getJupPrice(WSOL).get(WSOL, {}).get("price", 0))
    if not price:
        raise Exception(f"Price not found for {WSOL}")
    print(price)
    