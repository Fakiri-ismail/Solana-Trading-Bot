import os, json
from datetime import datetime
from helpers import json_helpers
from database.crud.wallet import wallet_tokens_ops
from database.crud.tokens import top_trading_tokens_ops


WALLET_CACHE_FILE = "database/db_sync/wallet_cache.json"
TOP_TRADING_CACHE_FILE = "database/db_sync/top_trading_cache.json"
LAST_UPDATE_FILE = "database/db_sync/last_update.json"

# Wallet chache
def load_wallet_cache():
    return json_helpers.read_json_file(WALLET_CACHE_FILE)
    
def save_wallet_cache(wallet_data):
    json_helpers.write_json_file(WALLET_CACHE_FILE, wallet_data)

# Top Trading pools cache
def load_top_trading_pools_cache():
    return json_helpers.read_json_file(TOP_TRADING_CACHE_FILE)

def save_top_trading_pools_cache(top_trading_data):
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
def sync_wallet_with_db():
    """
    Sync the database with the local wallet cache.
    """
    wallet_last_sync = get_last_sync_time('wallet')
    if wallet_last_sync:
        if (datetime.now() - wallet_last_sync).total_seconds() > 3600:
            # Load the wallet cache
            wallet_cache = load_wallet_cache()

            # Clear wallet_token table
            wallet_tokens_ops.delete_all_wallet_tokens()

            # Insert tokens
            for token in wallet_cache:
                wallet_tokens_ops.insert_wallet_token(
                    mint=token["mint"],
                    symbol=token["symbol"],
                    purchase_price=token["purchase_price"],
                    usdt_value=token["usdt_value"])
            
            # Update the last sync time
            update_last_sync_time('wallet')
    else:
        update_last_sync_time('wallet')

def sync_top_trading_pools_with_db(top_10_pools: list):
    """
    Sync the database with the local top trading pools cache.
    """
    top_trading_last_sync = get_last_sync_time('top_trading_db')
    if top_trading_last_sync:
        if (datetime.now() - top_trading_last_sync).days > 0:
            # Sync top trading pools cache with database
            top_trading_tokens_ops.insert_top_trading_tokens(top_10_pools)
            # Clear the cache
            json_helpers.delete_file(TOP_TRADING_CACHE_FILE)
            # Update the last sync time
            update_last_sync_time('top_trading_db')
    else:
        update_last_sync_time('top_trading_db')
