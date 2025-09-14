import requests, os
from dotenv import load_dotenv


load_dotenv()
TELEGRAM_API_URL = f"https://api.telegram.org/bot"
HUNTER_BOT_TOKEN = os.getenv('HUNTER_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')


class HunterBot:
    def __init__(self, chat_id=CHAT_ID):
        self.api_url = TELEGRAM_API_URL + HUNTER_BOT_TOKEN
        self.chat_id = chat_id

    def send_message(self, message):
        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload)
        return response.json()
    
    def send_photo(self, photo_path, caption=""):
        url = f"{self.api_url}/sendPhoto"
        with open(photo_path, 'rb') as photo:
            payload = {
                "chat_id": self.chat_id,
                "caption": caption,
                "parse_mode": "HTML"
            }
            files = {'photo': photo}
            response = requests.post(url, data=payload, files=files)
        return response.json()
    
    def get_chat(self, chat_id):
        url = f"{self.api_url}/getChat"
        payload = {
            "chat_id": chat_id
        }
        response = requests.get(url, params=payload)
        return response.json()
    
    def send_swap_message(self, swap_info):
        msg = "✅ Transaction finalized !\n" if swap_info['status'] else "❌ Transaction failed !\n"
        if not swap_info['swapData']:
            msg += f"❌ SWAP failed !\n"
            msg += f"💎 Symbol : <b>{swap_info['symbol']}</b>\n"
        else:
            msg += f"✅ SWAP success !\n"
            msg += f"💎 Symbol : <b>{swap_info['symbol']}</b>\n"

            token_output = swap_info['swapData']['tokenOutput']
            out_amount = token_output['amount'] / 10 ** token_output['decimals']
            msg += f"💰 Amount : <b>{out_amount:.3f} SOL</b>\n"
            msg += f"💵 Value : <b>{swap_info['usdValue']:.2f}$</b>\n"

            pnl_pct = ((swap_info['sell_price'] - swap_info['buy_price']) / swap_info['buy_price']) * 100
            inv_value = swap_info['usdValue'] / (1 + (pnl_pct / 100))
            pnl = swap_info['usdValue'] - inv_value
            emoji = "🟢" if pnl > 0 else "🔴"
            msg += f"{emoji} PNL : <b>{pnl:.2f}$</b> (<b>{pnl_pct:.2f}%</b>)\n"

            mint = swap_info['swapData']['tokenInput']['mint']
            msg += f"<code>{mint}</code>\n"

            dex_url = f"https://dexscreener.com/solana/{mint}"
            jup_url = f"https://jup.ag/tokens/{mint}"
            msg += f"🔗 <a href='{dex_url}'>DEX</a> | <a href='{jup_url}'>JUP</a>\n"
        
        solscan_url = f"https://solscan.io/tx/{swap_info['transactionId']}"
        msg += f"🔀 <a href='{solscan_url}'>SolScan</a>"
        return self.send_message(msg)


if __name__ == "__main__":
    # Example usage
    from helpers.wallet_helpers import get_swap_data
    bot = HunterBot()

    # Example swap info
    tx_passed = "5pNsKQCV6vfdcZjWeY8nTJDoVkXq7RiyHAHuNpAPDeDuHwLNZEvdBhLTpuM8aocYaL8Cx5jhUmSTGddPjTFg1ZkP"
    tx_failed = "R6quTum5ruRqtbztZ3mcitRuS2abDGFBDKyX9k6Mi2t4riKCyVX78iYWSJ7B1UgTKUY4U14oAJKbdEt3iD19eSe"
    swap_info ={
        "status": True,
        "transactionId": tx_passed,
        "symbol": "ALCH",
        "swapData": get_swap_data(tx_passed),
        "usdValue": 12.134,
        "buy_price": 10,
        "sell_price": 15
    }
    # response = bot.send_swap_message(swap_info)
    # print(response)

    # Example top trading pools message
    top_trading_data = [
        {"mint": "Dz9mQ9NzkBcCsuGPFJ3r1bS4wgqKMHBPiVuniW8Mbonk", "symbol": "USELESS", "appearance": 5, "mcap": 207073097.5218624},
        {"mint": "7BgBvyjrZX1YKz4oh9mjb8ZScatkkwb8DzFx7LoiVkM3", "symbol": "SLERF", "appearance": 3, "mcap": 36912585.23428662},
    ]
