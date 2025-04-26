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
export PYTHONPATH=/path/to/solana-trading-bot:$PYTHONPATH
## 2.Permanently
nano ~/.bashrc
export PYTHONPATH=/path/to/solana-trading-bot:$PYTHONPATH
source ~/.bashrc
```

### 2. Create a `.env` File
In the main directory, rename the file `.env_examaple` to  `.env` and fill in the empty fields.  
The `.env` file will store sensitive information needed for interacting with the Solana blockchain, your wallet, the database and various API services.

### 3. Database configuration
You can use any database you want, for this project I used the [Neon](https://neon.tech/) database.
