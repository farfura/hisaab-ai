def format_pkr(amount: float | int | None) -> str:
    if amount is None:
        return "Rs. 0"
    value = float(amount)
    if value == int(value):
        return f"Rs. {int(value):,}"
    return f"Rs. {value:,.2f}"
