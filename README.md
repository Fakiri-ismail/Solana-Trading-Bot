# Solana Trading Bot

## Description
This project focuses on identifying new tokens on the Solana blockchain, verifying their authenticity, and facilitating their trading.

## Installation and Setup
To run this project, you'll need to install the required packages.
Follow the steps below:

### 1. Environment
```bash
# Create a Virtual Environment
python -m venv venv

# Activate the Virtual Environment
source venv/bin/activate

# Install required packages
pip install -r requirements.txt

# Set the `PYTHONPATH` environment variable
## 1.Temporarily (For Current Session)
export PYTHONPATH=/path/to/SolanaBot:$PYTHONPATH
## 2.Permanently
nano ~/.bashrc
export PYTHONPATH=/path/to/SolanaBot:$PYTHONPATH
source ~/.bashrc
```

### 2. Create a `.env` File
In the `resources` directory, create a file named `.env` and add the following parameters:
```bash
# SOL WALLET
PUBLIC_KEY=
PRIVATE_KEY=

# API KEYS
SHYFT_API_KEY=
HELIUS_API_KEY=
BIRDEYE_API_KEY=
```
The `.env` file will store sensitive information needed for interacting with the Solana blockchain and various API services.
