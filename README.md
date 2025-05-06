# ASA Manager

A simple, powerful library for creating and managing Algorand Standard Assets (ASAs).

## Overview

ASA Manager makes it easy to create, opt-in to, and transfer Algorand Standard Assets. It abstracts away the complexity of the Algorand SDK, providing a straightforward interface for token management on the Algorand blockchain.

## Prerequisites

- Python 3.6+
- An Algorand node or access to a service like PureStake or Algorand TestNet/MainNet
- Algorand wallet with sufficient testnet algos. 

## Installation

```bash
# Clone the repository
git clone https://github.com/Caerlower/asa-manager.git
cd asa-manager

# Create and activate a virtual environment
python -m venv algorand
source algorand/bin/activate  # On Windows: algorand\Scripts\activate

```

## Quick Start

### Setup

### Setting up AlgoKit

AlgoKit is Algorand's official development kit that simplifies the developer experience:

1. Install AlgoKit:
    
    ```bash
    pip install algokit
    
    ```

2. Setting up Docker
    
3. Use AlgoKit for localnet development:
    
    ```bash
    algokit localnet start
    
    ```

4. Fillout the `.env` file in your project root with your mnemonic phrases:

```
# Your account's private key (keep this secure!)
PRIVATE_KEY="your_private_key_here"
```

**NOTE:** If you have Pera wallet then you can use the account.py file where you can paste your mnemonic phrase, after that first run `account.py` to get your private key and then paste it in the `.env` file.

### Basic Usage

I have give an `example.py` file to show the basic functioning for ASA Manager.

## Features

- **Create ASAs**: Create custom tokens with configurable properties
- **Opt-in/Opt-out**: Manage asset acceptance for Algorand accounts
- **Transfer Assets**: Send tokens between accounts
- **Asset Information**: Retrieve token balances and details
- **Utility Functions**: Helper methods for common operations

## API Reference

### Create an ASA

```python
from asa_manager import create_asa

signed_txn = create_asa(
    client=algod_client,              # AlgodClient instance
    creator_private_key=private_key,  # Private key of the creator
    asset_name="Token Name",          # Full name of the asset
    unit_name="TKN",                  # Short name (1-8 chars)
    total=1000000,                    # Total supply
    decimals=6,                       # Decimal places
    default_frozen=False,             # Whether accounts start frozen
    manager_address=None,             # Optional: Account that can change config
    reserve_address=None,             # Optional: Account that holds uncirculated tokens
    freeze_address=None,              # Optional: Account that can freeze/unfreeze
    clawback_address=None,            # Optional: Account that can clawback tokens
    url="https://example.com",        # Optional: URL about the asset
    metadata_hash=None                # Optional: Hash of additional data
)
```

### Opt-in to an ASA

```python
from asa_manager import opt_in

signed_txn = opt_in(
    client=algod_client,           # AlgodClient instance
    account_private_key=private_key,  # Private key of the account
    asset_id=12345                 # ID of the asset to opt into
)

txid = algod_client.send_transaction(signed_txn)
wait_for_confirmation(algod_client, txid)
```

### Transfer an ASA

```python
from asa_manager import transfer_asa

signed_txn = transfer_asa(
    client=algod_client,               # AlgodClient instance
    sender_private_key=private_key,    # Private key of the sender
    receiver_address="RECEIVER_ADDRESS",  # Address receiving the asset
    asset_id=12345,                    # ID of the asset to transfer
    amount=100                         # Amount to transfer
)

txid = algod_client.send_transaction(signed_txn)
wait_for_confirmation(algod_client, txid)
```

### Get Asset Balance

```python
from asa_manager.utils import get_asset_balance

balance = get_asset_balance(
    client=algod_client,       # AlgodClient instance
    account=address,           # Address to check balance for
    asset_id=12345             # Asset ID to check
)
print(f"Balance: {balance}")
```

## Common Use Cases

### Loyalty Program
There is a `loyalty_program.py` in the root directory implemeting this. 


### Event Tickets

```python
# Create limited event tickets
event_ticket_txn = create_asa(
    client=algod_client,
    creator_private_key=organizer_private_key,
    asset_name="Concert 2025 VIP",
    unit_name="TICKET",
    total=200,  # Only 200 tickets available
    decimals=0
)
```

### Digital Collectibles

```python
# Create a unique collectible
collectible_txn = create_asa(
    client=algod_client,
    creator_private_key=artist_private_key,
    asset_name="Digital Artwork #001",
    unit_name="NFT",
    total=1,  # Only 1 exists
    decimals=0,
    url="https://ipfs.io/ipfs/QmXyZ..." # Link to artwork
)
```

### Transaction Failed

- Check if your account has sufficient testnet Algos for the transaction fee
- Ensure the receiver has opted-in to the asset
- Verify asset IDs are correct
- Check the account's spending key has signing authority

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
