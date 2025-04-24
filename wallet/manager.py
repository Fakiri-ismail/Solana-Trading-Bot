import requests

from solders.pubkey import Pubkey
from solana.rpc.api import Client

from global_config import HELIUS_RPC, SOL_URI, WSOL


class WalletManager():
    def __init__(self, public_key: str, endpoint=SOL_URI):
        """Initialize the wallet manager"""
        self.client = Client(endpoint)
        self.public_key = public_key

    def get_sol_balance(self) -> int:
        """Get wallet SOL balance"""
        balance = self.client.get_balance(Pubkey.from_string(self.public_key))
        return balance.value

    def get_assets(self, RPC_URL: str = HELIUS_RPC) -> list:
        """Get all tokens in the wallet"""
        payload = {
            "jsonrpc": "2.0",
            "id": "my-id",
            "method": "getAssetsByOwner",
            "params": {
                "ownerAddress": self.public_key,
                "page": 1,
                "limit": 1000,
                "displayOptions": {
                    "showFungible": True
                }
            }
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(RPC_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            tokens = []
            # SOL Token
            sol_balance = self.get_sol_balance()
            if sol_balance:
                tokens.append({
                    "mint": WSOL,
                    "symbol": "WSOL",
                    "balance": sol_balance,
                    "decimals": 9
                })
            # SPL Tokens
            if "result" in data:
                assets = data["result"]["items"]
                for asset in assets:
                    if asset.get("interface", "") == "V1_NFT":
                        continue  # Skip NFT assets
                    token_metadata = asset.get("content", {}).get("metadata", {})
                    token_info = asset.get("token_info", {})
                    balance = token_info.get("balance", None)
                    if balance and float(balance) > 0:
                        tokens.append({
                            "mint": asset["id"],
                            "symbol": token_metadata.get("symbol", ""),
                            "balance": balance,
                            "decimals": token_info.get("decimals", None)
                        })
            return tokens
        except requests.exceptions.HTTPError as e:
            print(f"Erreur HTTP: {e}")

    def get_token(self, mint_or_symbol: str) -> dict:
        """Get info for a specific token by symbol or mint address"""
        assets = self.get_assets()
        for token in assets:
            if mint_or_symbol in [token["mint"], token["symbol"]]:
                return token
    

