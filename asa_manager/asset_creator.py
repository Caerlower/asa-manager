# asa_manager/asset_creator.py
from algosdk.v2client import algod
from algosdk import transaction
from algosdk import account, mnemonic
from typing import Dict, Optional, Union

def create_asa(
    client: algod.AlgodClient,
    creator_private_key: str,
    asset_name: str,
    unit_name: str,
    total: int,
    decimals: int = 0,
    default_frozen: bool = False,
    url: Optional[str] = None,
    metadata_hash: Optional[bytes] = None,
    manager_address: Optional[str] = None,
    reserve_address: Optional[str] = None,
    freeze_address: Optional[str] = None,
    clawback_address: Optional[str] = None,
    note: Optional[bytes] = None,
    sign_transaction: bool = True
) -> Union[transaction.SignedTransaction, transaction.Transaction]:
    """
    Create an Algorand Standard Asset (ASA)
    
    Args:
        client: Algod client instance
        creator_private_key: Private key of the creator account
        asset_name: Name of the asset
        unit_name: Unit name of the asset (e.g., "ALGO")
        total: Total supply of the asset
        decimals: Number of decimals for the asset
        default_frozen: Whether the asset is frozen by default
        url: URL where more information about the asset can be found
        metadata_hash: Hash of the metadata of the asset
        manager_address: Address of the manager account
        reserve_address: Address of the reserve account
        freeze_address: Address of the freeze account
        clawback_address: Address of the clawback account
        note: Optional note to include in the transaction
        sign_transaction: Whether to sign the transaction
        
    Returns:
        The signed transaction if sign_transaction is True, otherwise the unsigned transaction
    """
    # Get suggested parameters
    params = client.suggested_params()
    
    # Get creator address from private key
    creator_address = account.address_from_private_key(creator_private_key)
    
    # Use creator address as default for manager, reserve, freeze, and clawback
    manager_address = manager_address or creator_address
    reserve_address = reserve_address or creator_address
    freeze_address = freeze_address or creator_address
    clawback_address = clawback_address or creator_address
    
    # Create the asset creation transaction
    txn = transaction.AssetConfigTxn(
        sender=creator_address,
        sp=params,
        total=total,
        default_frozen=default_frozen,
        unit_name=unit_name,
        asset_name=asset_name,
        manager=manager_address,
        reserve=reserve_address,
        freeze=freeze_address,
        clawback=clawback_address,
        url=url,
        metadata_hash=metadata_hash,
        decimals=decimals,
        note=note
    )
    
    # Sign the transaction if requested
    if sign_transaction:
        signed_txn = txn.sign(creator_private_key)
        return signed_txn
    
    return txn