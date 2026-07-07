def format_currency(value: float) -> str:
    return f"${value:,.2f}"


def format_percentage(value: float) -> str:
    return f"{value:.1f}%"