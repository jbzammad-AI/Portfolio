# src/preprocess.py

import re

# -------------------------------
# TEXT CLEANING
# -------------------------------

def clean_text(text):
    """
    Lowercase, remove extra spaces, normalize text.
    """
    text = text.replace('\r','\n')  # normalize line breaks
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# -------------------------------
# DATE EXTRACTION
# -------------------------------

def extract_date(text):
    """
    Extract invoice date. Looks for MM/DD/YYYY or similar patterns.
    """
    match = re.search(r'\b\d{2}[/-]\d{2}[/-]\d{4}\b', text)
    if match:
        return match.group(0)
    return ""


# -------------------------------
# VENDOR EXTRACTION
# -------------------------------

def extract_vendor(text):
    """
    Extract vendor from invoice text.
    Uses 'Seller:' as anchor.
    """
    match = re.search(r'seller[:\n]\s*(.+?)(?:\n|Tax Id|Client:)', text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return "Other"


# -------------------------------
# AMOUNT EXTRACTION
# -------------------------------

def extract_amount(text):
    """
    Extract total amount from invoice text.
    Looks for keywords: Total, Gross worth, $ etc.
    """
    patterns = [
        r'total[: ]+\$?\s*([\d\s,.]+)',        # Total: $ 5 640,19
        r'gross worth[: ]+\$?\s*([\d\s,.]+)',  # Gross worth: 6 204,19
        r'\$\s*([\d\s,.]+)'                     # $ 5,640.17
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1)
            # Remove spaces and convert comma to dot if needed
            amount_str = amount_str.replace(' ', '').replace(',', '.')
            try:
                return float(amount_str)
            except:
                continue
    return 0.0


# -------------------------------
# CATEGORY EXTRACTION
# -------------------------------

def extract_category(vendor):
    """
    Assign category based on vendor or leave as Other.
    Can be extended to use ML or keyword matching.
    """
    return "Other"
