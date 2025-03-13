from algosdk import account 
from algosdk.v2client import algod
from asa_manager import create_asa, opt_in, transfer_asa
from asa_manager.utils import wait_for_confirmation, get_asset_balance
import os
from dotenv import load_dotenv
import ssl

# Disable SSL verification (not recommended for production)
ssl._create_default_https_context = ssl._create_unverified_context


# Load environment variables from .env file
load_dotenv()

# Get private key and address from environment variables
private_key = os.getenv("PRIVATE_KEY")
address = account.address_from_private_key(private_key)
print("Address:", address)

# Get Algorand client parameters from environment variables
algod_token = os.getenv("TESTNET_ALGOD_TOKEN")
algod_url = os.getenv("TESTNET_ALGOD_URL")
algod_port = os.getenv("TESTNET_ALGOD_PORT")

# Initialize Algorand client
algod_client = algod.AlgodClient(algod_token, algod_url)

def main():
    
    # Example 1: Create a new ASA
    print("Creating a new ASA...")
    signed_txn = create_asa(
        client=algod_client,
        creator_private_key=private_key,
        asset_name="My Test Token",
        unit_name="TEST",
        total=1,
        decimals=2
    )
    
    # Send transaction
    txid = algod_client.send_transaction(signed_txn)
    print(f"Transaction sent with ID: {txid}")
    
    # Wait for confirmation
    tx_info = wait_for_confirmation(algod_client, txid)
    asset_id = tx_info["asset-index"]
    print(f"Asset created with ID: {asset_id}")
    
    # You can continue with more examples if you have multiple accounts
    # For example, opt in to the asset with another account, transfer, etc.

if __name__ == "__main__":
    main()