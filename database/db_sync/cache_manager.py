import os, json
from datetime import datetime
from database.crud.wallet.wallet_tokens_ops import get_wallet_token, get_all_wallet_tokens
from database.crud.wallet.wallet_tokens_ops import insert_wallet_token, delete_wallet_token


LOCAL_CACHE_FILE = "database/db_sync/wallet_cache.json"
LAST_UPDATE_FILE = "database/db_sync/last_update.txt"


def load_wallet_cache():
    if os.path.exists(LOCAL_CACHE_FILE):
        with open(LOCAL_CACHE_FILE, "r") as f:
            content = f.read()
            if not content.strip():
                return []
            return json.loads(content)
    return []
    
def save_wallet_cache(wallet_cache):
    with open(LOCAL_CACHE_FILE, "w") as f:
        json.dump(wallet_cache, f, indent=4)


def update_last_sync_time():
    with open(LAST_UPDATE_FILE, "w") as f:
        f.write(datetime.now().isoformat())

def get_last_sync_time():
    if os.path.exists(LAST_UPDATE_FILE):
        with open(LAST_UPDATE_FILE, "r") as f:
            return datetime.fromisoformat(f.read().strip())
    return None


def should_sync_db(interval=60):
    """
    Check if the database should be synced based on the last sync time and the current time.
    :param interval: The interval in minutes to check for syncing.
    :return: True if the database should be synced, False otherwise.
    """
    last_sync = get_last_sync_time()
    if not last_sync:
        return True
    else:
        now = datetime.now()
        return (now - last_sync).total_seconds() > interval * 60

def sync_with_db():
    """
    Sync the database with the local cache.
    :return: True if the sync was successful, False otherwise.
    """
    if should_sync_db():
        # Load the wallet cache
        wallet_cache = load_wallet_cache()
        cache_mints = [t["mint"] for t in wallet_cache]
        # Load the wallet datebase
        wallet_db = get_all_wallet_tokens()
        db_mints = [token.mint for token in wallet_db]

        # Remove tokens that are not in the wallet anymore
        for db_mint in db_mints:
            if db_mint not in cache_mints:
                # Delete token from DB
                delete_wallet_token(mint=db_mint)

        # Insert new token into DB
        for token in wallet_cache:
            if token["mint"] not in db_mints:
                # Insert new token into DB
                insert_wallet_token(
                    mint=token["mint"],
                    symbol=token["symbol"],
                    purchase_price=token["purchase_price"],
                    usdt_value=token["usdt_value"]
                )
    
        # Update the last sync time
        update_last_sync_time()
        return True
