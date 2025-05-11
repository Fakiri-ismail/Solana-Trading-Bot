import requests
from typing import List
from solders.pubkey import Pubkey
from solders.signature import Signature
from solana.rpc.api import Client
from global_config import SOL_URI, HELIUS_API, HELIUS_API_KEY


sol_client = Client(SOL_URI)


def get_wallet_signatures(public_key, before=None, until=None, limit=None, commitment='finalized'):
    """
    Get all signatures for a given wallet address
     - public_key: Wallet address
     - before: Signature to start from
     - until: Signature to end at
     - limit: Number of signatures to return
     - commitment: Commitment level
    :return: List of signatures
    """
    try:
        wallet = Pubkey.from_string(public_key)
        if before:
            before = Signature.from_string(before)
        if until:
            until = Signature.from_string(until)
        signatures = sol_client.get_signatures_for_address(wallet, before=before, until=until, limit=limit, commitment=commitment)
        return [str(sig.signature) for sig in signatures.value if sig.err is None]
    except Exception as e:
        print(f"[Get Wallet Signatures] {e}")
        return []


def get_signature_status(tx_signature: str) -> bool:
    """
    Get the status of a transaction
     - tx_signature: Transaction signature
    :return: True if the transaction is finalized, False otherwise
    """
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignatureStatuses",
        "params": [
            [tx_signature],
            {"searchTransactionHistory": True}
        ]
    }
    response = requests.post(SOL_URI, json=payload)
    status = response.json()['result']['value'][0]
    if status is None:
        print(f"Transaction '{tx_signature}' not found")
        return False
    elif status['confirmationStatus'] == 'finalized':
        print(f"Transaction '{tx_signature}' is finalized")
        return True
    else:
        print(f"Transaction '{tx_signature}' is not finalized yet. Current status: {status['confirmationStatus']}")
        return False


def get_transaction_data(signatures):
    """
    Get transaction data for a list of signatures
     - signatures: List of transaction signatures
    :return: List of transaction data
    """
    if not isinstance(signatures, List):
        raise ValueError("The param signatures must be a list")
    if len(signatures) == 0:
        raise ValueError("The param signatures cannot be a empty list")
    
    transactions_data = []
    # The API only accepts 100 signatures at a time
    div = len(signatures)//100
    div = div + 1 if len(signatures)%100 != 0 else div
    try:
        for i in range(div):
            response = requests.post(
                f"{HELIUS_API}/transactions?api-key={HELIUS_API_KEY}",
                headers={"Content-Type":"application/json"},
                json={'transactions': signatures[i*100 : (i+1)*100]}
            )
            response.raise_for_status()
            transactions_data = transactions_data + response.json()
        return transactions_data
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error [{response.status_code}]: {e}")
    except Exception as e:
        print(f"Error [{response.status_code}]: {e}")


def get_swap_data(tx_signature: str) -> dict:
    """
    Get swap data from transaction data
     - tx_signature: Transaction signature
    :return: Swap data
    """
    transaction_data = get_transaction_data([tx_signature])
    # Check if the transaction data is empty
    if not transaction_data:
        return None
    transaction_data = transaction_data[0]

    # Check if the transaction has an error or if it doesn't contain swap data
    transaction_error = transaction_data.get("transactionError")
    swap_data = transaction_data.get("events", {}).get("swap", {})
    if transaction_error or not swap_data:
        return None
    
    # Extract the swap data
    token_input = swap_data.get("tokenInputs")[0] if swap_data.get("tokenInputs") else {}
    token_output = swap_data.get("tokenOutputs")[0] if swap_data.get("tokenOutputs") else {}
    return {
        "description": transaction_data.get("description"),
        "fee": transaction_data.get("fee"),
        "tokenInput": {
            "mint": token_input.get("mint"),
            "amount": token_input.get("rawTokenAmount", {}).get("tokenAmount"),
            "decimals": token_input.get("rawTokenAmount", {}).get("decimals")
        },
        "tokenOutput": {
            "mint": token_output.get("mint"),
            "amount": token_output.get("rawTokenAmount", {}).get("tokenAmount"),
            "decimals": token_output.get("rawTokenAmount", {}).get("decimals")
        }
    }


if __name__ == "__main__":
    # Example usage
    tx_passed = "5pNsKQCV6vfdcZjWeY8nTJDoVkXq7RiyHAHuNpAPDeDuHwLNZEvdBhLTpuM8aocYaL8Cx5jhUmSTGddPjTFg1ZkP"
    tx_failed = "R6quTum5ruRqtbztZ3mcitRuS2abDGFBDKyX9k6Mi2t4riKCyVX78iYWSJ7B1UgTKUY4U14oAJKbdEt3iD19eSe"
    tx_not_exist = "5pNsKQCV6vfdcZjWeY8nTJDoVkXq7RiyHAHuNpAPDeDuHwLNZEvdBhLmpuM8aocYaL8Cx5jhUmSTGddPjTFg1ZkP"
    print(get_swap_data(tx_not_exist))
    