# asa_manager/asset_manager.py
from algosdk.v2client import algod
from algosdk import transaction
from algosdk import account
from typing import Optional, Union

def opt_in(
    client: algod.AlgodClient,
    account_private_key: str,
    asset_id: int,
    sign_transaction: bool = True
) -> Union[transaction.SignedTransaction, transaction.Transaction]:
    """
    Opt-in to an Algorand Standard Asset (ASA)
    
    Args:
        client: Algod client instance
        account_private_key: Private key of the account to opt-in
        asset_id: ID of the asset to opt-in to
        sign_transaction: Whether to sign the transaction
        
    Returns:
        The signed transaction if sign_transaction is True, otherwise the unsigned transaction
    """
    # Get suggested parameters
    params = client.suggested_params()
    
    # Get address from private key
    address = account.address_from_private_key(account_private_key)
    
    # Create the asset opt-in transaction
    txn = transaction.AssetTransferTxn(
        sender=address,
        sp=params,
        receiver=address,
        amt=0,
        index=asset_id
    )
    
    # Sign the transaction if requested
    if sign_transaction:
        signed_txn = txn.sign(account_private_key)
        return signed_txn
    
    return txn

def opt_out(
    client: algod.AlgodClient,
    account_private_key: str,
    asset_id: int,
    sign_transaction: bool = True
) -> Union[transaction.SignedTransaction, transaction.Transaction]:
    """
    Opt-out from an Algorand Standard Asset (ASA)
    
    Args:
        client: Algod client instance
        account_private_key: Private key of the account to opt-out
        asset_id: ID of the asset to opt-out from
        sign_transaction: Whether to sign the transaction
        
    Returns:
        The signed transaction if sign_transaction is True, otherwise the unsigned transaction
    """
    # Get suggested parameters
    params = client.suggested_params()
    
    # Get address from private key
    address = account.address_from_private_key(account_private_key)
    
    # Create the asset opt-out transaction
    # To opt-out, we send all our remaining balance to the asset creator
    asset_info = client.asset_info(asset_id)
    creator = asset_info["params"]["creator"]
    
    # Check if the account has a balance of the asset
    account_info = client.account_info(address)
    asset_balance = 0
    for asset in account_info.get("assets", []):
        if asset["asset-id"] == asset_id:
            asset_balance = asset["amount"]
            break
    
    txn = transaction.AssetTransferTxn(
        sender=address,
        sp=params,
        receiver=creator,
        amt=asset_balance,
        index=asset_id,
        close_assets_to=creator
    )
    
    # Sign the transaction if requested
    if sign_transaction:
        signed_txn = txn.sign(account_private_key)
        return signed_txn
    
    return txn

def modify_asset(
    client: algod.AlgodClient,
    manager_private_key: str,
    asset_id: int,
    new_manager: Optional[str] = None,
    new_reserve: Optional[str] = None,
    new_freeze: Optional[str] = None,
    new_clawback: Optional[str] = None,
    sign_transaction: bool = True
) -> Union[transaction.SignedTransaction, transaction.Transaction]:
    """
    Modify an Algorand Standard Asset (ASA)
    
    Args:
        client: Algod client instance
        manager_private_key: Private key of the manager account
        asset_id: ID of the asset to modify
        new_manager: New manager address (or None to keep current)
        new_reserve: New reserve address (or None to keep current)
        new_freeze: New freeze address (or None to keep current)
        new_clawback: New clawback address (or None to keep current)
        sign_transaction: Whether to sign the transaction
        
    Returns:
        The signed transaction if sign_transaction is True, otherwise the unsigned transaction
    """
    # Get suggested parameters
    params = client.suggested_params()
    
    # Get manager address from private key
    manager_address = account.address_from_private_key(manager_private_key)
    
    # Get current asset info
    asset_info = client.asset_info(asset_id)
    current_params = asset_info["params"]
    
    # Use current values if new values are not provided
    new_manager = new_manager or current_params.get("manager")
    new_reserve = new_reserve or current_params.get("reserve")
    new_freeze = new_freeze or current_params.get("freeze")
    new_clawback = new_clawback or current_params.get("clawback")
    
    # Create the asset modification transaction
    txn = transaction.AssetConfigTxn(
        sender=manager_address,
        sp=params,
        index=asset_id,
        manager=new_manager,
        reserve=new_reserve,
        freeze=new_freeze,
        clawback=new_clawback,
        strict_empty_address_check=False
    )
    
    # Sign the transaction if requested
    if sign_transaction:
        signed_txn = txn.sign(manager_private_key)
        return signed_txn
    
    return txn