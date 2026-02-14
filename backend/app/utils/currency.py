"""
Currency Utilities
Nigerian Naira (NGN) as default currency
"""

from typing import Optional, Union
from decimal import Decimal, ROUND_HALF_UP
import locale

# Currency symbols mapping
CURRENCY_SYMBOLS = {
    'NGN': '₦',
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'GHS': 'GH₵',
    'KES': 'KSh',
    'ZAR': 'R',
    'CNY': '¥',
    'JPY': '¥',
}

# Nigerian Naira formatting defaults
DEFAULT_CURRENCY = 'NGN'
DEFAULT_LOCALE = 'en_NG'


def get_currency_symbol(currency: str = DEFAULT_CURRENCY) -> str:
    """Get symbol for currency code"""
    return CURRENCY_SYMBOLS.get(currency.upper(), currency)


def format_currency(
    amount: Optional[Union[float, int, Decimal, str]],
    currency: str = DEFAULT_CURRENCY,
    include_symbol: bool = True,
    decimal_places: int = 2,
    thousands_separator: str = ',',
    decimal_separator: str = '.'
) -> str:
    """
    Format amount as currency string.
    
    Args:
        amount: The amount to format
        currency: Currency code (default: NGN)
        include_symbol: Whether to include currency symbol
        decimal_places: Number of decimal places
        thousands_separator: Thousands separator character
        decimal_separator: Decimal separator character
    
    Returns:
        Formatted currency string
    
    Examples:
        >>> format_currency(1234567.89)
        '₦1,234,567.89'
        >>> format_currency(1234567.89, 'USD')
        '$1,234,567.89'
        >>> format_currency(None)
        '-'
    """
    if amount is None:
        return '-'
    
    try:
        # Convert to Decimal for precise formatting
        if isinstance(amount, str):
            # Remove any existing formatting
            amount = amount.replace(',', '').replace('₦', '').replace('$', '').strip()
            amount = Decimal(amount)
        elif isinstance(amount, (float, int)):
            amount = Decimal(str(amount))
        elif not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        
        # Round to specified decimal places
        amount = amount.quantize(
            Decimal(10) ** -decimal_places,
            rounding=ROUND_HALF_UP
        )
        
        # Format the number
        parts = f"{abs(amount):,.{decimal_places}f}".split('.')
        integer_part = parts[0]
        decimal_part = parts[1] if len(parts) > 1 else '0' * decimal_places
        
        # Apply separators
        if thousands_separator != ',':
            integer_part = integer_part.replace(',', thousands_separator)
        if decimal_separator != '.':
            decimal_part = decimal_part.replace('.', decimal_separator)
        
        # Combine
        if decimal_places > 0:
            formatted = f"{integer_part}{decimal_separator}{decimal_part}"
        else:
            formatted = integer_part
        
        # Add negative sign if needed
        if amount < 0:
            formatted = f"-{formatted}"
        
        # Add currency symbol
        if include_symbol:
            symbol = get_currency_symbol(currency)
            if amount < 0:
                formatted = f"-{symbol}{formatted[1:]}"
            else:
                formatted = f"{symbol}{formatted}"
        
        return formatted
    
    except (ValueError, TypeError, AttributeError):
        return '-'


def parse_currency(
    value: str,
    currency: str = DEFAULT_CURRENCY
) -> Optional[Decimal]:
    """
    Parse currency string to Decimal.
    
    Args:
        value: Currency string to parse
        currency: Expected currency code
    
    Returns:
        Decimal value or None if parsing fails
    
    Examples:
        >>> parse_currency('₦1,234.56')
        Decimal('1234.56')
        >>> parse_currency('$1,234.56', 'USD')
        Decimal('1234.56')
    """
    if not value:
        return None
    
    try:
        # Remove currency symbols and whitespace
        symbols = list(CURRENCY_SYMBOLS.values()) + [currency]
        clean_value = value.strip()
        for symbol in symbols:
            clean_value = clean_value.replace(symbol, '')
        
        # Remove thousands separators
        clean_value = clean_value.replace(',', '').strip()
        
        # Parse as Decimal
        return Decimal(clean_value)
    
    except (ValueError, TypeError):
        return None


def convert_currency(
    amount: Union[float, Decimal],
    from_currency: str,
    to_currency: str,
    exchange_rate: float
) -> Decimal:
    """
    Convert amount from one currency to another.
    
    Args:
        amount: Amount to convert
        from_currency: Source currency code
        to_currency: Target currency code
        exchange_rate: Exchange rate (1 from_currency = exchange_rate to_currency)
    
    Returns:
        Converted amount as Decimal
    """
    if isinstance(amount, (float, int)):
        amount = Decimal(str(amount))
    
    return (amount * Decimal(str(exchange_rate))).quantize(
        Decimal('0.01'),
        rounding=ROUND_HALF_UP
    )


def calculate_percentage(
    amount: Union[float, Decimal],
    percentage: float,
    round_result: bool = True
) -> Decimal:
    """
    Calculate percentage of an amount.
    
    Args:
        amount: Base amount
        percentage: Percentage to calculate (e.g., 7.5 for 7.5%)
        round_result: Whether to round to 2 decimal places
    
    Returns:
        Calculated percentage as Decimal
    
    Examples:
        >>> calculate_percentage(100000, 7.5)
        Decimal('7500.00')
    """
    if isinstance(amount, (float, int)):
        amount = Decimal(str(amount))
    
    result = (amount * Decimal(str(percentage))) / Decimal('100')
    
    if round_result:
        result = result.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    return result


def format_amount_in_words(
    amount: Union[float, Decimal],
    currency: str = DEFAULT_CURRENCY
) -> str:
    """
    Convert amount to words (for Nigerian cheques/invoices).
    
    Args:
        amount: Amount to convert
        currency: Currency code
    
    Returns:
        Amount in words
    
    Examples:
        >>> format_amount_in_words(1234.56)
        'One Thousand, Two Hundred and Thirty-Four Naira, Fifty-Six Kobo'
    """
    if isinstance(amount, (float, int)):
        amount = Decimal(str(amount))
    
    # Get integer and decimal parts
    naira = int(amount)
    kobo = int((amount - naira) * 100)
    
    ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 
            'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 
            'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 
            'Nineteen']
    tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 
            'Seventy', 'Eighty', 'Ninety']
    
    def convert_less_than_thousand(n):
        if n == 0:
            return ''
        if n < 20:
            return ones[n]
        if n < 100:
            return tens[n // 10] + ('-' + ones[n % 10] if n % 10 != 0 else '')
        return ones[n // 100] + ' Hundred' + (' and ' + convert_less_than_thousand(n % 100) if n % 100 != 0 else '')
    
    def convert(n):
        if n == 0:
            return 'Zero'
        
        result = ''
        
        # Billions
        if n >= 1000000000:
            result += convert_less_than_thousand(n // 1000000000) + ' Billion'
            n %= 1000000000
            if n > 0:
                result += ', '
        
        # Millions
        if n >= 1000000:
            result += convert_less_than_thousand(n // 1000000) + ' Million'
            n %= 1000000
            if n > 0:
                result += ', '
        
        # Thousands
        if n >= 1000:
            result += convert_less_than_thousand(n // 1000) + ' Thousand'
            n %= 1000
            if n > 0:
                result += ', '
        
        # Hundreds
        if n > 0:
            result += convert_less_than_thousand(n)
        
        return result
    
    # Build the result
    words = ''
    if naira > 0:
        words += convert(naira) + ' Naira'
    elif naira == 0 and kobo == 0:
        words = 'Zero Naira'
    
    if kobo > 0:
        if naira > 0:
            words += ', '
        words += convert(kobo) + ' Kobo'
    
    return words


class Money:
    """
    Money class for currency calculations.
    Supports arithmetic operations with proper rounding.
    """
    
    def __init__(
        self,
        amount: Union[float, int, Decimal, str],
        currency: str = DEFAULT_CURRENCY
    ):
        if isinstance(amount, str):
            self.amount = Decimal(amount.replace(',', ''))
        elif isinstance(amount, (float, int)):
            self.amount = Decimal(str(amount))
        else:
            self.amount = amount
        self.currency = currency.upper()
    
    def __repr__(self):
        return f"Money({format_currency(self.amount, self.currency)})"
    
    def __str__(self):
        return format_currency(self.amount, self.currency)
    
    def __add__(self, other):
        if isinstance(other, Money):
            if other.currency != self.currency:
                raise ValueError("Cannot add different currencies")
            return Money(self.amount + other.amount, self.currency)
        return Money(self.amount + Decimal(str(other)), self.currency)
    
    def __sub__(self, other):
        if isinstance(other, Money):
            if other.currency != self.currency:
                raise ValueError("Cannot subtract different currencies")
            return Money(self.amount - other.amount, self.currency)
        return Money(self.amount - Decimal(str(other)), self.currency)
    
    def __mul__(self, other):
        return Money(self.amount * Decimal(str(other)), self.currency)
    
    def __truediv__(self, other):
        return Money(self.amount / Decimal(str(other)), self.currency)
    
    def __eq__(self, other):
        if isinstance(other, Money):
            return self.amount == other.amount and self.currency == other.currency
        return self.amount == Decimal(str(other))
    
    def __lt__(self, other):
        if isinstance(other, Money):
            return self.amount < other.amount
        return self.amount < Decimal(str(other))
    
    def __le__(self, other):
        if isinstance(other, Money):
            return self.amount <= other.amount
        return self.amount <= Decimal(str(other))
    
    def __gt__(self, other):
        if isinstance(other, Money):
            return self.amount > other.amount
        return self.amount > Decimal(str(other))
    
    def __ge__(self, other):
        if isinstance(other, Money):
            return self.amount >= other.amount
        return self.amount >= Decimal(str(other))
    
    @property
    def symbol(self) -> str:
        return get_currency_symbol(self.currency)
    
    def percentage(self, pct: float) -> 'Money':
        """Calculate percentage of this amount"""
        return Money(calculate_percentage(self.amount, pct), self.currency)
    
    def to_dict(self) -> dict:
        return {
            'amount': float(self.amount),
            'currency': self.currency,
            'formatted': str(self)
        }
