CURRENCY_SYMBOLS = {
    'USD': 'US$',
    'SGD': 'SG$',
    'CNY': 'CN¥',
    'HKD': 'HK$',
    'JPY': 'JP¥',
    'EUR': '€',
    'GBP': '£',
    'CAD': 'CA$',
    'AUD': 'A$',
    'NZD': 'NZ$',
    'CHF': 'CHF',
}

def get_currency_symbol(currency_code: str) -> str:
    return CURRENCY_SYMBOLS.get(currency_code, currency_code)

def format_currency(amount: float, currency: str) -> str:
    symbol = get_currency_symbol(currency)
    if amount < 0:
        return f"-{symbol}{abs(amount):,.2f}"
    return f"{symbol}{amount:,.2f}"

def get_currency_options():
    return [
        {'code': code, 'symbol': symbol, 'display': f"{code} ({symbol})"} 
        for code, symbol in CURRENCY_SYMBOLS.items()
    ]