import requests, base58, asyncio

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.api import Client

from exchanges.jupiter.swap import get_quote, build_transaction, send_transaction
from wallet.helpers import get_signature_status
from global_config import HELIUS_RPC, SOL_URI, WSOL


class WalletManager():
    def __init__(self, public_key: str, private_key:str, endpoint=SOL_URI):
        """Initialize the wallet manager"""
        self.client = Client(endpoint)
        self.public_key = public_key
        self.payer = Keypair.from_bytes(base58.b58decode(private_key))

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

    async def swap_token(self, in_mint, out_mint=WSOL, pct_amount=50, slippage=500):
        """
        Sell a token using the Jupiter API
        - in_mint (str): The mint address of the token to sell
        - out_mint (str): The mint address of the token to buy (default is WSOL)
        - pct_amount (int): The percentage of the token to sell (0-100 : default is 50%)
        - param slippage (int): The slippage percentage (default is 5%)
        :return: The transaction ID
        """
        # Get the token info and calculate the amount to sell
        token = self.get_token(in_mint)
        amount = int(token["balance"] * (pct_amount / 100))

        # Swap
        quote = get_quote(in_mint, out_mint, amount, slippage)
        swap_transaction = build_transaction(self.public_key, quote)
        tx_id = await send_transaction(self.payer, swap_transaction)
        count, tx_status = 0, False
        while not tx_status and count < 5:
            tx_status = get_signature_status(tx_id)
            count += 1
            await asyncio.sleep(5)

        return {
            "tx_signature": tx_id,
            "status": tx_status
        }
