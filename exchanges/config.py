import base58
from solders.keypair import Keypair
from global_config import WALLET_PRIV_KEY

payer = Keypair.from_bytes(base58.b58decode(WALLET_PRIV_KEY))
