# asa_manager/transaction.py
from algosdk.v2client import algod
from algosdk import transaction
from algosdk import account
from typing import Optional, Union

def transfer_asa(
    client: algod.AlgodClient,
    sender_private_key: str,
    receiver_address: str,
    asset_id: int,
    amount: int,
    note: Optional[bytes] = None,
    sign_transaction: bool = True
) -> Union[transaction.SignedTransaction, transaction.Transaction]:
    """
    Transfer an Algorand Standard Asset (ASA) from one account to another
    
    Args:
        client: Algod client instance
        sender_private_key: Private key of the sender account
        receiver_address: Address of the receiver account
        asset_id: ID of the asset to transfer
        amount: Amount of the asset to transfer
        note: Optional note to include in the transaction
        sign_transaction: Whether to sign the transaction
        
    Returns:
        The signed transaction if sign_transaction is True, otherwise the unsigned transaction
    """
    # Get suggested parameters
    params = client.suggested_params()
    
    # Get sender address from private key
    sender_address = account.address_from_private_key(sender_private_key)
    
    # Create the asset transfer transaction
    txn = transaction.AssetTransferTxn(
        sender=sender_address,
        sp=params,
        receiver=receiver_address,
        amt=amount,
        index=asset_id,
        note=note
    )
    
    # Sign the transaction if requested
    if sign_transaction:
        signed_txn = txn.sign(sender_private_key)
        return signed_txn
    
    return txn