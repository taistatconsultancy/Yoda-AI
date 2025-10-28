from datetime import datetime, timezone, timedelta

# Kenya is UTC+3 (East Africa Time)
KENYA_TZ_OFFSET = timedelta(hours=3)


def utc_to_kenya_time(utc_dt):
    """Convert UTC datetime to Kenya time (UTC+3)"""
    if not utc_dt:
        return None
    
    # Ensure UTC
    if not utc_dt.tzinfo:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    else:
        utc_dt = utc_dt.astimezone(timezone.utc)
    
    # Add 3 hours for Kenya time
    return utc_dt + KENYA_TZ_OFFSET


def format_kenya_datetime(dt, format_str="%Y-%m-%d %H:%M"):
    """Format datetime in Kenya timezone"""
    if not dt:
        return None
    
    kenya_dt = utc_to_kenya_time(dt)
    return kenya_dt.strftime(format_str)
