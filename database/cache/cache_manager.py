import os, json
from datetime import datetime
from helpers import json_helpers
from wallet.manager import WalletManager
from exchanges.jupiter.price import get_price
from database.crud.wallet import wallet_tokens_ops
from database.crud.tokens import top_trading_tokens_ops
from global_config import WALLET_PRIV_KEY, WALLET_PUB_KEY


WALLET_CACHE_FILE = "database/cache/wallet_cache.json"
TOP_TRADING_CACHE_FILE = "database/cache/top_trading_cache.json"
LAST_UPDATE_FILE = "database/cache/last_update.json"

# Wallet cache
def load_wallet_cache() -> list:
    wallet_cache = json_helpers.read_json_file(WALLET_CACHE_FILE)
    if not wallet_cache:
        # Get wallet tokens from the database
        wallet_cache = [
            {
                "mint": token.mint,
                "symbol": token.symbol,
                "balance": int(token.balance),
                "buy_price": float(token.buy_price),
                "usdt_value": float(token.usdt_value)
            }
            for token in wallet_tokens_ops.get_all_wallet_tokens()
        ]

    return wallet_cache

def update_wallet_cache(wallet_cache: list):
    my_wallet = WalletManager(WALLET_PUB_KEY, WALLET_PRIV_KEY)
    wallet_assets = my_wallet.get_assets()
    wallet_mints = [token["mint"] for token in wallet_assets]
    cache_mints = [token["mint"] for token in wallet_cache]

    # Remove tokens that are not in the wallet anymore
    for token in wallet_cache:
        if token["mint"] not in wallet_mints:
            wallet_cache.remove(token)

    # Add new tokens and Update existing ones
    for token in wallet_assets:
        if token["mint"] in cache_mints:
            cache_token = next((t for t in wallet_cache if t["mint"] == token["mint"]), None)
            # Check Balance
            if cache_token['balance'] != token['balance']:
                actual_price = get_price(token["mint"])
                if not actual_price:
                    continue

                if cache_token['balance'] < token['balance']:
                    # Calculate average buy price
                    added_balance = token['balance'] - cache_token['balance']
                    new_buy_price = (cache_token['balance'] * cache_token['buy_price'] + added_balance * actual_price) / token['balance']
                else:
                    new_buy_price = actual_price

                cache_token['balance'] = token['balance']
                cache_token['buy_price'] = new_buy_price
                cache_token['usdt_value'] = new_buy_price * (token['balance'] / 10 ** token["decimals"])
        else:
            buy_price = get_price(token["mint"])
            if not buy_price:
                continue
            wallet_cache.append({
                "mint": token["mint"],
                "symbol": token["symbol"],
                "balance": token["balance"],
                "buy_price": buy_price,
                "usdt_value": buy_price * (token['balance'] / 10 ** token["decimals"])
            })

    save_wallet_cache(wallet_cache)
    return wallet_cache

def save_wallet_cache(wallet_cache):
    json_helpers.write_json_file(WALLET_CACHE_FILE, wallet_cache)

# Top Trading assets cache
def load_top_trading_assets_cache():
    top_trading_assets = json_helpers.read_json_file(TOP_TRADING_CACHE_FILE)
    return top_trading_assets if top_trading_assets else []

def save_top_trading_assets_cache(top_trading_data):
    json_helpers.write_json_file(TOP_TRADING_CACHE_FILE, top_trading_data)

# Sync Time
def get_last_sync_time(field):
    if os.path.exists(LAST_UPDATE_FILE):
        with open(LAST_UPDATE_FILE, 'r') as f:
            data = json.load(f)
        
        last_sync = data.get(field, None)
        if last_sync:
            return datetime.fromisoformat(last_sync)

def update_last_sync_time(field):
    try:
        with open(LAST_UPDATE_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    data[field] = datetime.now().isoformat()
    with open(LAST_UPDATE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Sync Database    
def sync_wallet_with_db(wallet_cache: list, iteration_time: int):
    """
    Sync the database with the local wallet cache.
    """
    wallet_last_sync = get_last_sync_time('wallet')
    if wallet_last_sync:
        if (datetime.now() - wallet_last_sync).total_seconds() > iteration_time:
            # Clear wallet_token table
            wallet_tokens_ops.delete_all_wallet_tokens()

            # Insert tokens
            for token in wallet_cache:
                wallet_tokens_ops.insert_wallet_token(
                    mint=token["mint"],
                    symbol=token["symbol"],
                    balance=token["balance"],
                    buy_price=token["buy_price"],
                    usdt_value=token["usdt_value"])
            
            # Update the last sync time
            update_last_sync_time('wallet')
    else:
        update_last_sync_time('wallet')

def sync_top_trading_assets_with_db(top_trading_tokens: list):
    """
    Sync the database with the local top trading assets cache.
    """
    top_trading_last_sync = get_last_sync_time('top_trading_db')
    if top_trading_last_sync:
        if (datetime.now() - top_trading_last_sync).days > 0:
            # Sync top trading assets cache with database
            top_10 = sorted(top_trading_tokens, key=lambda d: d["appearance"], reverse=True)[:10]
            top_trading_tokens_ops.insert_top_trading_tokens(top_10)
            # Clear the cache
            json_helpers.delete_file(TOP_TRADING_CACHE_FILE)
            # Update the last sync time
            update_last_sync_time('top_trading_db')
    else:
        update_last_sync_time('top_trading_db')
