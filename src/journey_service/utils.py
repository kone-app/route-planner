from datetime import datetime

def format_arrival_time(arrival_time_str: str) -> str:
    """Format arrival time into YYYYMMDDHHMMSS"""
    return datetime.fromisoformat(arrival_time_str.split("+")[0]).strftime("%Y%m%d%H%M%S")
