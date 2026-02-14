"""
Currency Service - Nigerian Naira (₦) Utilities
"""

from typing import Optional, Union
from decimal import Decimal, ROUND_HALF_UP
import locale


# Nigerian Naira symbol
NAIRA_SYMBOL = "₦"

# Exchange rates (approximate - should be updated from API in production)
EXCHANGE_RATES = {
    'NGN': 1.0,
    'USD': 1550.0,  # 1 USD = ~1550 NGN
    'EUR': 1680.0,  # 1 EUR = ~1680 NGN
    'GBP': 1960.0,  # 1 GBP = ~1960 NGN
}


def format_naira(
    amount: Union[float, int, Decimal, str, None],
    include_symbol: bool = True,
    decimal_places: int = 2,
    thousands_separator: str = ","
) -> str:
    """
    Format amount as Nigerian Naira
    
    Args:
        amount: The amount to format
        include_symbol: Whether to include the ₦ symbol
        decimal_places: Number of decimal places
        thousands_separator: Thousands separator character
    
    Returns:
        Formatted currency string
    """
    if amount is None:
        return "-"
    
    try:
        # Convert to float
        if isinstance(amount, str):
            amount = float(amount.replace(',', '').replace('₦', '').strip())
        elif isinstance(amount, Decimal):
            amount = float(amount)
        
        # Round to specified decimal places
        amount = round(amount, decimal_places)
        
        # Format with thousands separator
        if decimal_places > 0:
            formatted = f"{amount:,.{decimal_places}f}"
        else:
            formatted = f"{int(amount):,}"
        
        # Replace comma with custom separator
        if thousands_separator != ",":
            formatted = formatted.replace(",", thousands_separator)
        
        # Add symbol
        if include_symbol:
            formatted = f"{NAIRA_SYMBOL}{formatted}"
        
        return formatted
        
    except (ValueError, TypeError, AttributeError):
        return "-"


def parse_naira(value: str) -> float:
    """
    Parse Nigerian Naira string to float
    
    Args:
        value: String value like "₦1,234.56" or "1234.56"
    
    Returns:
        Float value
    """
    if not value:
        return 0.0
    
    # Remove currency symbol and whitespace
    cleaned = value.replace(NAIRA_SYMBOL, '').replace(',', '').strip()
    
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str = 'NGN'
) -> float:
    """
    Convert between currencies using exchange rates
    
    Args:
        amount: Amount to convert
        from_currency: Source currency code
        to_currency: Target currency code
    
    Returns:
        Converted amount
    """
    if from_currency == to_currency:
        return amount
    
    # Get rates
    from_rate = EXCHANGE_RATES.get(from_currency, 1.0)
    to_rate = EXCHANGE_RATES.get(to_currency, 1.0)
    
    # Convert to NGN first, then to target
    amount_in_ngn = amount * from_rate
    
    if to_currency == 'NGN':
        return amount_in_ngn
    
    return amount_in_ngn / to_rate


def calculate_vat(amount: float, vat_rate: float = 7.5) -> float:
    """
    Calculate Nigerian VAT (default 7.5%)
    
    Args:
        amount: Base amount
        vat_rate: VAT rate (default 7.5%)
    
    Returns:
        VAT amount
    """
    return round(amount * (vat_rate / 100), 2)


def add_vat(amount: float, vat_rate: float = 7.5) -> float:
    """
    Add VAT to amount
    
    Args:
        amount: Base amount
        vat_rate: VAT rate (default 7.5%)
    
    Returns:
        Total amount including VAT
    """
    return round(amount * (1 + vat_rate / 100), 2)


def number_to_words_naira(amount: float) -> str:
    """
    Convert number to words in Naira (for cheques, receipts)
    
    Args:
        amount: Amount in Naira
    
    Returns:
        Amount in words
    """
    ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
    teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 
             'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
    tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 
            'Sixty', 'Seventy', 'Eighty', 'Ninety']
    thousands = ['', 'Thousand', 'Million', 'Billion', 'Trillion']
    
    def convert_hundreds(n):
        result = ''
        if n >= 100:
            result += ones[int(n // 100)] + ' Hundred'
            n %= 100
            if n > 0:
                result += ' '
        
        if n >= 20:
            result += tens[int(n // 10)]
            n %= 10
            if n > 0:
                result += '-' + ones[int(n)]
        elif n >= 10:
            result += teens[int(n - 10)]
        elif n > 0:
            result += ones[int(n)]
        
        return result
    
    if amount == 0:
        return "Zero Naira"
    
    # Split into naira and kobo
    naira = int(amount)
    kobo = int(round((amount - naira) * 100))
    
    result = ''
    thousand_index = 0
    
    while naira > 0:
        chunk = naira % 1000
        if chunk > 0:
            chunk_words = convert_hundreds(chunk)
            if thousands[thousand_index]:
                chunk_words += ' ' + thousands[thousand_index]
            result = chunk_words + (' ' + result if result else result)
        naira //= 1000
        thousand_index += 1
    
    result += ' Naira'
    
    if kobo > 0:
        result += ' and ' + convert_hundreds(kobo) + ' Kobo'
    
    return result.strip()


class CurrencyService:
    """Currency conversion and formatting service"""
    
    @staticmethod
    def format(amount, currency='NGN', **kwargs):
        """Format amount in specified currency"""
        if currency == 'NGN':
            return format_naira(amount, **kwargs)
        
        symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£'
        }
        
        symbol = symbols.get(currency, currency)
        
        try:
            amount = float(amount)
            return f"{symbol}{amount:,.2f}"
        except:
            return "-"
    
    @staticmethod
    def convert(amount, from_curr, to_curr):
        """Convert currency"""
        return convert_currency(amount, from_curr, to_curr)
    
    @staticmethod
    def to_words(amount, currency='NGN'):
        """Convert amount to words"""
        if currency == 'NGN':
            return number_to_words_naira(amount)
        return str(amount)


# Singleton instance
currency_service = CurrencyService()
