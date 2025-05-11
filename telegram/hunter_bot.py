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
    
    def send_photo(self, photo_path):
        url = f"{self.api_url}/sendPhoto"
        with open(photo_path, 'rb') as photo:
            payload = {
                "chat_id": self.chat_id,
            }
            files = {
                'photo': photo
            }
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
            msg += f"❌ <b>{swap_info['symbol']}</b> SWAP failed !\n"
        else:
            msg += f"✅ <b>{swap_info['symbol']}</b> SWAP success !\n"
            token_output = swap_info['swapData']['tokenOutput']
            amount = int(token_output['amount']) / 10 ** int(token_output['decimals'])
            msg += f"💰 Amount: {amount} USDC\n"
        
        solscan_url = f"https://solscan.io/tx/{swap_info['transactionId']}"
        msg += f"🔗 <a href='{solscan_url}'>SolScan</a>"
        return self.send_message(msg)


if __name__ == "__main__":
    # Example usage
    from wallet.helpers import get_swap_data
    bot = HunterBot()
    tx_passed = "5pNsKQCV6vfdcZjWeY8nTJDoVkXq7RiyHAHuNpAPDeDuHwLNZEvdBhLTpuM8aocYaL8Cx5jhUmSTGddPjTFg1ZkP"
    tx_failed = "R6quTum5ruRqtbztZ3mcitRuS2abDGFBDKyX9k6Mi2t4riKCyVX78iYWSJ7B1UgTKUY4U14oAJKbdEt3iD19eSe"
    swap_info ={
        "status": True,
        "transactionId": tx_failed,
        "symbol": "ALCH",
        "swapData": get_swap_data(tx_failed)
    }
    response = bot.send_swap_message(swap_info)
    print(response)