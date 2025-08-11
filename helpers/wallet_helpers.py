import requests, logging
from typing import List
from solders.pubkey import Pubkey
from solders.signature import Signature
from solana.rpc.api import Client
from global_config import SOL_URI, HELIUS_API, HELIUS_API_KEY, WSOL, USDC


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
        logging.error(f"Get Wallet Signatures Error:\n >> {e}")
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
        logging.warning(f"Transaction '{tx_signature}' not found")
        return False
    elif status['confirmationStatus'] == 'finalized':
        logging.info(f"Transaction '{tx_signature}' is finalized")
        return True
    else:
        logging.info(f"Transaction '{tx_signature}' is not finalized yet. Current status: {status['confirmationStatus']}")
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
        logging.error(f"HTTP Error [{response.status_code}]: {e}")
    except Exception as e:
        logging.error(f"Error [{response.status_code}]: {e}")


def get_swap_data(tx_signature: str) -> dict:
    """
    Get swap data from transaction data
     - tx_signature: Transaction signature
    :return: Swap data
    """
    transaction_data = get_transaction_data([tx_signature])
    # Check if the transaction data is empty
    if not transaction_data:
        logging.warning(f"Swap data not found for : {tx_signature}")
        return None
    transaction_data = transaction_data[0]

    # Check if the transaction has an error 
    transaction_error = transaction_data.get("transactionError")
    if transaction_error:
        logging.error(f"Transaction error detected for : {tx_signature}")
        return None
    
    # Check if the transaction is a swap transaction
    swap_data = transaction_data.get("events", {}).get("swap", {})
    if not swap_data:
        # Extract the transfer data
        transfer_data = transaction_data.get("tokenTransfers")
        if len(transfer_data) >= 2:
            if transfer_data[0].get("mint") in [WSOL, USDC]:
                transfer_data_input, transfer_data_output = transfer_data[1], transfer_data[0]
            else:
                transfer_data_input, transfer_data_output = transfer_data[0], transfer_data[1]
            token_input = {
                "mint": transfer_data_input.get("mint"),
                "amount": float(transfer_data_input.get("tokenAmount")),
                "decimals": 0
            }
            token_output = {
                "mint": transfer_data_output.get("mint"),
                "amount": float(transfer_data_output.get("tokenAmount")),
                "decimals": 0
            }
    else:
        # Extract the swap data
        ## Extract the token input data
        if swap_data.get("nativeInput"):
            token_input = {
                "mint": WSOL,
                "amount": int(swap_data.get("nativeInput", {}).get("amount", 0)),
                "decimals": 9
            }
        elif swap_data.get("tokenInputs"):
            token_input_data = swap_data.get("tokenInputs")[0]
            token_input = {
                "mint": token_input_data.get("mint"),
                "amount": int(token_input_data.get("rawTokenAmount", {}).get("tokenAmount", 0)),
                "decimals": token_input_data.get("rawTokenAmount", {}).get("decimals")
            }
        elif swap_data.get("innerSwaps"):
            token_input_data = swap_data.get("innerSwaps")[0]["tokenInputs"][0]
            token_input = {
                "mint": token_input_data.get("mint"),
                "amount": float(token_input_data.get("tokenAmount")),
                "decimals": 0
            }
        else:
            logging.warning(f"Token input data not found for : {tx_signature}")
            token_input = None
        
        ## Extract the token output data
        if swap_data.get("nativeOutput"):
            token_output = {
                "mint": WSOL,
                "amount": int(swap_data.get("nativeOutput", {}).get("amount", 0)),
                "decimals": 9
            }
        elif swap_data.get("tokenOutputs"):
            token_output_data = swap_data.get("tokenOutputs")[0]
            token_output = {
                "mint": token_output_data.get("mint"),
                "amount": int(token_output_data.get("rawTokenAmount", {}).get("tokenAmount", 0)),
                "decimals": token_output_data.get("rawTokenAmount", {}).get("decimals")
            }
        else:
            logging.warning(f"Token output data not found for : {tx_signature}")
            token_output = None

    return {
        "description": transaction_data.get("description"),
        "fee": transaction_data.get("fee"),
        "tokenInput": token_input,
        "tokenOutput": token_output
    }


if __name__ == "__main__":
    # Example usage
    tx_passed = "2KUQ3ZdUYa5FthTFT3YzNFCnsGzj7XbtxrWfnGSfj7hHSt8PN96gEba3Kc7W2p6LU38e3TW8amaGPFpjPcWqNQtU"
    tx_failed = "R6quTum5ruRqtbztZ3mcitRuS2abDGFBDKyX9k6Mi2t4riKCyVX78iYWSJ7B1UgTKUY4U14oAJKbdEt3iD19eSe"
    tx_not_exist = "5pNsKQCV6vfdcZjWeY8nTJDoVkXq7RiyHAHuNpAPDeDuHwLNZEvdBhLmpuM8aocYaL8Cx5jhUmSTGddPjTFg1ZkP"
    print(get_swap_data(tx_passed))
    