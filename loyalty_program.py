from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from asa_manager import create_asa, opt_in, transfer_asa
from asa_manager.utils import wait_for_confirmation, get_asset_balance
import os
from dotenv import load_dotenv
import ssl
import json
from datetime import datetime

# Disable SSL verification (not recommended for production)
ssl._create_default_https_context = ssl._create_unverified_context

# Load environment variables from .env file
load_dotenv()

# Get business admin private key and address from environment variables
admin_private_key = os.getenv("PRIVATE_KEY")
admin_address = account.address_from_private_key(admin_private_key)

# Get Algorand client parameters from environment variables
algod_token = os.getenv("TESTNET_ALGOD_TOKEN")
algod_url = os.getenv("TESTNET_ALGOD_URL")

# Initialize Algorand client
algod_client = algod.AlgodClient(algod_token, algod_url)

# Utility function to create a new test customer account
def create_customer_account():
    private_key, address = account.generate_account()
    print(f"Created new customer account: {address}")
    print(f"Customer mnemonic: {mnemonic.from_private_key(private_key)}")
    return private_key, address

def fund_account(address, amount=1000000):  # 1 ALGO in microALGOs
    print(f"Funding account {address} with {amount/1000000} ALGO...")
    
    # Get parameters for the transaction
    params = algod_client.suggested_params()
    
    # Create payment transaction
    txn = transaction.PaymentTxn(
        sender=admin_address,
        sp=params,
        receiver=address,
        amt=amount
    )
    
    # Sign transaction
    signed_txn = txn.sign(admin_private_key)
    
    # Send transaction
    txid = algod_client.send_transaction(signed_txn)
    print(f"Funding transaction sent with ID: {txid}")
    
    # Wait for confirmation
    wait_for_confirmation(algod_client, txid)
    print(f"Account funded successfully!")
    
    
def create_loyalty_program():
    print("=== Star Coffee Loyalty Program ===")
    print(f"Business Admin Address: {admin_address}")
    
    # Create the loyalty points token
    print("\nCreating loyalty points token...")
    
    # Asset parameters
    asset_name = "Star Coffee Rewards"
    unit_name = "STAR"
    total_supply = 10000000  # 10 million points
    decimals = 0  # No fractional points
    
    # Additional asset parameters
    url = "https://starcoffee.example/rewards"
    metadata_hash = None  # Optional hash of asset metadata
    default_frozen = False  # Tokens are not frozen by default
    
    # Reserve, freeze, clawback, and manager addresses
    # For a loyalty program, the business might want to maintain control
    reserve = admin_address  # Reserve address holds unreleased tokens
    freeze = admin_address  # Ability to freeze customer points if needed
    clawback = admin_address  # Ability to clawback points (e.g., expired points)
    manager = admin_address  # Ability to change asset configuration
    
    # Create the asset
    signed_txn = create_asa(
        client=algod_client,
        creator_private_key=admin_private_key,
        asset_name=asset_name,
        unit_name=unit_name,
        total=total_supply,
        decimals=decimals,
        default_frozen=default_frozen,
        url=url,
        metadata_hash=metadata_hash,
        manager_address=manager,
        reserve_address=reserve,
        freeze_address=freeze,
        clawback_address=clawback,
        note=f"Loyalty Program Created: {datetime.now().isoformat()}"
    )
    
    # Send the transaction
    txid = algod_client.send_transaction(signed_txn)
    print(f"Transaction sent with ID: {txid}")
    
    # Wait for confirmation
    tx_info = wait_for_confirmation(algod_client, txid)
    asset_id = tx_info["asset-index"]
    print(f"Loyalty token created with Asset ID: {asset_id}")
    
    return asset_id

def customer_registration(asset_id):
    """Simulate customer registration process"""
    print("\n=== New Customer Registration ===")
    
    # Create a new customer account (in production, customer would provide their address)
    customer_private_key, customer_address = create_customer_account()
    
    # Fund the customer account so they can opt-in to the asset
    fund_account(customer_address)
    
    print(f"\nCustomer needs to opt-in to receive loyalty points (Asset ID: {asset_id})")
    # In a real application, you would ask the customer to opt-in to the asset
    # For this example, we'll simulate this:
    
    try:
        # Customer opts in to the loyalty program token
        opt_in_txn = opt_in(
            client=algod_client,
            account_private_key=customer_private_key,
            asset_id=asset_id
        )
        
        txid = algod_client.send_transaction(opt_in_txn)
        print(f"Opt-in transaction sent with ID: {txid}")
        
        # Wait for confirmation
        wait_for_confirmation(algod_client, txid)
        print(f"Customer {customer_address} successfully opted in to loyalty program!")
        
        return customer_private_key, customer_address
        
    except Exception as e:
        print(f"Error during opt-in: {e}")
        return None, None

def award_points(asset_id, customer_address, points, purchase_amount=None):
    """Award loyalty points to a customer"""
    print(f"\n=== Awarding {points} points to customer ===")
    
    # Add purchase details in the note field
    note = {
        "type": "loyalty_reward",
        "timestamp": datetime.now().isoformat(),
        "points_awarded": points
    }
    
    if purchase_amount:
        note["purchase_amount"] = purchase_amount
        
    note_encoded = json.dumps(note).encode()
    
    try:
        # Transfer loyalty points to the customer
        signed_txn = transfer_asa(
            client=algod_client,
            sender_private_key=admin_private_key,
            receiver_address=customer_address,
            asset_id=asset_id,
            amount=points,
            note=note_encoded
        )
        
        txid = algod_client.send_transaction(signed_txn)
        print(f"Points transfer transaction sent with ID: {txid}")
        
        # Wait for confirmation
        wait_for_confirmation(algod_client, txid)
        print(f"Successfully awarded {points} points to customer {customer_address}")
        
        # Get customer's updated balance
        balance = get_asset_balance(algod_client, customer_address, asset_id)
        print(f"Customer's total loyalty points balance: {balance}")
        
    except Exception as e:
        print(f"Error awarding points: {e}")

def redeem_points(asset_id, customer_private_key, customer_address, points):
    """Customer redeems loyalty points for a reward"""
    print(f"\n=== Customer redeeming {points} points ===")
    
    # Add redemption details in the note field
    note = {
        "type": "loyalty_redemption",
        "timestamp": datetime.now().isoformat(),
        "points_redeemed": points,
        "reward": "Free Coffee"
    }
    
    note_encoded = json.dumps(note).encode()
    
    try:
        # Check if customer has enough points
        balance = get_asset_balance(algod_client, customer_address, asset_id)
        if balance < points:
            print(f"Insufficient points. Customer has {balance} points, but attempted to redeem {points}.")
            return False
        
        # Transfer loyalty points back to the business
        signed_txn = transfer_asa(
            client=algod_client,
            sender_private_key=customer_private_key,
            receiver_address=admin_address,
            asset_id=asset_id,
            amount=points,
            note=note_encoded
        )
        
        txid = algod_client.send_transaction(signed_txn)
        print(f"Redemption transaction sent with ID: {txid}")
        
        # Wait for confirmation
        wait_for_confirmation(algod_client, txid)
        print(f"Successfully redeemed {points} points from customer {customer_address}")
        
        # Get customer's updated balance
        balance = get_asset_balance(algod_client, customer_address, asset_id)
        print(f"Customer's remaining loyalty points balance: {balance}")
        
        return True
        
    except Exception as e:
        print(f"Error redeeming points: {e}")
        return False

def main():
    try:
        # Create the loyalty program and token
        asset_id = create_loyalty_program()
        
        # Register a new customer
        customer_private_key, customer_address = customer_registration(asset_id)
        if not customer_address:
            print("Failed to register customer. Exiting.")
            return
            
        # Simulate customer purchases and point awards
        award_points(asset_id, customer_address, 50, purchase_amount=10.99)  # $10.99 purchase
        award_points(asset_id, customer_address, 75, purchase_amount=15.50)  # $15.50 purchase
        award_points(asset_id, customer_address, 100, purchase_amount=22.75)  # $22.75 purchase
        
        # Simulate customer redeeming points
        redeem_points(asset_id, customer_private_key, customer_address, 100)
        
        print("\n=== Loyalty Program Demonstration Complete ===")
        print(f"Loyalty Token Asset ID: {asset_id}")
        print(f"Business Admin Address: {admin_address}")
        print(f"Customer Address: {customer_address}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()