import requests
import logging
from global_config import HELIUS_RPC


def get_assets_by_owner(wallet_pub_address: str, RPC_URL :str = HELIUS_RPC):
    payload = {
        "jsonrpc": "2.0",
        "id": "my-id",
        "method": "getAssetsByOwner",
        "params": {
            "ownerAddress": wallet_pub_address,
            "page": 1,
            "limit": 1000,
            "displayOptions": {
                "showFungible": True
            }
        }
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(RPC_URL, headers=headers, json=payload)
    response.raise_for_status()

    if response.status_code == 200:
        data = response.json()
        if "result" in data:
            assets = data["result"]["items"]
            spl_tokens = []
            for asset in assets:
                if asset.get("interface", "") == "V1_NFT":
                    continue  # Skip NFT assets
                token_metadata = asset.get("content", {}).get("metadata", {})
                token_info = asset.get("token_info", {})
                balance = token_info.get("balance", None)
                if balance and float(balance) > 0:
                    spl_tokens.append({
                        "mint": asset["id"],
                        "symbol": token_metadata.get("symbol", ""),
                        "balance": balance,
                        "decimals": token_info.get("decimals", None)
                    })
            return spl_tokens
        else:
            logging.error("No result found in response")
    else:
        logging.error("Error: {}, {}", response.status_code, response.text)