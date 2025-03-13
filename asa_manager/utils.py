# asa_manager/utils.py
from algosdk.v2client import algod
from algosdk import transaction
from typing import Dict, Optional

def wait_for_confirmation(client: algod.AlgodClient, txid: str, timeout: int = 10) -> Dict:
    """
    Wait for a transaction to be confirmed by the network
    
    Args:
        client: Algod client instance
        txid: Transaction ID to wait for
        timeout: Maximum number of seconds to wait
        
    Returns:
        Transaction information if confirmed
    """
    start_round = client.status()["last-round"] + 1
    current_round = start_round
    
    while current_round < start_round + timeout:
        try:
            pending_txn = client.pending_transaction_info(txid)
            if pending_txn.get("confirmed-round", 0) > 0:
                return pending_txn
        except Exception:
            pass
            
        client.status_after_block(current_round)
        current_round += 1
        
    raise Exception(f"Transaction {txid} not confirmed after {timeout} rounds")

def get_asset_balance(client: algod.AlgodClient, account_address: str, asset_id: int) -> int:
    """
    Get the balance of a specific asset for an account
    
    Args:
        client: Algod client instance
        account_address: Address of the account
        asset_id: ID of the asset
        
    Returns:
        Balance of the asset
    """
    account_info = client.account_info(account_address)
    for asset in account_info.get("assets", []):
        if asset["asset-id"] == asset_id:
            return asset["amount"]
    return 0