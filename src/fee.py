DEFAULT_FEE_RATE = 0.001  # BGL per byte

def estimate_fee(tx_size: int, priority: str = "normal") -> float:
    rates = {"low": 0.0005, "normal": 0.001, "high": 0.002}
    rate = rates.get(priority, DEFAULT_FEE_RATE)
    return round(tx_size * rate, 8)