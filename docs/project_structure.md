# 📌 Solana Trading Bot Roadmap

## 📂 Project Structure
```
📂 Solana-Trading-Bot/
    🐍 main.py
    📝 README.md
    🐍 global_config.py
    📂 telegram_bots/
        📂 hunter/
            🐍 run.py
            🐍 markup.py
            🐍 messenger.py
            🐍 handlers.py
    📂 docs/
        📝 project_structure.md
        📝 standard_format.md
    📂 exchanges/
        📂 jupiter/
            🐍 swap.py
            🐍 pro.py
            🐍 ultra_swap.py
            🐍 price.py
            🐍 top_trading_pools.py
    📂 resources/
        📜 user_agent.json
    📂 database/
        🐍 connection.py
        🐍 config.py
        📂 db_sync/
            🐍 cache_manager.py
        📂 crud/
            📂 coins/
                🐍 top_memes_ops.py
            📂 wallet/
                🐍 wallet_tokens_ops.py
                🐍 trading_history_ops.py
                🐍 wallet_history_ops.py
        📂 models/
            🐍 wallet.py
            🐍 coins.py
    📂 helpers/
        🐍 generate_roadmap.py
        🐍 wallet_helpers.py
        🐍 json_helpers.py
        🐍 utils.py
    📂 scripts/
        📄 trading.sh
        📄 top_trading_pools.sh
        📄 wallet_history.sh
        📄 telegram_bot.sh
    📂 wallet/
        🐍 trading.py
        🐍 report.py
        🐍 manager.py
        🐍 history.py
```

### `main.py`

### `global_config.py`

### `telegram_bots/hunter/run.py`

### `telegram_bots/hunter/markup.py`

#### Functions:
- `start_markup`

### `telegram_bots/hunter/messenger.py`
#### Classes:
- `HunterBot`

#### Functions:
- `__init__`
- `send_message`
- `send_photo`
- `get_chat`
- `send_swap_message`
- `send_top_trading_pools_message`

### `telegram_bots/hunter/handlers.py`

#### Functions:
- `start`
- `button_handler`
- `text_handler`

### `exchanges/jupiter/swap.py`

#### Functions:
- `get_quote`
- `build_transaction`
- `send_transaction`

### `exchanges/jupiter/pro.py`

#### Functions:
- `get_toptrending`

### `exchanges/jupiter/ultra_swap.py`

#### Functions:
- `get_order`
- `sign_transaction`
- `execute`

### `exchanges/jupiter/price.py`

#### Functions:
- `getJupPrice`

### `exchanges/jupiter/top_trading_pools.py`

### `database/connection.py`

#### Functions:
- `get_connection`
- `get_cursor`
- `init_db`

### `database/config.py`

#### Functions:
- `parse_db_url`

### `database/db_sync/cache_manager.py`

#### Functions:
- `load_wallet_cache`
- `save_wallet_cache`
- `load_top_trading_pools_cache`
- `save_top_trading_pools_cache`
- `get_last_sync_time`
- `update_last_sync_time`
- `sync_wallet_with_db`
- `sync_top_trading_pools_with_db`

### `database/crud/coins/top_memes_ops.py`

#### Functions:
- `insert_top_meme`
- `get_all_top_memes`
- `delete_top_meme`

### `database/crud/wallet/wallet_tokens_ops.py`

#### Functions:
- `insert_wallet_token`
- `get_wallet_token`
- `get_all_wallet_tokens`
- `update_wallet_token`
- `delete_wallet_token`
- `delete_all_wallet_tokens`

### `database/crud/wallet/trading_history_ops.py`

#### Functions:
- `create_trading_history`
- `get_trading_history`
- `get_all_trading_history`
- `get_trading_history_by_token`
- `get_trading_history_by_date_range`
- `delete_trading_history`

### `database/crud/wallet/wallet_history_ops.py`

#### Functions:
- `create_wallet_history`
- `get_wallet_history`
- `delete_wallet_history`
- `get_all_wallet_history`
- `get_latest_wallet_history`
- `get_wallet_history_by_date_range`

### `database/models/wallet.py`
#### Classes:
- `WalletHistory`
- `WalletToken`
- `TradingHistory`

#### Functions:
- `__post_init__`
- `__post_init__`

### `database/models/coins.py`
#### Classes:
- `TopMeme`

### `helpers/generate_roadmap.py`

#### Functions:
- `get_tree_structure`
- `parse_file`
- `generate_markdown`

### `helpers/wallet_helpers.py`

#### Functions:
- `get_wallet_signatures`
- `get_signature_status`
- `get_transaction_data`
- `get_swap_data`

### `helpers/json_helpers.py`

#### Functions:
- `read_json_file`
- `write_json_file`
- `add_json_record`
- `delete_file`

### `helpers/utils.py`

#### Functions:
- `setup_logging`
- `get_random_user_agent`
- `format_number`

### `wallet/trading.py`

#### Functions:
- `main`

### `wallet/report.py`

#### Functions:
- `wallet_history_report`
- `trading_history_report`
- `wallet_tokens_report`
- `send_monthly_wallet_report`

### `wallet/manager.py`
#### Classes:
- `WalletManager`

#### Functions:
- `__init__`
- `get_sol_balance`
- `get_assets`
- `get_token`
- `swap_token`

### `wallet/history.py`

