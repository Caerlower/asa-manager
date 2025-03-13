from algosdk import mnemonic


mnemonic_phrase = "your mnemonic phrase"

derived_private_key = mnemonic.to_private_key(mnemonic_phrase)
print("Private Key Derived from Mnemonic:", derived_private_key)