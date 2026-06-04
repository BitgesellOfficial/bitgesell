# bitgesell/transaction_pool.py
def _validate_transaction(tx: Transaction) -> bool:
    """Validate transaction supports segwit (v0)"""
    if tx.version == 0 and tx.witnesses:
        return False  # Non-segwit transactions are invalid

    # Check if the transaction is a known segwit transaction
    if tx.is_segwit():
        return True  # Segwit transactions are valid

    # If not, we need to check if it's a known legacy transaction
    if tx.is_legacy():
        return False  # Legacy transactions are invalid

    # Otherwise, we assume it's a non-segwit transaction
    return False