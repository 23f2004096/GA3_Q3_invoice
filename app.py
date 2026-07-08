import re
from datetime import datetime

def extract_field(pattern, text, flags=re.IGNORECASE):
    match = re.search(pattern, text, flags)
    if match:
        return match.group(1).strip()
    return None

def extract_invoice_no(text):
    patterns = [
        r"(?im)^\s*Invoice\s*(?:No\.?|Number|#)\s*[:\-]?\s*([A-Z0-9\-\/]+)\s*$",
        r"(?im)^\s*Bill\s*(?:No\.?|Number|#)\s*[:\-]?\s*([A-Z0-9\-\/]+)\s*$",
        r"(?im)^\s*Receipt\s*(?:No\.?|Number|#)\s*[:\-]?\s*([A-Z0-9\-\/]+)\s*$",
        r"(?im)^\s*(?:Invoice|Bill|Receipt)\s*[:\-]?\s*([A-Z0-9\-\/]+)\s*$",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return None

def parse_money(value):
    if value is None:
        return None
    value = value.strip()
    value = re.sub(r"(?i)\b(?:rs\.?|inr)\b", "", value)
    value = value.replace(",", "").replace("₹", "").strip()
    try:
        return float(value)
    except ValueError:
        return None

def parse_date_to_iso(value):
    if value is None:
        return None
    value = value.strip()
    possible_formats = [
        "%d %B %Y",
        "%d %b %Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d.%m.%Y",
    ]
    for fmt in possible_formats:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None