from dotenv import load_dotenv
import os

# Load variables from .env into environment
load_dotenv()

# WALLETS ADDRESS
WALLET_PUB_KEY = os.getenv("PUBLIC_KEY")
WALLET_PRIV_KEY = os.getenv("PRIVATE_KEY")

# URLS
HELIUS_RPC = f"https://mainnet.helius-rpc.com/?api-key={os.getenv('HELIUS_API_KEY')}"
