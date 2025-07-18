import pandas as pd
from datetime import datetime, timedelta
import re

def get_date_range_from_query(query: str) -> tuple[datetime, datetime]:
    """
    Parses a natural language query to extract a date range (start_date, end_date).
    Supports keywords like "上周" (last week), "上月" (last month), "今天" (today).
    Defaults to a reasonable range if no specific keywords are found.
    """
    today = datetime.now()
    start_date = None
    end_date = None

    query_lower = query.lower()

    if "今天" in query_lower:
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif "昨天" in query_lower:
        yesterday = today - timedelta(days=1)
        start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif "上周" in query_lower or "过去一周" in query_lower:
        # Monday of last week to Sunday of last week
        start_of_this_week = today - timedelta(days=today.weekday())
        end_of_last_week = start_of_this_week - timedelta(days=1)
        start_of_last_week = end_of_last_week - timedelta(days=6)
        start_date = start_of_last_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_of_last_week.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif "本周" in query_lower:
        start_date = today - timedelta(days=today.weekday())
        end_date = today + timedelta(days=(6 - today.weekday()))
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif "上月" in query_lower or "过去一月" in query_lower:
        # Last month
        first_day_of_this_month = today.replace(day=1)
        last_day_of_last_month = first_day_of_this_month - timedelta(days=1)
        first_day_of_last_month = last_day_of_last_month.replace(day=1)
        start_date = first_day_of_last_month.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = last_day_of_last_month.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif "本月" in query_lower:
        start_date = today.replace(day=1)
        # Calculate last day of current month
        next_month = today.replace(day=28) + timedelta(days=4)  # Go to the 4th day of next month
        end_date = next_month - timedelta(days=next_month.day) # Subtract days to get last day of current month
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        # Default to last 30 days if no specific range is found
        start_date = today - timedelta(days=30)
        end_date = today

    return start_date, end_date

def extract_date_from_query(query: str) -> datetime | None:
    """
    Extracts a specific date from a natural language query.
    Supports formats like "YYYY年MM月DD号", "YYYY-MM-DD", "MM月DD号".
    """
    # YYYY年MM月DD号
    match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})号', query)
    if match:
        return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    
    # YYYY-MM-DD
    match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', query)
    if match:
        return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))

    # MM月DD号 (assumes current year)
    match = re.search(r'(\d{1,2})月(\d{1,2})号', query)
    if match:
        return datetime(datetime.now().year, int(match.group(1)), int(match.group(2)))

    return None