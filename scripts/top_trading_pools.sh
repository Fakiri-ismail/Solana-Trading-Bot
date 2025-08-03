#!/bin/bash
export PYTHONPATH=$SOL_PROJECT_PATH:$PYTHONPATH

cd $SOL_PROJECT_PATH
source venv/bin/activate
python3 exchanges/jupiter/top_trading_pools.py