"""
Date Utility Functions
Handles date range calculations, formatting, and fiscal year management
"""

from datetime import datetime, date, timedelta
from typing import Optional, Tuple, List
from enum import Enum


class PeriodType(str, Enum):
    TODAY = "today"
    YESTERDAY = "yesterday"
    THIS_WEEK = "this_week"
    LAST_WEEK = "last_week"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    THIS_QUARTER = "this_quarter"
    LAST_QUARTER = "last_quarter"
    THIS_YEAR = "this_year"
    LAST_YEAR = "last_year"
    CUSTOM = "custom"


def get_date_range(
    period: str = "this_month",
    custom_start: Optional[date] = None,
    custom_end: Optional[date] = None,
    fiscal_year_start_month: int = 1
) -> Tuple[date, date]:
    """
    Get start and end dates for a given period.
    
    Args:
        period: Period type (today, this_month, last_month, etc.)
        custom_start: Custom start date for custom period
        custom_end: Custom end date for custom period
        fiscal_year_start_month: Month that fiscal year starts (1=January)
    
    Returns:
        Tuple of (start_date, end_date)
    """
    today = date.today()
    
    if period == PeriodType.TODAY or period == "today":
        return today, today
    
    elif period == PeriodType.YESTERDAY or period == "yesterday":
        yesterday = today - timedelta(days=1)
        return yesterday, yesterday
    
    elif period == PeriodType.THIS_WEEK or period == "this_week":
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return start, end
    
    elif period == PeriodType.LAST_WEEK or period == "last_week":
        start = today - timedelta(days=today.weekday() + 7)
        end = start + timedelta(days=6)
        return start, end
    
    elif period == PeriodType.THIS_MONTH or period == "this_month":
        start = today.replace(day=1)
        # Get last day of month
        if today.month == 12:
            end = today.replace(day=31)
        else:
            end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        return start, end
    
    elif period == PeriodType.LAST_MONTH or period == "last_month":
        # First day of last month
        if today.month == 1:
            start = today.replace(year=today.year - 1, month=12, day=1)
        else:
            start = today.replace(month=today.month - 1, day=1)
        # Last day of last month
        end = today.replace(day=1) - timedelta(days=1)
        return start, end
    
    elif period == PeriodType.THIS_QUARTER or period == "this_quarter":
        quarter = (today.month - 1) // 3
        start_month = quarter * 3 + 1
        start = today.replace(month=start_month, day=1)
        end_month = start_month + 2
        if end_month == 12:
            end = today.replace(month=12, day=31)
        else:
            end = today.replace(month=end_month + 1, day=1) - timedelta(days=1)
        return start, end
    
    elif period == PeriodType.LAST_QUARTER or period == "last_quarter":
        quarter = (today.month - 1) // 3
        if quarter == 0:
            # Q4 of previous year
            start_month = 10
            start = today.replace(year=today.year - 1, month=start_month, day=1)
        else:
            start_month = (quarter - 1) * 3 + 1
            start = today.replace(month=start_month, day=1)
        end_month = start_month + 2
        if end_month == 12:
            end = today.replace(year=start.year, month=12, day=31)
        else:
            end = today.replace(year=start.year, month=end_month + 1, day=1) - timedelta(days=1)
        return start, end
    
    elif period == PeriodType.THIS_YEAR or period == "this_year":
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)
        return start, end
    
    elif period == PeriodType.LAST_YEAR or period == "last_year":
        start = today.replace(year=today.year - 1, month=1, day=1)
        end = today.replace(year=today.year - 1, month=12, day=31)
        return start, end
    
    elif period == PeriodType.CUSTOM or period == "custom":
        if custom_start and custom_end:
            return custom_start, custom_end
        elif custom_start:
            return custom_start, today
        else:
            return today, today
    
    else:
        # Default to this month
        start = today.replace(day=1)
        if today.month == 12:
            end = today.replace(day=31)
        else:
            end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        return start, end


def get_fiscal_year_start(
    year: Optional[int] = None,
    fiscal_year_start_month: int = 1
) -> date:
    """
    Get the start date of a fiscal year.
    
    Args:
        year: Calendar year (if fiscal year spans years)
        fiscal_year_start_month: Month that fiscal year starts
    
    Returns:
        Start date of fiscal year
    """
    if year is None:
        year = date.today().year
    
    return date(year, fiscal_year_start_month, 1)


def get_fiscal_year_end(
    year: Optional[int] = None,
    fiscal_year_start_month: int = 1
) -> date:
    """
    Get the end date of a fiscal year.
    
    Args:
        year: Calendar year (if fiscal year spans years)
        fiscal_year_start_month: Month that fiscal year starts
    
    Returns:
        End date of fiscal year
    """
    if year is None:
        year = date.today().year
    
    # Fiscal year ends one month before it starts
    end_month = fiscal_year_start_month - 1 if fiscal_year_start_month > 1 else 12
    end_year = year if fiscal_year_start_month > 1 else year - 1
    
    # Last day of the end month
    if end_month == 12:
        return date(end_year, 12, 31)
    else:
        return date(end_year, end_month + 1, 1) - timedelta(days=1)


def get_fiscal_year(
    target_date: Optional[date] = None,
    fiscal_year_start_month: int = 1
) -> Tuple[int, date, date]:
    """
    Get the fiscal year for a given date.
    
    Args:
        target_date: Date to check (default: today)
        fiscal_year_start_month: Month that fiscal year starts
    
    Returns:
        Tuple of (fiscal_year, start_date, end_date)
    """
    if target_date is None:
        target_date = date.today()
    
    # Determine which fiscal year the date belongs to
    if target_date.month >= fiscal_year_start_month:
        fiscal_year = target_date.year
    else:
        fiscal_year = target_date.year - 1
    
    start_date = get_fiscal_year_start(fiscal_year, fiscal_year_start_month)
    end_date = get_fiscal_year_end(fiscal_year, fiscal_year_start_month)
    
    return fiscal_year, start_date, end_date


def get_quarter(
    target_date: Optional[date] = None,
    quarter_start_month: int = 1
) -> Tuple[int, int, date, date]:
    """
    Get the quarter for a given date.
    
    Args:
        target_date: Date to check (default: today)
        quarter_start_month: Month that Q1 starts
    
    Returns:
        Tuple of (year, quarter_number, start_date, end_date)
    """
    if target_date is None:
        target_date = date.today()
    
    # Calculate quarter
    month = target_date.month
    quarter = ((month - quarter_start_month) % 12) // 3 + 1
    
    # Calculate start and end of quarter
    quarter_start_month_actual = ((quarter - 1) * 3 + quarter_start_month - 1) % 12 + 1
    year = target_date.year
    if quarter_start_month_actual > month:
        year -= 1
    
    start_date = date(year, quarter_start_month_actual, 1)
    
    # End date
    end_month = (quarter_start_month_actual + 2 - 1) % 12 + 1
    if end_month < quarter_start_month_actual:
        end_year = year + 1
    else:
        end_year = year
    
    if end_month == 12:
        end_date = date(end_year, 12, 31)
    else:
        end_date = date(end_year, end_month + 1, 1) - timedelta(days=1)
    
    return year, quarter, start_date, end_date


def format_date(
    date_value: Optional[date],
    format_str: str = "%d/%m/%Y"
) -> str:
    """
    Format a date as string.
    
    Args:
        date_value: Date to format
        format_str: strftime format string
    
    Returns:
        Formatted date string
    """
    if date_value is None:
        return "-"
    
    if isinstance(date_value, str):
        date_value = parse_date(date_value)
    
    if date_value is None:
        return "-"
    
    return date_value.strftime(format_str)


def format_datetime(
    datetime_value: Optional[datetime],
    format_str: str = "%d/%m/%Y %H:%M"
) -> str:
    """
    Format a datetime as string.
    
    Args:
        datetime_value: Datetime to format
        format_str: strftime format string
    
    Returns:
        Formatted datetime string
    """
    if datetime_value is None:
        return "-"
    
    if isinstance(datetime_value, str):
        datetime_value = parse_datetime(datetime_value)
    
    if datetime_value is None:
        return "-"
    
    return datetime_value.strftime(format_str)


def parse_date(date_str: str) -> Optional[date]:
    """
    Parse a string to date.
    
    Args:
        date_str: Date string in various formats
    
    Returns:
        Parsed date or None
    """
    if not date_str:
        return None
    
    # Common date formats
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%d %b %Y",
        "%d %B %Y",
        "%b %d, %Y",
        "%B %d, %Y",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    
    return None


def parse_datetime(datetime_str: str) -> Optional[datetime]:
    """
    Parse a string to datetime.
    
    Args:
        datetime_str: Datetime string in various formats
    
    Returns:
        Parsed datetime or None
    """
    if not datetime_str:
        return None
    
    # Remove timezone info for simplicity
    datetime_str = datetime_str.replace('Z', '').replace('T', ' ')
    
    # Common datetime formats
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(datetime_str.strip(), fmt)
        except ValueError:
            continue
    
    return None


def get_months_between(start_date: date, end_date: date) -> List[Tuple[int, int]]:
    """
    Get list of (year, month) tuples between two dates.
    
    Args:
        start_date: Start date
        end_date: End date
    
    Returns:
        List of (year, month) tuples
    """
    months = []
    current = start_date.replace(day=1)
    end = end_date.replace(day=1)
    
    while current <= end:
        months.append((current.year, current.month))
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    
    return months


def days_between(start_date: date, end_date: date) -> int:
    """
    Calculate number of days between two dates.
    
    Args:
        start_date: Start date
        end_date: End date
    
    Returns:
        Number of days
    """
    return (end_date - start_date).days


def is_weekend(check_date: date) -> bool:
    """
    Check if a date is a weekend.
    
    Args:
        check_date: Date to check
    
    Returns:
        True if weekend, False otherwise
    """
    return check_date.weekday() >= 5


def add_business_days(start_date: date, days: int) -> date:
    """
    Add business days to a date (skipping weekends).
    
    Args:
        start_date: Start date
        days: Number of business days to add
    
    Returns:
        Result date
    """
    current = start_date
    days_added = 0
    
    while days_added < days:
        current += timedelta(days=1)
        if not is_weekend(current):
            days_added += 1
    
    return current


def get_month_name(month: int, abbreviated: bool = False) -> str:
    """
    Get month name from month number.
    
    Args:
        month: Month number (1-12)
        abbreviated: Whether to return abbreviated name
    
    Returns:
        Month name
    """
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    months_abbr = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    
    if 1 <= month <= 12:
        return months_abbr[month - 1] if abbreviated else months[month - 1]
    return ""


def get_quarter_name(quarter: int) -> str:
    """
    Get quarter name from quarter number.
    
    Args:
        quarter: Quarter number (1-4)
    
    Returns:
        Quarter name (e.g., "Q1")
    """
    if 1 <= quarter <= 4:
        return f"Q{quarter}"
    return ""


# Nigerian public holidays (major ones)
NIGERIAN_PUBLIC_HOLIDAYS_2024 = {
    date(2024, 1, 1): "New Year's Day",
    date(2024, 4, 10): "Eid el-Fitr",
    date(2024, 4, 11): "Eid el-Fitr Holiday",
    date(2024, 5, 1): "Workers' Day",
    date(2024, 6, 12): "Democracy Day",
    date(2024, 6, 16): "Eid el-Kabir",
    date(2024, 6, 17): "Eid el-Kabir Holiday",
    date(2024, 10, 1): "Independence Day",
    date(2024, 10, 2): "Independence Day Holiday",
    date(2024, 12, 25): "Christmas Day",
    date(2024, 12, 26): "Boxing Day",
}


def get_nigerian_holidays(year: int) -> dict:
    """
    Get Nigerian public holidays for a given year.
    Note: Islamic holidays are approximate and should be verified.
    
    Args:
        year: Year to get holidays for
    
    Returns:
        Dictionary of date -> holiday name
    """
    # Fixed holidays
    holidays = {
        date(year, 1, 1): "New Year's Day",
        date(year, 5, 1): "Workers' Day",
        date(year, 6, 12): "Democracy Day",
        date(year, 10, 1): "Independence Day",
        date(year, 12, 25): "Christmas Day",
        date(year, 12, 26): "Boxing Day",
    }
    
    # Add Good Friday (2 days before Easter Sunday)
    easter = calculate_easter(year)
    holidays[easter - timedelta(days=2)] = "Good Friday"
    holidays[easter + timedelta(days=1)] = "Easter Monday"
    
    return holidays


def calculate_easter(year: int) -> date:
    """
    Calculate Easter Sunday for a given year.
    Uses the Anonymous Gregorian algorithm.
    
    Args:
        year: Year to calculate Easter for
    
    Returns:
        Easter Sunday date
    """
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    
    return date(year, month, day)
